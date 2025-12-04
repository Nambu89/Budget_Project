"""
Componente de recuperación de contraseña para Streamlit.
"""

import streamlit as st
import requests
from loguru import logger


def render_forgot_password():
    """
    Renderiza el formulario de solicitud de recuperación de contraseña.
    """
    st.title("🔐 Recuperar Contraseña")
    
    st.markdown("""
    Ingresa tu email y te enviaremos un link para restablecer tu contraseña.
    """)
    
    with st.form("forgot_password_form"):
        email = st.text_input(
            "📧 Email",
            placeholder="tu@email.com",
            help="Ingresa el email de tu cuenta"
        )
        
        submitted = st.form_submit_button(
            "Enviar Link de Recuperación",
            use_container_width=True
        )
        
        if submitted:
            if not email:
                st.error("Por favor ingresa tu email")
                return
            
            try:
                # Llamar a la API
                response = requests.post(
                    "http://localhost:8000/api/v1/auth/request-password-reset",
                    json={"email": email}
                )
                
                if response.status_code == 200:
                    st.success(
                        "✅ Si el email existe, recibirás un link de recuperación. "
                        "Revisa tu bandeja de entrada."
                    )
                    st.info(
                        "💡 El link expira en 1 hora. "
                        "Si no recibes el email, verifica tu carpeta de spam."
                    )
                else:
                    st.error("Error al procesar la solicitud. Intenta nuevamente.")
                    
            except Exception as e:
                logger.error(f"Error en forgot password: {e}")
                st.error("Error de conexión. Verifica que la API esté funcionando.")
    
    # Botón para volver al login
    st.markdown("---")
    if st.button("⬅️ Volver al Login"):
        st.session_state.show_forgot_password = False
        st.rerun()


def render_reset_password(token: str):
    """
    Renderiza el formulario de reset de contraseña con token.
    
    Args:
        token: Token de reset de contraseña
    """
    st.title("🔐 Nueva Contraseña")
    
    # Verificar token
    try:
        response = requests.get(
            f"http://localhost:8000/api/v1/auth/verify-reset-token/{token}"
        )
        
        if response.status_code != 200:
            st.error("❌ Link inválido o expirado")
            st.info("Solicita un nuevo link de recuperación")
            if st.button("Ir a Recuperación"):
                st.session_state.show_forgot_password = True
                st.rerun()
            return
        
        data = response.json()
        
        if not data.get('valid'):
            st.error("❌ Link inválido o expirado")
            st.info("El link solo es válido por 1 hora")
            if st.button("Solicitar Nuevo Link"):
                st.session_state.show_forgot_password = True
                st.rerun()
            return
        
        # Mostrar info del usuario
        st.success(f"✅ Link válido para: {data.get('email')}")
        st.info(f"👤 Usuario: {data.get('nombre')}")
        
        # Formulario de nueva contraseña
        with st.form("reset_password_form"):
            new_password = st.text_input(
                "🔒 Nueva Contraseña",
                type="password",
                help="Mínimo 6 caracteres"
            )
            
            confirm_password = st.text_input(
                "🔒 Confirmar Contraseña",
                type="password"
            )
            
            submitted = st.form_submit_button(
                "Cambiar Contraseña",
                use_container_width=True
            )
            
            if submitted:
                # Validaciones
                if not new_password or not confirm_password:
                    st.error("Por favor completa ambos campos")
                    return
                
                if len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                    return
                
                if new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                    return
                
                # Resetear contraseña
                try:
                    reset_response = requests.post(
                        "http://localhost:8000/api/v1/auth/reset-password",
                        json={
                            "token": token,
                            "new_password": new_password
                        }
                    )
                    
                    if reset_response.status_code == 200:
                        st.success("✅ ¡Contraseña actualizada correctamente!")
                        # st.balloons()
                        st.info("Ahora puedes iniciar sesión con tu nueva contraseña")
                        
                        # Limpiar query params y volver al login
                        if st.button("Ir al Login"):
                            st.session_state.clear()
                            st.rerun()
                    else:
                        error_detail = reset_response.json().get('detail', 'Error desconocido')
                        st.error(f"Error: {error_detail}")
                        
                except Exception as e:
                    logger.error(f"Error reseteando contraseña: {e}")
                    st.error("Error de conexión. Verifica que la API esté funcionando.")
        
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        st.error("Error de conexión. Verifica que la API esté funcionando.")
