"""
Página de reset de contraseña.
"""

import streamlit as st
from loguru import logger
from ...services.auth_service import get_auth_service


def render_reset_password_page(token: str):
	"""
	Renderiza la página de reset de contraseña.
	
	Args:
		token: Token de reset desde la URL
	"""
	st.set_page_config(
		page_title="Restablecer Contraseña - ISI Obras",
		page_icon="🔐",
		layout="centered"
	)
	
	st.title("🔐 Restablecer Contraseña")
	st.markdown("---")
	
	# Validar token
	auth_service = get_auth_service()
	user_info = auth_service.verify_reset_token(token)
	
	if not user_info:
		st.error("❌ El link de recuperación es inválido o ha expirado.")
		st.info("Por favor solicita un nuevo link de recuperación.")
		
		st.markdown("---")
		if st.button("Ir al login", use_container_width=True, type="primary"):
			st.query_params.clear()
			st.rerun()
		return
	
	# Formulario de nueva contraseña
	st.success(f"✅ Link válido para: **{user_info['email']}**")
	st.info("Ingresa tu nueva contraseña a continuación.")
	
	with st.form("reset_password_form"):
		nueva_password = st.text_input(
			"Nueva Contraseña",
			type="password",
			placeholder="Mínimo 6 caracteres",
			help="Elige una contraseña segura"
		)
		
		confirmar_password = st.text_input(
			"Confirmar Nueva Contraseña",
			type="password",
			placeholder="Repite tu contraseña"
		)
		
		submitted = st.form_submit_button(
			"Cambiar Contraseña",
			use_container_width=True,
			type="primary"
		)
		
		if submitted:
			# Validaciones
			if not nueva_password or not confirmar_password:
				st.error("Por favor completa ambos campos")
				return
			
			if len(nueva_password) < 6:
				st.error("La contraseña debe tener al menos 6 caracteres")
				return
			
			if nueva_password != confirmar_password:
				st.error("Las contraseñas no coinciden")
				return
			
			# Cambiar contraseña
			try:
				resultado = auth_service.reset_password(token, nueva_password)
				
				if resultado:
					st.success("✅ ¡Contraseña cambiada correctamente!")
					st.info("Ya puedes iniciar sesión con tu nueva contraseña.")
					# st.balloons()
					
					st.markdown("---")
					if st.button("Ir al login", use_container_width=True, type="primary", key="goto_login"):
						st.query_params.clear()
						st.rerun()
				else:
					st.error("❌ Error al cambiar la contraseña.")
					
			except ValueError as e:
				st.error(f"❌ {str(e)}")
			except Exception as e:
				logger.error(f"Error cambiando contraseña: {e}")
				st.error("❌ Error al cambiar la contraseña. Inténtalo de nuevo.")