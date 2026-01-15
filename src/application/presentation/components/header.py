"""
Componente Header para Streamlit.

Renderiza la cabecera de la aplicación con logo,
título y descripción.
"""

import streamlit as st
import os
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
        page_icon="Logo/Logo ISI.jpeg",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # CSS personalizado con colores corporativos
    st.markdown("""
        <style>
        /* Colores corporativos */
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
            font-size: 2rem;
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
    
    # Header con logo
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Mostrar logo si existe
        logo_path = "Logo/Logo ISI.jpeg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        
        # Título sin emoji
        st.markdown("""
            <div class="main-header">
                <div class="main-title">Calculadora de Presupuestos</div>
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
    - Info del usuario (si está autenticado)
    - Info de la empresa
    - Leyenda de calidades
    - Contacto
    """
    with st.sidebar:
        # Renderizar info del usuario o botón de login
        try:
            from .login import render_user_info
            
            if st.session_state.get("authenticated"):
                # Usuario autenticado: mostrar info
                render_user_info()
                st.divider()
            else:
                # Usuario no autenticado: mostrar opción de login
                if st.button("Iniciar sesión", use_container_width=True, key="sidebar_login_btn"):
                    st.session_state.show_sidebar_login = True
                    st.rerun()
                
                # Modal de login en sidebar
                if st.session_state.get("show_sidebar_login"):
                    _render_sidebar_login_modal()
                    st.divider()
                    
        except ImportError:
            pass
        
        st.markdown("### Contacto")
        st.markdown(f"""
        **{settings.empresa_nombre}**
        
        Tel: {settings.empresa_telefono}  
        Email: {settings.empresa_email}  
        Web: {settings.empresa_web}
        """)
        
        st.divider()
        
        st.markdown("### Niveles de Calidad")
        st.markdown("""
        **Básico**  
        Materiales económicos, buena relación calidad-precio
        
        **Estándar**  
        Materiales de calidad media-alta, equilibrio perfecto
        
        **Premium**  
        Materiales de alta gama, acabados de lujo
        """)
        
        st.divider()
        
        st.markdown("### Información")
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
        ("1", "Tipo de obra"),
        ("2", "Superficie"),
        ("3", "Partidas"),
        ("4", "Resultados"),
        ("5", "Datos"),
    ]
    
    cols = st.columns(len(steps))
    
    for i, (icon, label) in enumerate(steps):
        with cols[i]:
            step_num = i + 1
            if step_num < current_step:
                st.markdown(f"~~{label}~~")
            elif step_num == current_step:
                st.markdown(f"**{icon}. {label}**")
            else:
                st.markdown(f"{label}")
    
    # Barra de progreso con color corporativo
    progress = (current_step - 1) / (len(steps) - 1)
    st.progress(progress)


def render_footer() -> None:
    """Renderiza el pie de página."""
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; color: #999999; font-size: 0.8rem;">
            © 2026 {settings.empresa_nombre} | 
            Presupuesto orientativo - Requiere visita técnica
        </div>
        """, unsafe_allow_html=True)


def _render_sidebar_login_modal() -> None:
    """Modal de login rápido en el sidebar."""
    from loguru import logger
    from ...services.auth_service import get_auth_service
    
    with st.container(border=True):
        st.markdown("#### Iniciar sesión")
        
        with st.form("sidebar_login_form"):
            email = st.text_input("Email", placeholder="tu@email.com", key="side_email")
            password = st.text_input("Contraseña", type="password", key="side_pass")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                    if email and password:
                        try:
                            auth_service = get_auth_service()
                            user = auth_service.login(email, password)
                            if user:
                                st.session_state.user = user
                                st.session_state.authenticated = True
                                st.session_state.show_sidebar_login = False
                                st.rerun()
                            else:
                                st.error("Credenciales incorrectas")
                        except Exception as e:
                            logger.error(f"Error login sidebar: {e}")
                            st.error("Error al iniciar sesión")
                    else:
                        st.error("Completa todos los campos")
            
            with col2:
                if st.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state.show_sidebar_login = False
                    st.rerun()