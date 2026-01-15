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
	st.title(" Bienvenido")
	st.markdown("---")
	
	# Verificar si se está mostrando el formulario de reset
	if st.session_state.get("show_forgot_password", False):
		_render_forgot_password_form()
		return
	
	# Tabs para Login y Registro
	tab, tab = st.tabs(["Iniciar Sesión", "Registrarse"])
	
	# Tab : Login
	with tab:
		_render_login_form()
	
	# Tab : Registro
	with tab:
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
			
			try:
				# Intentar login (puede lanzar ValueError)
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
					st.error(" Email o contraseña incorrectos")
					
			except ValueError as e:
				# Capturar error de credenciales inválidas
				st.error(f" {str(e)}")
			except Exception as e:
				# Otros errores inesperados
				logger.error(f"Error en login: {e}")
				st.error(" Error al iniciar sesión. Inténtalo de nuevo.")
	
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
		
		col, col = st.columns()
		
		with col:
			telefono = st.text_input(
				"Teléfono",
				placeholder="6006",
				help="Opcional"
			)
		
		with col:
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
			
			try:
				# Intentar registro (puede lanzar ValueError)
				auth_service = get_auth_service()
				user = auth_service.register(
					email=email,
					password=password,
					nombre=nombre,
					telefono=telefono if telefono else None,
					empresa=empresa if empresa else None
				)
				
				if user:
					st.success(" ¡Cuenta creada correctamente!")
					st.info("Ahora puedes iniciar sesión con tu email y contraseña")
					logger.info(f"Nuevo usuario registrado: {user['email']}")
				else:
					st.error(" No se pudo crear la cuenta")
					
			except ValueError as e:
				# Email duplicado u otro error de validación
				st.error(f" {str(e)}")
			except Exception as e:
				# Otros errores inesperados
				logger.error(f"Error en registro: {e}")
				st.error(" Error al crear la cuenta. Inténtalo de nuevo.")

def _render_forgot_password_form():
	"""Renderiza el formulario de recuperación de contraseña."""
	st.subheader("Recuperar Contraseña")
	
	st.info(" Ingresa tu email y te enviaremos un link para restablecer tu contraseña.")
	
	with st.form("forgot_password_form"):
		email = st.text_input(
			"Email",
			placeholder="tu@email.com",
			help="Email con el que te registraste"
		)
		
		col, col = st.columns()
		
		with col:
			cancelar = st.form_submit_button(
				"← Cancelar",
				use_container_width=True
			)
		
		with col:
			enviar = st.form_submit_button(
				"Enviar link",
				use_container_width=True,
				type="primary"
			)
		
		if cancelar:
			st.session_state.show_forgot_password = False
			st.rerun()
		
		if enviar:
			if not email:
				st.error("Por favor ingresa tu email")
				return
			
			try:
				auth_service = get_auth_service()
				token = auth_service.request_password_reset(email)
				
				# Siempre mostrar éxito (seguridad)
				st.success(
					" Si el email existe en nuestro sistema, "
					"recibirás un link de recuperación en los próximos minutos.\n\n"
					"**Revisa tu bandeja de entrada y spam.**"
				)
				
				# Si se generó token, enviar email
				if token:
					from ...services.email_service import get_email_service
					from ....config.settings import settings
					
					reset_link = f"{settings.app_url}/?reset_token={token}"
					
					email_service = get_email_service()
					email_service.enviar_reset_password(
						email_destinatario=email,
						reset_link=reset_link,
						nombre="Usuario"
					)
					
					logger.info(f"Email de reset enviado a: {email}")
				
			except Exception as e:
				logger.error(f"Error en forgot password: {e}")
				st.error(" Error al procesar la solicitud. Inténtalo de nuevo.")

def render_user_info() -> None:
	"""Renderiza la información del usuario autenticado en el sidebar."""
	if not st.session_state.get("authenticated"):
		return
	
	user = st.session_state.get("user")
	if not user:
		return
	
	with st.sidebar:
		st.markdown("###  Usuario")
		st.markdown(f"**{user['nombre']}**")
		st.caption(user['email'])
		
		# Mostrar contador de presupuestos
		# CONSULTAR PRESUPUESTOS DIRECTAMENTE A LA BD
		try:
			from ....application.services.user_budget_service import get_user_budget_service
			budget_service = get_user_budget_service()
			presupuestos = budget_service.get_user_budgets(user['id'])
			num_presupuestos = len(presupuestos)
		except Exception as e:
			logger.error(f"Error obteniendo presupuestos del usuario: {e}")
			num_presupuestos = 0

		st.info(f" {num_presupuestos} presupuesto{'s' if num_presupuestos !=  else ''}")
		
		st.divider()
		
		# Botones de navegación según página actual
		current_page = st.session_state.get("current_page", "calculator")
		
		if current_page == "calculator":
			# Si estamos en la calculadora, mostrar botón a presupuestos
			if st.button(" Mis Presupuestos", use_container_width=True):
				st.session_state.current_page = "mis_presupuestos"
				st.rerun()
		else:
			# Si estamos en otra página, mostrar botón a calculadora
			if st.button(" Calculadora", use_container_width=True):
				st.session_state.current_page = "calculator"
				st.rerun()
		
		# Botón de cerrar sesión
		if st.button(" Cerrar Sesión", use_container_width=True):
			st.session_state.authenticated = False
			st.session_state.user = None
			st.session_state.current_page = "calculator"
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