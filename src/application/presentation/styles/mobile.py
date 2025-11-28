"""
Mobile-First Styles - Estilos CSS responsive para Streamlit.

Aplica diseño mobile-first con breakpoints para tablet y desktop.
"""

# CSS Mobile-First
MOBILE_FIRST_CSS = """
<style>
/* ========================================
   VARIABLES Y RESET
   ======================================== */
:root {
    --primary-color: #1f77b4;
    --secondary-color: #ff7f0e;
    --success-color: #2ca02c;
    --danger-color: #d62728;
    --text-color: #262730;
    --bg-color: #ffffff;
    --border-color: #e6e9ef;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* ========================================
   MOBILE FIRST (< 768px)
   ======================================== */
@media (max-width: 768px) {
    /* Contenedor principal */
    .stApp {
        padding: 0.5rem !important;
    }
    
    /* Ocultar sidebar en móvil por defecto */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    section[data-testid="stSidebar"][aria-expanded="true"] {
        display: block;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Botones táctiles grandes */
    .stButton button {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Inputs táctiles */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox select,
    .stTextArea textarea {
        font-size: 16px !important; /* Evita zoom en iOS */
        min-height: 44px !important;
        padding: 0.75rem !important;
        border-radius: 8px !important;
    }
    
    /* Columnas apiladas en móvil */
    .row-widget.stHorizontal {
        flex-direction: column !important;
    }
    
    .row-widget.stHorizontal > div {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Tabs más grandes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        min-height: 44px !important;
    }
    
    /* Headers más compactos */
    h1 {
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Cards con mejor espaciado */
    .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Formularios */
    .stForm {
        padding: 1rem !important;
        border-radius: 12px !important;
        background: var(--bg-color);
        box-shadow: var(--shadow);
    }
    
    /* Expanders táctiles */
    .streamlit-expanderHeader {
        min-height: 48px !important;
        font-size: 1.1rem !important;
        padding: 0.75rem !important;
    }
    
    /* Métricas apiladas */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    
    /* Tablas responsive */
    .stDataFrame {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    
    /* Alertas */
    .stAlert {
        padding: 1rem !important;
        border-radius: 8px !important;
        margin: 0.5rem 0 !important;
    }
}

/* ========================================
   TABLET (769px - 1024px)
   ======================================== */
@media (min-width: 769px) and (max-width: 1024px) {
    .stApp {
        padding: 1rem !important;
    }
    
    section[data-testid="stSidebar"] {
        width: 250px !important;
    }
    
    .stButton button {
        min-height: 44px !important;
        padding: 0.625rem 1rem !important;
    }
    
    /* Columnas en 2 en tablet */
    .row-widget.stHorizontal > div {
        flex: 1 1 48% !important;
    }
}

/* ========================================
   DESKTOP (> 1024px)
   ======================================== */
@media (min-width: 1025px) {
    .stApp {
        max-width: 1400px !important;
        margin: 0 auto !important;
        padding: 2rem !important;
    }
    
    section[data-testid="stSidebar"] {
        width: 300px !important;
    }
    
    /* Hover effects solo en desktop */
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
    }
}

/* ========================================
   MEJORAS GENERALES
   ======================================== */

/* Botones primarios */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary-color), #1565c0) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(31, 119, 180, 0.3) !important;
}

/* Botones secundarios */
.stButton button[kind="secondary"] {
    background: white !important;
    border: 2px solid var(--primary-color) !important;
    color: var(--primary-color) !important;
    font-weight: 600 !important;
}

/* Focus visible para accesibilidad */
*:focus-visible {
    outline: 2px solid var(--primary-color) !important;
    outline-offset: 2px !important;
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Loading spinner */
.stSpinner > div {
    border-color: var(--primary-color) !important;
}

/* Success messages */
.stSuccess {
    background-color: rgba(44, 160, 44, 0.1) !important;
    border-left: 4px solid var(--success-color) !important;
}

/* Error messages */
.stError {
    background-color: rgba(214, 39, 40, 0.1) !important;
    border-left: 4px solid var(--danger-color) !important;
}

/* Warning messages */
.stWarning {
    background-color: rgba(255, 127, 14, 0.1) !important;
    border-left: 4px solid var(--secondary-color) !important;
}

/* Info messages */
.stInfo {
    background-color: rgba(31, 119, 180, 0.1) !important;
    border-left: 4px solid var(--primary-color) !important;
}

/* Cards con sombra */
.element-container > div {
    border-radius: 12px;
}

/* Dividers más suaves */
hr {
    margin: 1.5rem 0 !important;
    border: none !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, var(--border-color), transparent) !important;
}

/* ========================================
   ANIMACIONES
   ======================================== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.element-container {
    animation: fadeIn 0.3s ease-out;
}

/* ========================================
   DARK MODE SUPPORT
   ======================================== */
@media (prefers-color-scheme: dark) {
    :root {
        --text-color: #fafafa;
        --bg-color: #0e1117;
        --border-color: #262730;
    }
}

/* ========================================
   PRINT STYLES
   ======================================== */
@media print {
    section[data-testid="stSidebar"],
    .stButton,
    header {
        display: none !important;
    }
    
    .stApp {
        padding: 0 !important;
    }
}
</style>
"""


def apply_mobile_styles():
    """
    Aplica estilos mobile-first a la aplicación Streamlit.
    
    Debe llamarse al inicio de la aplicación, típicamente en main().
    """
    import streamlit as st
    st.markdown(MOBILE_FIRST_CSS, unsafe_allow_html=True)


def set_mobile_viewport():
    """
    Configura el viewport para móviles.
    
    Mejora la experiencia en dispositivos móviles.
    """
    import streamlit as st
    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        """,
        unsafe_allow_html=True
    )
