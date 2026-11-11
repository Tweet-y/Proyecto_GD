import urllib.request
import streamlit as st
import pandas as pd

BASE_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
SERIES = (
    ("time_series_covid19_confirmed_global.csv", "confirmed"),
    ("time_series_covid19_deaths_global.csv", "deceased"),
    ("time_series_covid19_recovered_global.csv", "recovered"),
)

def fetch_and_melt(filename, value_name):
    """Descarga una serie global de JHU y la deja en formato país-fecha."""
    url = f"{BASE_URL}{filename}"
    with urllib.request.urlopen(url, timeout=60) as response:
        frame = pd.read_csv(response)
    required = {"Country/Region", "Province/State", "Lat", "Long"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"faltan columnas {sorted(missing)}")
    frame = frame.drop(columns=["Lat", "Long", "Province/State"])
    frame = frame.groupby("Country/Region", as_index=False).sum(numeric_only=True)
    melted = frame.melt(id_vars=["Country/Region"], var_name="date", value_name=value_name)
    melted["date"] = pd.to_datetime(melted["date"], format="%m/%d/%y")
    return melted

def mask_unreported_recovered(frame):
    """Los ceros posteriores al último recuperado real son ausencia de reporte, no altas."""
    recovered = frame["recovered"]
    positive = recovered.gt(0).eq(True)
    last_positive = frame.loc[positive].groupby("country")["date"].max()
    last_date = frame["country"].map(last_positive)
    ever_confirmed = frame.groupby("country")["confirmed"].transform("max") > 0
    never_reported = last_date.isna() & ever_confirmed
    stopped_reporting = last_date.notna() & (frame["date"] > last_date)
    frame.loc[never_reported | stopped_reporting, "recovered"] = pd.NA
    return frame

# caché para velocidad
@st.cache_data(ttl=3600)
def load_data_simple():
    """
    Carga confirmados, fallecidos y recuperados. Si una serie falla, las otras siguen.
    Devuelve el DataFrame y advertencias para mostrar en la interfaz.
    """
    loaded = {}
    warnings = []
    for filename, value_name in SERIES:
        try:
            loaded[value_name] = fetch_and_melt(filename, value_name)
        except Exception as exc:
            loaded[value_name] = None
            warnings.append(f"No se pudo cargar {filename}: {exc}")

    if loaded["confirmed"] is None:
        return pd.DataFrame(), tuple(warnings)

    df_final = loaded["confirmed"]
    if loaded["deceased"] is None:
        df_final["deceased"] = pd.NA
    else:
        df_final = pd.merge(df_final, loaded["deceased"], on=["Country/Region", "date"], how="left")

    if loaded["recovered"] is None:
        df_final["recovered"] = pd.NA
    else:
        df_final = pd.merge(df_final, loaded["recovered"], on=["Country/Region", "date"], how="left")

    df_final.rename(columns={"Country/Region": "country"}, inplace=True)
    df_final["deceased"] = df_final["deceased"].fillna(0)
    df_final = mask_unreported_recovered(df_final)
    # Activos solo cuando hay recuperados reportados. Un cero posterior al corte no es un alta.
    df_final["active"] = (df_final["confirmed"] - df_final["deceased"] - df_final["recovered"]).clip(lower=0)

    # 5. Mapeo Completo de Continentes
    continent_map = {
        # North America
        'US': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
        'Antigua and Barbuda': 'North America', 'Bahamas': 'North America', 'Barbados': 'North America',
        'Belize': 'North America', 'Costa Rica': 'North America', 'Cuba': 'North America',
        'Dominica': 'North America', 'Dominican Republic': 'North America', 'El Salvador': 'North America',
        'Grenada': 'North America', 'Guatemala': 'North America', 'Haiti': 'North America',
        'Honduras': 'North America', 'Jamaica': 'North America', 'Nicaragua': 'North America',
        'Panama': 'North America', 'Saint Kitts and Nevis': 'North America', 'Saint Lucia': 'North America',
        'Saint Vincent and the Grenadines': 'North America', 'Trinidad and Tobago': 'North America',
        
        # South America
        'Argentina': 'South America', 'Bolivia': 'South America', 'Brazil': 'South America',
        'Chile': 'South America', 'Colombia': 'South America', 'Ecuador': 'South America',
        'Guyana': 'South America', 'Paraguay': 'South America', 'Peru': 'South America',
        'Suriname': 'South America', 'Uruguay': 'South America', 'Venezuela': 'South America',
        
        # Europe
        'Albania': 'Europe', 'Andorra': 'Europe', 'Armenia': 'Europe', 'Austria': 'Europe',
        'Azerbaijan': 'Europe', 'Belarus': 'Europe', 'Belgium': 'Europe', 'Bosnia and Herzegovina': 'Europe',
        'Bulgaria': 'Europe', 'Croatia': 'Europe', 'Cyprus': 'Europe', 'Czechia': 'Europe',
        'Denmark': 'Europe', 'Estonia': 'Europe', 'Finland': 'Europe', 'France': 'Europe',
        'Georgia': 'Europe', 'Germany': 'Europe', 'Greece': 'Europe', 'Hungary': 'Europe',
        'Iceland': 'Europe', 'Ireland': 'Europe', 'Italy': 'Europe', 'Kazakhstan': 'Europe',
        'Kosovo': 'Europe', 'Latvia': 'Europe', 'Liechtenstein': 'Europe', 'Lithuania': 'Europe',
        'Luxembourg': 'Europe', 'Malta': 'Europe', 'Moldova': 'Europe', 'Monaco': 'Europe',
        'Montenegro': 'Europe', 'Netherlands': 'Europe', 'North Macedonia': 'Europe', 'Norway': 'Europe',
        'Poland': 'Europe', 'Portugal': 'Europe', 'Romania': 'Europe', 'Russia': 'Europe',
        'San Marino': 'Europe', 'Serbia': 'Europe', 'Slovakia': 'Europe', 'Slovenia': 'Europe',
        'Spain': 'Europe', 'Sweden': 'Europe', 'Switzerland': 'Europe', 'Turkey': 'Europe',
        'Ukraine': 'Europe', 'United Kingdom': 'Europe', 'Holy See': 'Europe',
        
        # Asia
        'Afghanistan': 'Asia', 'Bahrain': 'Asia', 'Bangladesh': 'Asia', 'Bhutan': 'Asia',
        'Brunei': 'Asia', 'Burma': 'Asia', 'Cambodia': 'Asia', 'China': 'Asia',
        'East Timor': 'Asia', 'India': 'Asia', 'Indonesia': 'Asia', 'Iran': 'Asia',
        'Iraq': 'Asia', 'Israel': 'Asia', 'Japan': 'Asia', 'Jordan': 'Asia',
        'Korea, North': 'Asia', 'Korea, South': 'Asia', 'Kuwait': 'Asia', 'Kyrgyzstan': 'Asia',
        'Laos': 'Asia', 'Lebanon': 'Asia', 'Malaysia': 'Asia', 'Maldives': 'Asia',
        'Mongolia': 'Asia', 'Nepal': 'Asia', 'Oman': 'Asia', 'Pakistan': 'Asia',
        'Philippines': 'Asia', 'Qatar': 'Asia', 'Saudi Arabia': 'Asia', 'Singapore': 'Asia',
        'Sri Lanka': 'Asia', 'Syria': 'Asia', 'Taiwan*': 'Asia', 'Tajikistan': 'Asia',
        'Thailand': 'Asia', 'Timor-Leste': 'Asia', 'United Arab Emirates': 'Asia', 'Uzbekistan': 'Asia',
        'Vietnam': 'Asia', 'Yemen': 'Asia',
        
        # Africa
        'Algeria': 'Africa', 'Angola': 'Africa', 'Benin': 'Africa', 'Botswana': 'Africa',
        'Burkina Faso': 'Africa', 'Burundi': 'Africa', 'Cabo Verde': 'Africa', 'Cameroon': 'Africa',
        'Central African Republic': 'Africa', 'Chad': 'Africa', 'Comoros': 'Africa',
        'Congo (Brazzaville)': 'Africa', 'Congo (Kinshasa)': 'Africa', 'Cote d\'Ivoire': 'Africa',
        'Djibouti': 'Africa', 'Egypt': 'Africa', 'Equatorial Guinea': 'Africa', 'Eritrea': 'Africa',
        'Eswatini': 'Africa', 'Ethiopia': 'Africa', 'Gabon': 'Africa', 'Gambia': 'Africa',
        'Ghana': 'Africa', 'Guinea': 'Africa', 'Guinea-Bissau': 'Africa', 'Kenya': 'Africa',
        'Lesotho': 'Africa', 'Liberia': 'Africa', 'Libya': 'Africa', 'Madagascar': 'Africa',
        'Malawi': 'Africa', 'Mali': 'Africa', 'Mauritania': 'Africa', 'Mauritius': 'Africa',
        'Morocco': 'Africa', 'Mozambique': 'Africa', 'Namibia': 'Africa', 'Niger': 'Africa',
        'Nigeria': 'Africa', 'Rwanda': 'Africa', 'Sao Tome and Principe': 'Africa', 'Senegal': 'Africa',
        'Seychelles': 'Africa', 'Sierra Leone': 'Africa', 'Somalia': 'Africa', 'South Africa': 'Africa',
        'South Sudan': 'Africa', 'Sudan': 'Africa', 'Tanzania': 'Africa', 'Togo': 'Africa',
        'Tunisia': 'Africa', 'Uganda': 'Africa', 'Zambia': 'Africa', 'Zimbabwe': 'Africa',
        
        # Oceania
        'Australia': 'Oceania', 'Fiji': 'Oceania', 'Kiribati': 'Oceania', 'Marshall Islands': 'Oceania',
        'Micronesia': 'Oceania', 'New Zealand': 'Oceania', 'Palau': 'Oceania', 'Papua New Guinea': 'Oceania',
        'Samoa': 'Oceania', 'Solomon Islands': 'Oceania', 'Tonga': 'Oceania', 'Vanuatu': 'Oceania',
        'Nauru': 'Oceania', 'Tuvalu': 'Oceania',
        'West Bank and Gaza': 'Asia',
    }
    
    def get_continent(country):
        return continent_map.get(country, 'Other')

    df_final['continent'] = df_final['country'].apply(get_continent)

    return df_final, tuple(warnings)