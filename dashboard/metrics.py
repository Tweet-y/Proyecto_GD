import pandas as pd
import numpy as np

def _as_float(series):
    return pd.to_numeric(series, errors="coerce")

def _rolling_mean(series, window):
    numeric = _as_float(series)
    if not numeric.notna().any():
        return pd.Series(np.nan, index=series.index)
    return numeric.rolling(window=window, min_periods=1).mean()

def calculate_growth_and_rebound(df_grouped):
    """
    Calcula métricas avanzadas incluyendo tendencias de Fallecidos y Recuperados.
    """
    empty_df = pd.DataFrame(columns=['date', 'new_cases', 'new_deaths', 'new_recovered', 'new_cases_7day_avg'])
    
    if df_grouped.empty:
        return {}, empty_df

    df_grouped = df_grouped.sort_values('date')
    
    # --- 1. CÁLCULO DE DATOS DIARIOS (Nuevos Casos, Muertes, Recuperados) ---
    cols = {'confirmed': 'new_cases', 'deceased': 'new_deaths', 'recovered': 'new_recovered'}
    for c_sum, c_new in cols.items():
        values = _as_float(df_grouped[c_sum]) if c_sum in df_grouped.columns else pd.Series(np.nan, index=df_grouped.index)
        if not values.notna().any():
            df_grouped[c_new] = np.nan
            continue
        daily = values.diff().clip(lower=0)
        if values.notna().all():
            daily = daily.fillna(0)
        df_grouped[c_new] = daily

    df_grouped['new_deaths_7d'] = _rolling_mean(df_grouped['new_deaths'], 7).fillna(0)
    df_grouped['new_recovered_7d'] = _rolling_mean(df_grouped['new_recovered'], 7)

    # no calculara nada con menos de 5 datos
    if len(df_grouped) < 5:
        return {}, df_grouped

    # --- 2. CÁLCULO DE PICOS  ---
    peaks = {}
    for metric in ['new_cases', 'new_deaths', 'new_recovered']:
        if metric in df_grouped.columns and df_grouped[metric].notna().any():
            max_idx = df_grouped[metric].idxmax()
            peaks[f'{metric}_peak_date'] = df_grouped.loc[max_idx, 'date']
            peaks[f'{metric}_peak_val'] = df_grouped.loc[max_idx, metric]

    # --- 3. TENDENCIAS AVANZADAS Y BANDERAS ---
    
    # Tasa de Crecimiento
    if 'new_cases' in df_grouped.columns:
        growth = df_grouped['new_cases'].pct_change().replace([np.inf, -np.inf], 0).fillna(0)
        avg_growth = growth.rolling(window=7).mean().iloc[-1]
        
        df_grouped['new_cases_7day_avg'] = df_grouped['new_cases'].rolling(window=7).mean().fillna(0)
        diffs = df_grouped['new_cases_7day_avg'].diff().fillna(0)
        is_rebound = (diffs.iloc[-3:] > 0).all() and len(diffs) > 3
    else:
        avg_growth = 0
        is_rebound = False

    def above_baseline(series):
        average = series.mean()
        last = series.iloc[-1]
        if pd.isna(average) or pd.isna(last) or average == 0:
            return False, False
        return bool(last > average * 1.5), bool(last < average * 0.5)

    high_deaths, low_deaths = above_baseline(df_grouped['new_deaths_7d'])
    high_recovered, low_recovered = above_baseline(df_grouped['new_recovered_7d'])

    # --- 4. EMPAQUETADO FINAL ---
    insights = {
        'growth_rate': avg_growth,
        'is_rebounding': is_rebound,
        'high_deaths': high_deaths,
        'low_deaths': low_deaths,
        'high_recovered': high_recovered,
        'low_recovered': low_recovered,
        **peaks
    }
    
    return insights, df_grouped