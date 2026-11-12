import streamlit as st
import pandas as pd
import plotly.express as px
from data import load_data_simple
from metrics import calculate_growth_and_rebound
import ui

HELP = {
    "dates": "La fecha final no puede ser anterior a la inicial. La fuente cubre del 22 de enero de 2020 al 9 de marzo de 2023.",
    "continents": "Si eliges uno o más, países y totales se restringen a esos continentes. Vacío incluye todos. Other agrupa cruceros, olimpiadas y Antártida.",
    "countries": "Vacío usa todos los países del filtro de continente. Si eliges países, el total es solo la suma de esos países.",
    "confirmed": "Casos acumulados al último día del rango, sumados desde la serie global de Johns Hopkins.",
    "active": "Confirmados menos fallecidos menos recuperados, solo en países que publicaron altas ese día. Si ninguno lo hizo, se muestra Sin reporte en lugar de un cero falso.",
    "recovered": "Altas acumuladas de los países que sí publicaron la serie ese día. Johns Hopkins la cerró el 4 de agosto de 2021. Estados Unidos dejó de reportarla en diciembre de 2020 y Suecia no la reportó.",
    "deceased": "Fallecidos acumulados al último día del rango.",
    "peak": "Día con más casos nuevos dentro del rango. El caso nuevo es la diferencia del acumulado respecto del día anterior.",
    "trend": "Promedio de la variación diaria de casos nuevos en los últimos 7 días. ALZA significa que esa media móvil subió cada uno de los últimos 3 días.",
    "rebound": "Hay rebrote cuando la media móvil de 7 días de casos nuevos aumenta en los tres últimos días del rango.",
    "evolution": "Acumulados del rango filtrado. Activos se interrumpe cuando Johns Hopkins no reportó recuperados.",
    "daily": "Diferencia diaria de confirmados. Un ajuste a la baja del acumulado no se dibuja como caso negativo.",
    "search": "Filtra la tabla por el nombre del país, tal como lo publica Johns Hopkins. Por ejemplo, US o Korea, South.",
    "sort": "Ordena toda la tabla. Los valores vacíos de recuperados o activos quedan al final cuando ordenas esas columnas.",
}

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="COVID Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# 1. Inicializar Estado de Navegación
query_params = st.query_params
current_page = query_params.get("page", "dashboard")

# 2. Estilos y Sidebar
ui.setup_page_style()
ui.render_sidebar()

# 3. Carga de Datos Global
with st.spinner('Cargando series de Johns Hopkins...'):
    df_full, load_warnings = load_data_simple()

if df_full.empty:
    st.error("No se pudo cargar la serie de casos confirmados. Revisa la conexión con GitHub.")
    for message in load_warnings:
        st.error(message)
    st.stop()

for message in load_warnings:
    ui.notice(message)

# --- CONTROLADOR DE VISTAS ---

if current_page == "dashboard":
    # ==========================================
    # VISTA 1: DASHBOARD
    # ==========================================
    
    ui.render_top_banner(title="Tendencias epidemiológicas")
    
    # Filtros Dashboard
    with st.container():
        c1, c2, c3 = st.columns([1, 1, 2], gap="small")
        
        # Filtro de Rango de Fechas
        with c1:
            min_d, max_d = df_full['date'].min().date(), df_full['date'].max().date()
            if "range_start" not in st.session_state:
                st.session_state.range_start = min_d
            if "range_end" not in st.session_state:
                st.session_state.range_end = max_d
            st.session_state.range_start = min(max(st.session_state.range_start, min_d), max_d)
            st.session_state.range_end = min(max(st.session_state.range_end, st.session_state.range_start), max_d)
            ui.field_label("Desde", HELP["dates"])
            start_date = st.date_input("Desde", min_value=min_d, max_value=max_d, key="range_start", label_visibility="collapsed")
            if st.session_state.range_end < start_date:
                st.session_state.range_end = start_date
            ui.field_label("Hasta", "Tiene que ser igual o posterior a la fecha inicial.")
            end_date = st.date_input("Hasta", min_value=start_date, max_value=max_d, key="range_end", label_visibility="collapsed")
            start, end = pd.to_datetime(start_date), pd.to_datetime(end_date)
        
        with c2:
            ui.field_label("Continentes", HELP["continents"])
            avail_continents = sorted(df_full['continent'].unique())
            sel_continents = st.multiselect("Continentes", options=avail_continents, default=[], label_visibility="collapsed")
        
        with c3:
            ui.field_label("Países", HELP["countries"])
            if sel_continents:
                filtered_countries = df_full[df_full['continent'].isin(sel_continents)]['country'].unique()
            else:
                filtered_countries = df_full['country'].unique()
            avail_countries = sorted(filtered_countries)
            sel_countries = st.multiselect("Países", options=avail_countries, default=[], label_visibility="collapsed")

    # --- Lógica de Filtrado ---
    
    # País/Continente
    if sel_countries:
        country_mask = df_full['country'].isin(sel_countries)
    elif sel_continents:
        country_mask = df_full['continent'].isin(sel_continents)
    else:
        # Si no hay filtros de ubicación, selecciona todos los datos 
        country_mask = pd.Series(True, index=df_full.index)

    # Máscara de Fecha
    date_mask = (df_full['date'] >= start) & (df_full['date'] <= end)
    
    # Aplicar Filtros
    mask = date_mask & country_mask
    df_filtered = df_full[mask]

    # Validación 
    if df_filtered.empty:
        st.warning("No hay datos disponibles para la combinación de filtros seleccionada.")
        st.stop()

    # --- Cálculos y Renderizado ---
    timeline = df_filtered.groupby("date", as_index=False)[["confirmed", "deceased"]].sum()
    reported_rows = df_filtered[df_filtered["recovered"].notna()]
    country_count = df_filtered.groupby("date")["country"].nunique()
    timeline["selected_countries"] = timeline["date"].map(country_count)
    if reported_rows.empty:
        timeline["recovered"] = pd.NA
        timeline["active"] = pd.NA
        timeline["recovered_countries"] = 0
    else:
        totals = reported_rows.groupby("date", as_index=False).agg(
            recovered=("recovered", "sum"),
            active=("active", "sum"),
            recovered_countries=("country", "nunique"),
        )
        timeline = timeline.merge(totals, on="date", how="left")
        timeline["recovered_countries"] = timeline["recovered_countries"].fillna(0)

    insights, timeline_metrics = calculate_growth_and_rebound(timeline)
    last_day = timeline.iloc[-1]
    covered = int(last_day["recovered_countries"])
    selected = int(last_day["selected_countries"])
    if covered == 0:
        ui.notice("Sin altas publicadas en la fecha final del rango.")
    elif covered < selected:
        ui.notice(f"Altas del último día: {covered} de {selected} países.")

    def format_count(value):
        if pd.isna(value):
            return "Sin reporte"
        return f"{value:,.0f}"

    # Iconos SVG 
    icon_users = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />'
    icon_chart = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />'
    icon_check = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
    icon_alert = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />'
    icon_trend_up = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />'
    icon_trend_flat = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14" />'

    # FILA 1: MÉTRICAS
    st.markdown("<div class='mb-6'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4, gap="large")
    if covered == 0:
        recovered_subtitle = "Sin publicación"
    elif covered < selected:
        recovered_subtitle = f"{covered} de {selected} países"
    else:
        recovered_subtitle = "Altas acumuladas"
    with k1: ui.metric_card("Confirmados", format_count(last_day["confirmed"]), "Total acumulado", icon_users, "purple", HELP["confirmed"])
    with k2: ui.metric_card("Activos", format_count(last_day["active"]), recovered_subtitle, icon_chart, "blue", HELP["active"])
    with k3: ui.metric_card("Recuperados", format_count(last_day["recovered"]), recovered_subtitle, icon_check, "green", HELP["recovered"])
    with k4: ui.metric_card("Fallecidos", format_count(last_day["deceased"]), "Total acumulado", icon_alert, "red", HELP["deceased"])

    # FILA 2: INSIGHTS Y ALERTA
    st.markdown("<div class='mb-6'></div>", unsafe_allow_html=True)
    i1, i2, i3 = st.columns([1, 1, 2], gap="large")
    
    peak_val = insights.get("new_cases_peak_val")
    peak_date = insights.get("new_cases_peak_date")
    is_rebound = insights.get("is_rebounding", False)
    growth = insights.get("growth_rate")
    peak_subtitle = peak_date.strftime("%d-%m-%Y") if peak_date is not None and pd.notna(peak_date) else "Casos nuevos"

    with i1: ui.metric_card("Punto máximo", format_count(peak_val), peak_subtitle, icon_alert, "yellow", HELP["peak"])
    with i2:
        has_trend = growth is not None and pd.notna(growth) and insights
        trend_icon = icon_trend_up if has_trend and growth > 0 else icon_trend_flat
        trend_color = "red" if is_rebound else "green"
        trend_text = "▲ ALZA" if is_rebound else ("▼ ESTABLE" if has_trend else "Sin dato")
        growth_label = f"{growth:.1%} (7d)" if has_trend else "Menos de 5 días"
        ui.metric_card("Tendencia", trend_text, growth_label, trend_icon, trend_color, HELP["trend"])
    with i3:
        ui.alert_card(bool(is_rebound) if insights else False, HELP["rebound"])

    # FILA 3: GRÁFICOS
    st.markdown("<div class='mb-6'></div>", unsafe_allow_html=True)
    g1, g2 = st.columns(2, gap="large")

    with g1:
        labels = {"confirmed": "Confirmados", "active": "Activos", "deceased": "Fallecidos"}
        plot_frame = timeline.rename(columns=labels)
        series = ["Confirmados", "Fallecidos"]
        if plot_frame["Activos"].notna().any():
            series.insert(1, "Activos")
        fig = px.line(
            plot_frame,
            x="date",
            y=series,
            color_discrete_map={"Confirmados": "#7c3aed", "Activos": "#60a5fa", "Fallecidos": "#f87171"},
        )
        ui.render_chart_card("Curva de evolución temporal", fig, help_text=HELP["evolution"])

    with g2:
        fig_bar = px.bar(
            timeline_metrics,
            x="date",
            y="new_cases",
            labels={"date": "Fecha", "new_cases": "Casos nuevos"},
        )
        fig_bar.update_traces(marker_color="#8b5cf6")
        ui.render_chart_card("Nuevos casos diarios", fig_bar, help_text=HELP["daily"])

elif current_page == "table":
    # ==========================================
    # VISTA 2: TABLA DE DATOS
    # ==========================================
    
    ui.render_top_banner(title="Registro de datos")
    
    with st.container():
        t1, t2 = st.columns(2)
        with t1:
            ui.field_label("Buscar país", HELP["search"])
            search_country = st.text_input("Buscar país", placeholder="Escribe para filtrar...", label_visibility="collapsed")
        with t2:
            ui.field_label("Ordenar por", HELP["sort"])
            sort_labels = {
                "Fecha": "date",
                "Confirmados acumulados": "confirmed",
                "Activos": "active",
                "Fallecidos acumulados": "deceased",
                "Recuperados acumulados": "recovered",
            }
            sort_choice = st.selectbox("Ordenar por", list(sort_labels), index=0, label_visibility="collapsed")
            sort_by = sort_labels[sort_choice]
    
    df_table = df_full.copy()
    if search_country:
        df_table = df_table[df_table['country'].str.contains(search_country, case=False, na=False)]
    df_table = df_table.sort_values(by=sort_by, ascending=False, na_position="last")
    df_table["date"] = df_table["date"].dt.strftime("%Y-%m-%d")
    df_table[["recovered", "active"]] = df_table[["recovered", "active"]].astype(float)
    df_table = df_table.rename(columns={
        "date": "Fecha",
        "country": "País",
        "continent": "Continente",
        "confirmed": "Confirmados acumulados",
        "deceased": "Fallecidos acumulados",
        "recovered": "Recuperados acumulados",
        "active": "Activos",
    })
    
    st.markdown("<div class='mb-4'></div>", unsafe_allow_html=True)
    ui.help_row([
        ("Fecha", "Día del reporte en la serie temporal de Johns Hopkins."),
        ("País", "Nombre del país o territorio tal como lo publica la fuente."),
        ("Continente", "Asignación usada por los filtros. Other no es un continente geográfico."),
        ("Confirmados acumulados", HELP["confirmed"]),
        ("Activos", HELP["active"]),
        ("Recuperados acumulados", HELP["recovered"]),
        ("Fallecidos acumulados", HELP["deceased"]),
    ])
    st.markdown(f"""<div class="bg-white shadow-sm rounded-xl border border-gray-100 p-6"><h3 class="font-bold text-lg text-gray-800 mb-4">Registros detallados ({len(df_table):,.0f} filas)</h3></div>""", unsafe_allow_html=True)
    st.dataframe(df_table, width="stretch", hide_index=True, height=600)