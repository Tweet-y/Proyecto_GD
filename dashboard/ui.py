import html
import streamlit as st

# --- CONSTANTES DE COLOR ---
BG_COLOR = "#f3f4f6"   
CARD_COLOR = "#ffffff" 
TEXT_COLOR = "#1f2937" 

def setup_page_style():
    """Inyecta CSS y Tailwind."""
    st.markdown('<script src="https://cdn.tailwindcss.com"></script>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <style>
        html, body, [class*="css"] {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        }}
        .stApp {{
            background-color: {BG_COLOR};
            color: {TEXT_COLOR};
        }}
        
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stMainMenu"],
        [data-testid="stAppDeployButton"],
        .stAppDeployButton,
        .stDeployButton {{
            display: none !important;
        }}
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        [data-testid="stExpandSidebarButton"] {{
            visibility: visible !important;
            background: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 0.5rem !important;
            color: #1f2937 !important;
        }}
        
        /* Ajuste del contenido principal para el sidebar de 5rem */
        .block-container {{
            padding-left: 6rem !important; /* 5rem sidebar + 1rem espacio */
            padding-top: 1rem !important;
            padding-right: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 100%;
        }}
        
        /* Ocultar botones originales de Streamlit para que no se vean dobles */
        div[data-testid="stSidebarContent"] .stButton button {{
            visibility: hidden;
            height: 0;
            padding: 0;
            margin: 0;
            width: 0;
        }}

        /* Estilos de inputs, tags y columns (Mantenidos) */
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] {{
            background-color: white !important;
            border: 1px solid #e5e7eb !important;
            color: {TEXT_COLOR} !important;
            border-radius: 0.5rem;
        }}
        div[data-baseweb="select"] span {{ color: {TEXT_COLOR} !important; }}
        span[data-baseweb="tag"] {{ background-color: #ef4444 !important; }}
        span[data-baseweb="tag"] span {{ color: white !important; }}
        span[data-baseweb="tag"] svg {{ fill: white !important; color: white !important; }}
        
        div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] {{
            gap: 1rem !important;
        }}

        /* --- SIDEBAR MODIFICADO (Contenedor principal) --- */
        [data-testid="stDateInputField"],
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }}
        [data-testid="stDateInputField"] span,
        [data-testid="stDateInputField"] input {{
            color: #1f2937 !important;
            -webkit-text-fill-color: #1f2937 !important;
        }}

        [data-testid="stSidebarContent"] {{
            overflow: visible !important;
        }}

        section[data-testid="stSidebar"][aria-expanded="true"] {{
            width: 5.75rem !important;
            min-width: 5.75rem !important;
            max-width: 5.75rem !important;
            background-color: #1f2937;
            padding-top: 0.5rem;
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }}
        
        /* --- ESTILO DE BOTONES HTML --- */
        .sidebar-btn-container {{
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            padding-top: 1rem;
        }}
        .sidebar-item {{
            position: relative;
            width: 4.4rem;
            min-height: 4.4rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.2rem;
            padding: 0.45rem 0.2rem;
            background-color: white;
            border-radius: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .sidebar-caption {{
            color: #374151;
            font-size: 0.62rem;
            font-weight: 600;
            line-height: 1.15;
            text-align: center;
        }}
        .sidebar-help {{
            display: none;
            position: absolute;
            left: calc(100% + 0.6rem);
            top: 0.35rem;
            width: 11rem;
            padding: 0.45rem 0.6rem;
            background: #111827;
            color: #f9fafb;
            border-radius: 0.45rem;
            font-size: 0.72rem;
            font-weight: 500;
            line-height: 1.35;
            text-align: left;
            z-index: 100000;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
        }}
        .sidebar-item:hover .sidebar-help,
        .sidebar-item:focus-within .sidebar-help {{
            display: block;
        }}
        .sidebar-item:hover {{
            background-color: #f3f4f6;
            transform: scale(1.05);
        }}
        .sidebar-item svg {{
            stroke: #7c3aed; /* Color del icono */
            stroke-width: 2;
            fill: none;
            width: 1.5rem;
            height: 1.5rem;
        }}
        
        /* Estilo para los enlaces de navegación */
        .sidebar-btn-container a {{
            text-decoration: none; /* Quitar subrayado por defecto del enlace */
        }}

        [data-testid="stMarkdown"],
        [data-testid="stMarkdownContainer"],
        [data-testid="column"],
        [data-testid="stVerticalBlock"] {{
            overflow: visible !important;
        }}

        .field-label {{
            font-size: 0.875rem;
            font-weight: 600;
            color: #374151;
            margin: 0 0 0.35rem 0;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}
        .info-tip {{
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.05rem;
            height: 1.05rem;
            border-radius: 999px;
            background: #eef2ff;
            color: #4338ca;
            border: 1px solid #c7d2fe;
            font-size: 0.68rem;
            font-weight: 700;
            font-family: Georgia, "Times New Roman", serif;
            text-transform: none;
            cursor: help;
            flex-shrink: 0;
            line-height: 1;
        }}
        .info-tip .info-tip-box {{
            display: none;
            position: absolute;
            left: 50%;
            top: calc(100% + 8px);
            transform: translateX(-50%);
            width: max-content;
            max-width: 280px;
            padding: 0.55rem 0.7rem;
            background: #111827;
            color: #f9fafb;
            border-radius: 0.5rem;
            font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 0.75rem;
            font-weight: 500;
            font-style: normal;
            line-height: 1.4;
            letter-spacing: 0;
            text-transform: none;
            text-align: left;
            white-space: normal;
            z-index: 10000;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
        }}
        .info-tip:hover .info-tip-box,
        .info-tip:focus .info-tip-box,
        .info-tip:focus-within .info-tip-box {{
            display: block;
        }}
        .data-notice {{
            margin: 0 0 0.65rem 0;
            padding: 0;
            color: #6b7280;
            background: transparent;
            border: none;
            font-size: 0.78rem;
            line-height: 1.35;
        }}
        .page-title {{
            margin: 0 0 0.85rem 0;
            padding-bottom: 0.35rem;
            border-bottom: 2px solid #7c3aed;
        }}
        .page-title h2 {{
            margin: 0;
            color: #1f2937;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            line-height: 1.3;
        }}
        .chart-heading {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            margin: 0 0 0.25rem 0;
            color: #1f2937;
            font-size: 1rem;
            font-weight: 600;
        }}
        .help-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 1rem;
            margin: 0 0 0.75rem 0;
            color: #4b5563;
            font-size: 0.8rem;
        }}
        .help-row > span {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }}
    </style>
    """, unsafe_allow_html=True)

def info_badge(help_text, floating=True):
    """Icono «i». El recuadro aparece al pasar el mouse; title cubre el mismo texto."""
    safe = html.escape(help_text, quote=True)
    box = f'<span class="info-tip-box" role="tooltip">{safe}</span>' if floating else ""
    return (
        f'<span class="info-tip" tabindex="0" title="{safe}" aria-label="{safe}">i{box}</span>'
    )

def field_label(label, help_text):
    st.markdown(
        f'<p class="field-label">{html.escape(label)}{info_badge(help_text)}</p>',
        unsafe_allow_html=True,
    )

def notice(text):
    st.markdown(f'<p class="data-notice">{html.escape(text)}</p>', unsafe_allow_html=True)

def help_row(items):
    chips = "".join(
        f"<span>{html.escape(label)}{info_badge(description)}</span>"
        for label, description in items
    )
    st.markdown(f'<div class="help-row">{chips}</div>', unsafe_allow_html=True)

def render_sidebar():
    """
    Renderiza el Sidebar usando HTML para el diseño y ENLACES HTML (QUERY PARAMS) para la funcionalidad.
    """
    
    icon_dashboard = '<svg viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>'
    icon_table = '<svg viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>'
    
    with st.sidebar:
        # Espacio superior
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        
        # --- Renderizado de HTML ---
        
        html_content = f"""
        <div class="sidebar-btn-container">
            <a href="?page=dashboard" target="_self" title="Indicadores, filtros y gráficos del rango elegido.">
                 <div class="sidebar-item">
                    {icon_dashboard}
                    <span class="sidebar-caption">Panel</span>
                    <span class="sidebar-help">Indicadores, filtros y gráficos del rango elegido.</span>
                 </div>
            </a>
            <a href="?page=table" target="_self" title="Tabla con cada país y cada fecha de la serie.">
                 <div class="sidebar-item">
                    {icon_table}
                    <span class="sidebar-caption">Registros</span>
                    <span class="sidebar-help">Tabla con cada país y cada fecha de la serie.</span>
                 </div>
            </a>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)


def render_header(title="Dashboard", subtitle="COVID-19 Global Tracking"):
    header_html = f"""
    <header class="flex items-center justify-between h-20 px-6 bg-white border-b border-gray-200 mb-8 rounded-xl shadow-sm" style="background-color:white; border-radius:0.75rem; margin-bottom:2rem; padding:0 1.5rem; display:flex; align-items:center; justify-content:space-between;">
        <div class="flex flex-col">
            <h1 class="text-2xl font-bold text-gray-800 m-0" style="color:#1f2937; font-size:1.5rem; font-weight:700; margin:0;">{title}</h1>
            <span class="text-sm text-gray-500" style="color:#6b7280; font-size:0.875rem;">{subtitle}</span>
        </div>
        <div class="flex items-center space-x-4">
            <div class="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold border border-purple-200" style="background-color:#f3e8ff; color:#7c3aed; display:flex; align-items:center; justify-content:center;">
                AU
            </div>
        </div>
    </header>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def metric_card(title, value, subtitle, icon_path, color_theme="purple", help_text=""):
    colors = {
        "purple": ("#f3e8ff", "#7c3aed"),
        "green": ("#dcfce7", "#16a34a"),
        "red": ("#fee2e2", "#dc2626"),
        "blue": ("#dbeafe", "#2563eb"),
        "yellow": ("#fef9c3", "#ca8a04"),
    }
    bg_hex, text_hex = colors.get(color_theme, colors["purple"])
    
    html = f"""
    <div style="background-color:white; padding:1.5rem; border-radius:0.75rem; display:flex; align-items:center; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); border:1px solid #e5e7eb; height:100%;">
        <div style="background-color:{bg_hex}; color:{text_hex}; height:4rem; width:4rem; border-radius:9999px; margin-right:1rem; display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;">
            <svg aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="height:2rem; width:2rem;">
                {icon_path}
            </svg>
        </div>
        <div style="flex-grow: 1; min-width: 0;">
            <span style="display:block; font-size:1.5rem; font-weight:700; color:#1f2937; line-height:1.2;">{value}</span>
            <span style="display:flex; align-items:center; gap:0.35rem; font-size:0.75rem; font-weight:600; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em;">{title}{info_badge(help_text) if help_text else ""}</span>
            <span style="display:block; font-size:0.75rem; color:#9ca3af; margin-top:0.25rem;">{subtitle}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_chart_card(title, fig, height=340, help_text=""):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=36, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        xaxis_title=None,
        yaxis_title=None,
    )
    with st.container(border=True):
        st.markdown(
            f'<div class="chart-heading"><span>{html.escape(title)}</span>{info_badge(help_text) if help_text else ""}</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, width="stretch", theme="streamlit", config={"displayModeBar": False})

def alert_card(is_rebounding, help_text=""):
    bg_hex = "#fee2e2" if is_rebounding else "#dcfce7"
    text_hex = "#dc2626" if is_rebounding else "#16a34a"
    title = "Alerta de rebrote" if is_rebounding else "Tendencia estable"
    desc = "La media móvil de 7 días subió en los últimos 3 días." if is_rebounding else "La media móvil de 7 días no acumula tres alzas al cierre del rango."

    card_html = f"""
    <div style="background-color:{bg_hex}; border:1px solid {text_hex}; border-radius:0.75rem; padding:1rem 1.15rem; display:flex; align-items:center; height:100%;">
        <div>
            <h4 style="margin:0 0 0.25rem 0; color:{text_hex}; font-weight:650; font-size:0.95rem; display:flex; align-items:center; gap:0.4rem;">{title}{info_badge(help_text) if help_text else ""}</h4>
            <p style="margin:0; color:{text_hex}; font-size:0.82rem; line-height:1.35;">{desc}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def get_chart_config():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4b5563'), 
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        showlegend=False
    )
    
def render_top_banner(title):
    st.markdown(
        f'<div class="page-title"><h2>{html.escape(title)}</h2></div>',
        unsafe_allow_html=True,
    )