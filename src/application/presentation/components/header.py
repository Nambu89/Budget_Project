"""
Componente Header para Streamlit.

Renderiza la cabecera de la aplicación con logo,
título y descripción.
"""

import streamlit as st
from src.config.settings import settings


def render_header() -> None:
    """
    Renderiza la cabecera de la aplicación.
    
    Incluye:
    - Logo (si existe)
    - Título principal
    - Descripción
    - Línea separadora
    """
    # Configurar página (debe ser lo primero)
    st.set_page_config(
        page_title="ISI Obras y Presupuestos | Calculadora de Presupuestos",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # CSS personalizado con colores corporativos Easy Obras
    st.markdown("""
        <style>
        /* Colores corporativos Easy Obras */
        :root {
            --easy-obras-orange: #F39200;
            --easy-obras-grey: #999999;
            --easy-obras-black: #000000;
            --easy-obras-white: #FFFFFF;
        }
        
        .main-header {
            text-align: center;
            padding: 1rem 0;
        }
        .main-title {
            color: #F39200;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .main-subtitle {
            color: #999999;
            font-size: 1.1rem;
        }
        .stProgress > div > div > div > div {
            background-color: #F39200;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d1fae5;
            border: 1px solid #10b981;
        }
        .warning-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #fef3c7;
            border: 1px solid #F39200;
        }
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f5f5f5;
            border: 1px solid #999999;
        }
        .total-display {
            font-size: 2rem;
            font-weight: bold;
            color: #F39200;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, #FFF5E6 0%, #FFE6C2 100%);
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
            <div class="main-header">
                <div class="main-title">🏗️ Easy Obras - Calculadora de Presupuestos</div>
                <div class="main-subtitle">
                    Calcula tu presupuesto de reforma en menos de 3 minutos
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()


def render_sidebar_info() -> None:
    """
    Renderiza información en el sidebar.
    
    Incluye:
    - Info de la empresa
    - Leyenda de calidades
    - Contacto
    """
    with st.sidebar:
        st.markdown("### 📞 Contacto")
        st.markdown(f"""
        **{settings.empresa_nombre}**
        
        📞 {settings.empresa_telefono}  
        ✉️ {settings.empresa_email}  
        🌐 {settings.empresa_web}
        """)
        
        st.divider()
        
        st.markdown("### 💎 Niveles de Calidad")
        st.markdown("""
        **⚡ Básico**  
        Materiales económicos, buena relación calidad-precio
        
        **⭐ Estándar**  
        Materiales de calidad media-alta, equilibrio perfecto
        
        **💎 Premium**  
        Materiales de alta gama, acabados de lujo
        """)
        
        st.divider()
        
        st.markdown("### ℹ️ Información")
        st.markdown("""
        - Presupuesto orientativo
        - Precios con IVA incluido
        - Válido 30 días
        - Requiere visita técnica
        """)


def render_progress_steps(current_step: int) -> None:
    """
    Renderiza los pasos del progreso.
    
    Args:
        current_step: Paso actual (1-5)
    """
    steps = [
        ("1️⃣", "Tipo de obra"),
        ("2️⃣", "Superficie"),
        ("3️⃣", "Partidas"),
        ("4️⃣", "Resultados"),
        ("5️⃣", "Datos"),
    ]
    
    cols = st.columns(len(steps))
    
    for i, (icon, label) in enumerate(steps):
        with cols[i]:
            step_num = i + 1
            if step_num < current_step:
                st.markdown(f"✅ ~~{label}~~")
            elif step_num == current_step:
                st.markdown(f"**{icon} {label}**")
            else:
                st.markdown(f"⬜ {label}")
    
    # Barra de progreso con color corporativo
    progress = (current_step - 1) / (len(steps) - 1)
    st.progress(progress)


def render_footer() -> None:
    """Renderiza el pie de página."""
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; color: #999999; font-size: 0.85rem;">
            © 2025 ISI Obras y Presupuestos| 
            Presupuesto orientativo - Requiere visita técnica
        </div>
        """, unsafe_allow_html=True)