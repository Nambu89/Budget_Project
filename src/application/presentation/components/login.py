"""
Login Component - Componente de login y registro para Streamlit.
"""

import streamlit as st
from loguru import logger

from ...services.auth_service import get_auth_service


def render_login():
    """
    Renderiza la pantalla de login/registro.
    
    Gestiona el estado de autenticación en st.session_state.
    """
    st.title("🔐 Bienvenido")
    st.markdown("---")
    
    # Tabs para Login y Registro
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    # Tab 1: Login
    with tab1:
        _render_login_form()
    
    # Tab 2: Registro
    with tab2:
        _render_register_form()


def _render_login_form():
    """Renderiza el formulario de login."""
    st.subheader("Iniciar Sesión")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="tu@email.com",
            help="Ingresa tu email registrado"
        )
        
        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Tu contraseña",
            help="Mínimo 6 caracteres"
        )
        
        submitted = st.form_submit_button(
            "Entrar",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not email or not password:
                st.error("Por favor completa todos los campos")
                return
            
            # Intentar login
            auth_service = get_auth_service()
            user = auth_service.login(email, password)
            
            if user:
                # Guardar en sesión (user ya es un dict)
                st.session_state.user = user
                st.session_state.authenticated = True
                
                st.success(f"¡Bienvenido {user['nombre']}!")
                logger.info(f"Usuario logueado en Streamlit: {user['email']}")
                
                # Recargar para mostrar app principal
                st.rerun()
            else:
                st.error("❌ Email o contraseña incorrectos")
    
    # Botón de forgot password
    st.markdown("---")
    if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
        st.session_state.show_forgot_password = True
        st.rerun()



def _render_register_form():
    """Renderiza el formulario de registro."""
    st.subheader("Crear Cuenta")
    
    with st.form("register_form"):
        nombre = st.text_input(
            "Nombre Completo *",
            placeholder="Juan Pérez",
            help="Tu nombre completo"
        )
        
        email = st.text_input(
            "Email *",
            placeholder="tu@email.com",
            help="Será tu nombre de usuario"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            telefono = st.text_input(
                "Teléfono",
                placeholder="600123456",
                help="Opcional"
            )
        
        with col2:
            empresa = st.text_input(
                "Empresa",
                placeholder="Mi Empresa",
                help="Opcional"
            )
        
        password = st.text_input(
            "Contraseña *",
            type="password",
            placeholder="Mínimo 6 caracteres",
            help="Elige una contraseña segura"
        )
        
        password_confirm = st.text_input(
            "Confirmar Contraseña *",
            type="password",
            placeholder="Repite tu contraseña"
        )
        
        submitted = st.form_submit_button(
            "Registrarse",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validaciones
            if not nombre or not email or not password:
                st.error("Por favor completa los campos obligatorios (*)")
                return
            
            if len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
                return
            
            if password != password_confirm:
                st.error("Las contraseñas no coinciden")
                return
            
            # Intentar registro
            auth_service = get_auth_service()
            user = auth_service.register(
                email=email,
                password=password,
                nombre=nombre,
                telefono=telefono if telefono else None,
                empresa=empresa if empresa else None
            )
            
            if user:
                st.success("✅ ¡Cuenta creada correctamente!")
                st.info("Ahora puedes iniciar sesión con tu email y contraseña")
                logger.info(f"Nuevo usuario registrado: {user['email']}")
            else:
                st.error("❌ Este email ya está registrado")


def render_user_info():
    """
    Renderiza información del usuario logueado en el sidebar.
    """
    if not st.session_state.get("authenticated"):
        return
    
    user = st.session_state.get("user")
    if not user:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Usuario")
        st.markdown(f"**{user['nombre']}**")
        st.markdown(f"📧 {user['email']}")
        
        if user.get('empresa'):
            st.markdown(f"🏢 {user['empresa']}")
        
        st.markdown(f"📊 {user.get('num_presupuestos', 0)} presupuestos")
        
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            logger.info(f"Usuario cerró sesión: {user['email']}")
            st.rerun()


def require_auth():
    """
    Verifica que el usuario esté autenticado.
    
    Si no está autenticado, muestra la pantalla de login.
    
    Returns:
        bool: True si está autenticado
    """
    if not st.session_state.get("authenticated"):
        render_login()
        st.stop()
        return False
    
    return True
