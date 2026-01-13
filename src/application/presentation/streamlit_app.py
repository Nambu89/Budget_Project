"""
Aplicación principal de Streamlit.

Orquesta todos los componentes de la UI para crear
la experiencia completa de generación de presupuestos.

FASE 2: Incluye estimaciones inteligentes con IA + caché optimizado + paso de estimaciones a resumen
OPTIMIZADO: BudgetCrew cacheado para evitar recargas en cada interacción
"""

import streamlit as st
from loguru import logger
import asyncio

from src.config.settings import settings
from src.application.crews import get_budget_crew
from src.application.services.email_service import get_email_service
from src.domain.models.project import Project
from src.application.presentation.components import (
	render_header,
	render_sidebar_info,
	render_progress_steps,
	render_footer,
	render_property_form,
	render_property_summary,
	render_work_selector,
	render_work_summary,
	render_results,
	render_download_section,
	render_empty_results,
	render_customer_form,
	render_customer_summary,
	render_login,
	render_user_info,
	render_registration_gate,
)


# ============================================================================
# CACHÉ DEL CREW - EVITA RECARGAS INNECESARIAS
# ============================================================================

@st.cache_resource
def get_crew_cached():
	"""
	Obtiene el BudgetCrew cacheado para evitar reinicializaciones.
	
	Streamlit recarga todo el script en cada interacción.
	Esta función cachea el crew para que solo se inicialice una vez.
	
	Returns:
		BudgetCrew: Instancia cacheada del crew
	"""
	logger.info("🔄 Inicializando BudgetCrew (cacheado)...")
	return get_budget_crew()


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def init_session_state() -> None:
	"""Inicializa el estado de la sesión."""
	defaults = {
		"current_step": 1,
		"proyecto_data": None,
		"partidas_seleccionadas": [],
		"paquetes_seleccionados": [],
		"presupuesto": None,
		"desglose": None,
		"sugerencias": [],
		"pdf_bytes": None,
		"cliente_data": None,
		"proceso_completado": False,
		"estimaciones_ia": None,
		"proyecto_estimado_hash": None,
		"mostrar_modal_email": False,
	}
	
	for key, value in defaults.items():
		if key not in st.session_state:
			st.session_state[key] = value


def main() -> None:
	"""Función principal de la aplicación."""

	# Verificar si hay un token de reset en la URL
	query_params = st.query_params
	if "reset_token" in query_params:
		from src.application.presentation.pages.reset_password import render_reset_password_page
		render_reset_password_page(query_params["reset_token"])
		return
	
	# LEAD GENERATION: Ya NO bloqueamos al inicio
	# El usuario puede crear presupuesto sin login
	# El login se requerirá en el paso 5 (ver resultado final)
	
	# Inicializar estado
	init_session_state()
	
	# Gestión de páginas
	if 'current_page' not in st.session_state:
		st.session_state.current_page = "calculator"
	
	# Renderizar header (configura página también) - SOLO UNA VEZ
	render_header()
	
	# Sidebar con información - SOLO UNA VEZ
	render_sidebar_info()
	
	# Renderizar según página actual
	if st.session_state.current_page == "mis_presupuestos":
		from src.application.presentation.pages.mis_presupuestos import render_mis_presupuestos
		render_mis_presupuestos()
		render_footer()
		return
	
	# Si no, renderizar calculadora normal
	# Progreso
	render_progress_steps(st.session_state.current_step)
	
	st.divider()
	
	# Contenido principal según el paso actual
	if st.session_state.current_step == 1:
		_render_step_1_proyecto()
	
	elif st.session_state.current_step == 2:
		_render_step_2_trabajos()
	
	elif st.session_state.current_step == 3:
		_render_step_3_calculo()
	
	elif st.session_state.current_step == 4:
		_render_step_4_cliente()
	
	elif st.session_state.current_step == 5:
		_render_step_5_final()
	
	# Footer
	render_footer()


def _necesita_calcular_estimaciones(proyecto: Project) -> bool:
	"""
	Verifica si necesitamos calcular estimaciones.
	
	Args:
		proyecto: Proyecto actual
		
	Returns:
		True si necesita calcular, False si ya están calculadas
	"""
	if not proyecto.num_habitaciones:
		return False
	
	# Si ya tenemos estimaciones, verificar si el proyecto cambió
	if st.session_state.get("estimaciones_ia"):
		proyecto_hash = hash((
			proyecto.metros_cuadrados,
			proyecto.num_habitaciones,
			proyecto.ubicacion or ""
		))
		
		# Si el hash es el mismo, no recalcular
		if st.session_state.get("proyecto_estimado_hash") == proyecto_hash:
			return False
	
	return True


def _mostrar_estimaciones_guardadas() -> None:
	"""
	Muestra las estimaciones ya calculadas sin recalcular.
	"""
	estimaciones = st.session_state.get("estimaciones_ia")
	if not estimaciones:
		return
	
	st.markdown("### ✨ Estimaciones Inteligentes con IA")
	
	# Mostrar estimaciones en columnas
	col1, col2, col3 = st.columns(3)
	
	with col1:
		st.metric(
			label="🏠 m² de paredes",
			value=f"{estimaciones['m2_paredes_estimado']:.1f} m²",
			help="Superficie total de paredes (ancho × alto)"
		)
	
	with col2:
		st.metric(
			label="📏 Rodapiés",
			value=f"{estimaciones['ml_rodapies_estimado']:.1f} ml",
			help="Metros lineales de perímetro"
		)
	
	with col3:
		st.metric(
			label="🚪 Puertas",
			value=f"{estimaciones['num_puertas_estimado']} ud",
			help="Número de puertas de paso estimadas"
		)
	
	# Mostrar distribución de espacios si está disponible
	if estimaciones.get("distribucion_espacios"):
		with st.expander("📐 Distribución estimada de espacios"):
			st.markdown("**Espacios detectados:**")
			
			for espacio in estimaciones["distribucion_espacios"]:
				tipo = espacio.get("tipo", "").capitalize()
				cantidad = espacio.get("cantidad", 0)
				m2_prom = espacio.get("m2_promedio", 0)
				
				if cantidad > 0:
					st.markdown(f"- **{tipo}:** {cantidad} × {m2_prom:.1f} m² ≈ {cantidad * m2_prom:.1f} m² totales")
	
	# Mostrar razonamiento
	if estimaciones.get("razonamiento"):
		with st.expander("🧠 Razonamiento de la IA"):
			st.info(estimaciones["razonamiento"])
	
	# Indicador de confianza
	confianza = estimaciones.get("confianza", "baja")
	mensaje = estimaciones.get("mensaje", "")
	
	if confianza == "alta":
		st.success(f"✅ {mensaje}")
	else:
		st.info(f"ℹ️ {mensaje}")


def _render_step_1_proyecto() -> None:
	"""Renderiza el paso 1: Datos del proyecto."""
	st.markdown("## Paso 1: Información del proyecto")
	
	datos_proyecto = render_property_form()
	
	# FASE 2: Gestión inteligente de estimaciones con caché
	if datos_proyecto and datos_proyecto.num_habitaciones:
		st.divider()
		
		# Verificar si necesitamos calcular o solo mostrar
		if _necesita_calcular_estimaciones(datos_proyecto):
			# CALCULAR: Primera vez o proyecto cambió
			_mostrar_estimaciones_inteligentes(datos_proyecto)
			
			# Guardar hash del proyecto para futuras comparaciones
			proyecto_hash = hash((
				datos_proyecto.metros_cuadrados,
				datos_proyecto.num_habitaciones,
				datos_proyecto.ubicacion or ""
			))
			st.session_state.proyecto_estimado_hash = proyecto_hash
		else:
			# MOSTRAR: Ya tenemos estimaciones válidas
			_mostrar_estimaciones_guardadas()
	
	st.divider()
	
	col1, col2 = st.columns([3, 1])
	
	with col2:
		if datos_proyecto:
			if st.button("Siguiente →", type="primary", use_container_width=True):
				st.session_state.proyecto_data = datos_proyecto
				st.session_state.current_step = 2
				st.rerun()
		else:
			st.button(
				"Siguiente →",
				disabled=True,
				use_container_width=True,
				help="Completa la información del proyecto",
			)
	
	with col1:
		if datos_proyecto:
			st.success("✅ Proyecto configurado correctamente")
		else:
			st.warning("⚠️ Selecciona el tipo de inmueble para continuar")


def _mostrar_estimaciones_inteligentes(proyecto: Project) -> None:
	"""
	Calcula y muestra las estimaciones inteligentes calculadas por IA.
	
	Args:
		proyecto: Proyecto con num_habitaciones
	"""
	st.markdown("### ✨ Estimaciones Inteligentes con IA")
	
	with st.spinner("🤖 Calculando estimaciones con inteligencia artificial..."):
		try:
			crew = get_crew_cached()  # ← USAR VERSIÓN CACHEADA
			estimaciones = asyncio.run(crew.calculator.calcular_estimaciones_inteligentes(proyecto))
			
			# GUARDAR en session_state
			st.session_state.estimaciones_ia = estimaciones
			
			# Mostrar estimaciones en columnas
			col1, col2, col3 = st.columns(3)
			
			with col1:
				st.metric(
					label="🏠 m² de paredes",
					value=f"{estimaciones['m2_paredes_estimado']:.1f} m²",
					help="Superficie total de paredes (ancho × alto)"
				)
			
			with col2:
				st.metric(
					label="📏 Rodapiés",
					value=f"{estimaciones['ml_rodapies_estimado']:.1f} ml",
					help="Metros lineales de perímetro"
				)
			
			with col3:
				st.metric(
					label="🚪 Puertas",
					value=f"{estimaciones['num_puertas_estimado']} ud",
					help="Número de puertas de paso estimadas"
				)
			
			# Mostrar distribución de espacios si está disponible
			if estimaciones.get("distribucion_espacios"):
				with st.expander("📐 Distribución estimada de espacios"):
					st.markdown("**Espacios detectados:**")
					
					for espacio in estimaciones["distribucion_espacios"]:
						tipo = espacio.get("tipo", "").capitalize()
						cantidad = espacio.get("cantidad", 0)
						m2_prom = espacio.get("m2_promedio", 0)
						
						if cantidad > 0:
							st.markdown(f"- **{tipo}:** {cantidad} × {m2_prom:.1f} m² ≈ {cantidad * m2_prom:.1f} m² totales")
			
			# Mostrar razonamiento
			if estimaciones.get("razonamiento"):
				with st.expander("🧠 Razonamiento de la IA"):
					st.info(estimaciones["razonamiento"])
			
			# Indicador de confianza
			confianza = estimaciones.get("confianza", "baja")
			mensaje = estimaciones.get("mensaje", "")
			
			if confianza == "alta":
				st.success(f"✅ {mensaje}")
			else:
				st.info(f"ℹ️ {mensaje}")
				
		except Exception as e:
			logger.error(f"Error mostrando estimaciones: {e}")
			st.warning("⚠️ No se pudieron calcular las estimaciones inteligentes. Continuaremos con estimaciones básicas.")


def _render_step_2_trabajos() -> None:
	"""Renderiza el paso 2: Selección de trabajos."""
	st.markdown("## Paso 2: Trabajos a realizar")
	
	# FASE 2: Resumen del proyecto CON estimaciones IA
	if st.session_state.proyecto_data:
		render_property_summary(
			st.session_state.proyecto_data,
			estimaciones=st.session_state.get("estimaciones_ia")  # ← NUEVO: Pasar estimaciones
		)
		st.divider()
	
	# Selector de trabajos
	calidad = st.session_state.proyecto_data.calidad_general if st.session_state.proyecto_data else None
	trabajos = render_work_selector(calidad)
	
	st.divider()
	
	# Navegación
	col1, col2, col3 = st.columns([1, 2, 1])
	
	with col1:
		if st.button("← Anterior", use_container_width=True):
			st.session_state.current_step = 1
			st.rerun()
	
	with col2:
		render_work_summary()
	
	with col3:
		tiene_trabajos = (
			len(st.session_state.partidas_seleccionadas) > 0 or
			len(st.session_state.paquetes_seleccionados) > 0
		)
		
		if tiene_trabajos:
			if st.button("Calcular presupuesto →", type="primary", use_container_width=True):
				st.session_state.current_step = 3
				st.rerun()
		else:
			st.button(
				"Calcular presupuesto →",
				disabled=True,
				use_container_width=True,
				help="Selecciona al menos un trabajo",
			)


def _render_step_3_calculo() -> None:
	"""Renderiza el paso 3: Cálculo del presupuesto."""
	st.markdown("## Paso 3: Tu presupuesto")
	
	# Calcular si no existe
	if st.session_state.presupuesto is None:
		with st.spinner("🔄 Calculando tu presupuesto..."):
			_calcular_presupuesto()
	
	# ══════════════════════════════════════════════════════════════════
	# LEAD GENERATION: Verificar autenticación antes de mostrar resultado
	# ══════════════════════════════════════════════════════════════════
	if st.session_state.presupuesto and not st.session_state.get("authenticated"):
		# Mostrar gate de registro con rango de precios
		render_registration_gate(st.session_state.presupuesto)
		
		st.divider()
		
		# Solo botón de volver
		if st.button("← Modificar trabajos", use_container_width=True):
			st.session_state.presupuesto = None
			st.session_state.current_step = 2
			st.rerun()
		return  # No continuar hasta que se autentique
	
	# ══════════════════════════════════════════════════════════════════
	# Usuario autenticado: Mostrar presupuesto completo
	# ══════════════════════════════════════════════════════════════════
	if st.session_state.presupuesto:
		# FASE 2: Pasar estimaciones
		render_results(
			presupuesto=st.session_state.presupuesto,
			desglose=st.session_state.desglose,
			sugerencias=st.session_state.sugerencias,
			estimaciones=st.session_state.get("estimaciones_ia"),
		)
		
		st.divider()
		
		# Navegación
		col1, col2, col3 = st.columns([1, 2, 1])
		
		with col1:
			if st.button("← Modificar trabajos", use_container_width=True):
				st.session_state.presupuesto = None
				st.session_state.current_step = 2
				st.rerun()
		
		with col2:
			if st.button("🔄 Recalcular", use_container_width=True):
				st.session_state.presupuesto = None
				st.rerun()
		
		with col3:
			if st.button("Continuar →", type="primary", use_container_width=True):
				st.session_state.current_step = 4
				st.rerun()
	else:
		render_empty_results()
		
		if st.button("← Volver", use_container_width=True):
			st.session_state.current_step = 2
			st.rerun()


def _render_step_4_cliente() -> None:
	"""Renderiza el paso 4: Datos del cliente."""
	st.markdown("## Paso 4: Tus datos")
	
	# Resumen del presupuesto
	if st.session_state.presupuesto:
		col1, col2 = st.columns([2, 1])
		
		with col1:
			st.markdown(f"""
				**Presupuesto:** {st.session_state.presupuesto.numero_presupuesto}  
				**Total:** {st.session_state.presupuesto.total:,.2f}€ (IVA incluido)
			""")
		
		with col2:
			if st.button("← Volver al presupuesto"):
				st.session_state.current_step = 3
				st.rerun()
	
	st.divider()
	
	# Formulario de cliente
	datos_cliente = render_customer_form()
	
	if datos_cliente:
		st.session_state.cliente_data = datos_cliente
		st.session_state.current_step = 5
		st.rerun()


def _render_step_5_final() -> None:
	"""Renderiza el paso 5: Presupuesto final CON email funcional."""
	
	# ══════════════════════════════════════════════════════════════════
	# LEAD GENERATION: Verificar autenticación antes de mostrar resultado
	# ══════════════════════════════════════════════════════════════════
	if not st.session_state.get("authenticated"):
		# Mostrar gate de registro con rango de precios
		if st.session_state.presupuesto:
			render_registration_gate(st.session_state.presupuesto)
		else:
			# Si no hay presupuesto calculado, volver al paso anterior
			st.warning("⚠️ Ocurrió un error. Por favor, vuelve a calcular el presupuesto.")
			if st.button("← Volver"):
				st.session_state.current_step = 3
				st.rerun()
		return  # No continuar hasta que se autentique
	
	# ══════════════════════════════════════════════════════════════════
	# Usuario autenticado: Mostrar presupuesto completo
	# ══════════════════════════════════════════════════════════════════
	st.markdown("## ✅ ¡Presupuesto completado!")
	
	# Asignar cliente al presupuesto y generar PDF
	if st.session_state.pdf_bytes is None:
		with st.spinner("📄 Generando tu presupuesto en PDF..."):
			_finalizar_presupuesto()
	
	# Mostrar resumen final
	if st.session_state.presupuesto:
		presupuesto = st.session_state.presupuesto
		
		# Resumen del cliente
		if st.session_state.cliente_data:
			render_customer_summary(st.session_state.cliente_data)
		
		st.divider()
		
		# Resultados - FASE 2: Pasar estimaciones
		render_results(
			presupuesto=presupuesto,
			desglose=st.session_state.desglose,
			sugerencias=[],  # Sin sugerencias en paso final
			estimaciones=st.session_state.get("estimaciones_ia"),
		)
		
		st.divider()
		
		# Descargas
		render_download_section(
			presupuesto=presupuesto,
			pdf_bytes=st.session_state.pdf_bytes,
			resumen_texto=presupuesto.resumen_texto,
		)
		
		st.divider()
		
		# ──────────────────────────────────────────────────────────────
		# MODAL DE ENVÍO POR EMAIL (si está activado)
		# ──────────────────────────────────────────────────────────────
		if st.session_state.get("mostrar_modal_email", False):
			_mostrar_modal_enviar_email()
		
		# ──────────────────────────────────────────────────────────────
		# ACCIONES FINALES
		# ──────────────────────────────────────────────────────────────
		col1, col2, col3 = st.columns(3)
		
		with col1:
			if st.button("🔄 Nuevo presupuesto", use_container_width=True):
				_reset_session()
				st.rerun()
		
		with col2:
			# ✅ BOTÓN EMAIL FUNCIONAL
			if st.button("📧 Enviar por email", use_container_width=True, type="secondary"):
				st.session_state.mostrar_modal_email = True
				st.rerun()
		
		with col3:
			st.button(
				"📅 Solicitar visita",
				use_container_width=True,
				disabled=True,
				help="Próximamente",
			)
		
		# Mensaje final
		st.success(f"""
			### 🎉 ¡Gracias por usar nuestra calculadora!
			
			Tu presupuesto **{presupuesto.numero_presupuesto}** está listo.
			
			**Próximos pasos:**
			1. Descarga tu presupuesto en PDF
			2. Revísalo con calma
			3. Contáctanos para una visita técnica gratuita
			
			📞 {settings.empresa_telefono}  
			✉️ {settings.empresa_email}
		""")


def _calcular_presupuesto() -> None:
	"""Calcula el presupuesto usando el BudgetCrew."""
	try:
		crew = get_crew_cached()  # ← USAR VERSIÓN CACHEADA
		
		# Preparar datos del formulario
		datos_formulario = {
			"tipo_inmueble": st.session_state.proyecto_data.tipo_inmueble,
			"metros_cuadrados": st.session_state.proyecto_data.metros_cuadrados,
			"num_habitaciones": st.session_state.proyecto_data.num_habitaciones,  # FASE 2
			"calidad": st.session_state.proyecto_data.calidad_general,
			"estado_actual": st.session_state.proyecto_data.estado_actual,
			"ubicacion": st.session_state.proyecto_data.ubicacion,  # IMPORTANTE: Se pasa al crew
			"descripcion": st.session_state.proyecto_data.descripcion,
			"partidas": st.session_state.partidas_seleccionadas,
			"paquetes": st.session_state.paquetes_seleccionados,
		}
		
		# ══════════════════════════════════════════════════════════════════
		# Extraer opciones de paquetes (ej: armario empotrado para habitación)
		# ══════════════════════════════════════════════════════════════════
		opciones_paquetes = {}
		for paquete in st.session_state.paquetes_seleccionados:
			# Buscar opciones en session_state (formato: opcion_{paquete}_{opcion})
			for key in st.session_state:
				if key.startswith(f"opcion_{paquete}_"):
					opcion_nombre = key.replace(f"opcion_{paquete}_", "")
					if st.session_state[key]:  # Solo si está activada
						if paquete not in opciones_paquetes:
							opciones_paquetes[paquete] = []
						opciones_paquetes[paquete].append(opcion_nombre)
		
		if opciones_paquetes:
			datos_formulario["opciones_paquetes"] = opciones_paquetes
		
		# Procesar
		resultado = crew.procesar_presupuesto(
			datos_formulario=datos_formulario,
			generar_pdf=False,  # PDF lo generamos después con datos del cliente
		)
		
		if resultado["exito"]:
			st.session_state.presupuesto = resultado["presupuesto"]
			st.session_state.desglose = resultado["desglose"]
			st.session_state.sugerencias = resultado.get("sugerencias", [])
			logger.info(f"Presupuesto calculado: {resultado['presupuesto'].numero_presupuesto}")
		else:
			for error in resultado["errores"]:
				st.error(f"❌ {error}")
			for warning in resultado["warnings"]:
				st.warning(f"⚠️ {warning}")
				
	except Exception as e:
		logger.exception(f"Error calculando presupuesto: {e}")
		st.error(f"Error al calcular el presupuesto: {str(e)}")


def _finalizar_presupuesto() -> None:
	"""Finaliza el presupuesto asignando cliente y generando PDF."""
	try:
		crew = get_crew_cached()  # ← USAR VERSIÓN CACHEADA
		presupuesto = st.session_state.presupuesto
		cliente_data = st.session_state.cliente_data
		
		if presupuesto and cliente_data:
			# Asignar cliente
			crew.document_agent.budget_service.asignar_cliente(
				presupuesto=presupuesto,
				**cliente_data,
			)
			
			# Generar PDF
			pdf_bytes = crew.document_agent.generar_pdf(presupuesto)
			st.session_state.pdf_bytes = pdf_bytes
			
			# Guardar en BD si el usuario está autenticado
			if st.session_state.get("authenticated"):
				user_id = st.session_state.user["id"]
				resultado = crew.document_agent.budget_service.guardar_presupuesto(
					user_id=user_id,
					presupuesto=presupuesto
				)
				if resultado.get("guardado"):
					logger.info(f"✓ Presupuesto guardado para usuario {user_id}")
					
					# Refrescar datos del usuario
					from src.application.services.auth_service import get_auth_service
					auth_service = get_auth_service()
					st.session_state.user = auth_service.refresh_user_data(user_id)
					
				else:
					logger.warning(f"No se pudo guardar presupuesto: {resultado.get('error')}")
			
			# Actualizar desglose
			st.session_state.desglose = crew.calculator.obtener_desglose_completo(presupuesto)
			
			logger.info(f"Presupuesto finalizado: {presupuesto.numero_presupuesto}")
			
	except Exception as e:
		logger.exception(f"Error finalizando presupuesto: {e}")
		st.error(f"Error al generar el PDF: {str(e)}")


def _reset_session() -> None:
	"""Resetea la sesión para un nuevo presupuesto."""
	keys_to_reset = [
		"current_step",
		"proyecto_data",
		"partidas_seleccionadas",
		"paquetes_seleccionados",
		"presupuesto",
		"desglose",
		"sugerencias",
		"pdf_bytes",
		"cliente_data",
		"proceso_completado",
		"estimaciones_ia",  # FASE 2
		"proyecto_estimado_hash",  # FASE 2
		"tipo_inmueble",
		"metros_cuadrados",
		"num_habitaciones",  # FASE 2
		"calidad",
		"estado_actual",
		"ubicacion",
	]
	
	for key in keys_to_reset:
		if key in st.session_state:
			del st.session_state[key]
	
	init_session_state()


def _mostrar_modal_enviar_email() -> None:
	"""
	Muestra modal para confirmar envío de email con el presupuesto.
	
	Permite al usuario:
	- Verificar/cambiar email destinatario
	- Añadir mensaje personalizado opcional
	- Enviar o cancelar
	"""
	with st.container(border=True):
		st.markdown("### 📧 Enviar presupuesto por email")
		
		# Email destinatario
		email_default = st.session_state.cliente_data.get("email", "")
		email_destinatario = st.text_input(
			"Email del destinatario",
			value=email_default,
			help="Email donde se enviará el presupuesto",
			key="email_destinatario_input"
		)
		
		# Mensaje personalizado (opcional)
		mensaje_personalizado = st.text_area(
			"Mensaje personalizado (opcional)",
			placeholder="Añade un mensaje personal que acompañe al presupuesto...",
			height=100,
			help="Este mensaje aparecerá destacado en el email",
			key="mensaje_personalizado_input"
		)
		
		# Botones de acción
		col1, col2 = st.columns(2)
		
		with col1:
			if st.button("❌ Cancelar", use_container_width=True):
				st.session_state.mostrar_modal_email = False
				st.rerun()
		
		with col2:
			if st.button("✅ Enviar ahora", type="primary", use_container_width=True):
				if not email_destinatario or "@" not in email_destinatario:
					st.error("❌ Por favor, introduce un email válido")
				else:
					_ejecutar_envio_email(
						email_destinatario,
						mensaje_personalizado if mensaje_personalizado else None
					)


def _ejecutar_envio_email(email_destinatario: str, mensaje_personalizado: str = None) -> None:
	"""
	Ejecuta el envío del presupuesto por email.
	
	Args:
		email_destinatario: Email del destinatario
		mensaje_personalizado: Mensaje opcional del remitente
	"""
	presupuesto = st.session_state.presupuesto
	pdf_bytes = st.session_state.pdf_bytes
	
	if not presupuesto or not pdf_bytes:
		st.error("❌ No hay presupuesto disponible para enviar")
		return
	
	try:
		with st.spinner("📨 Enviando email..."):
			# Preparar datos del presupuesto para el email
			datos_presupuesto = {
				"numero": presupuesto.numero_presupuesto,
				"fecha": presupuesto.fecha_emision_str,
				"total": f"{presupuesto.total:,.2f}",
				"cliente": {
					"nombre": presupuesto.cliente.nombre if presupuesto.tiene_cliente else "Cliente",
				}
			}
			
			# Obtener servicio de email y enviar
			email_service = get_email_service()
			exito = email_service.enviar_presupuesto(
				email_destinatario=email_destinatario,
				pdf_bytes=pdf_bytes,
				datos_presupuesto=datos_presupuesto,
				mensaje_personalizado=mensaje_personalizado,
			)
			
			if exito:
				st.success(f"✅ ¡Presupuesto enviado con éxito a {email_destinatario}!")
				logger.info(f"Email enviado: {presupuesto.numero_presupuesto} → {email_destinatario}")
				
				# Cerrar modal
				st.session_state.mostrar_modal_email = False
				
				# Esperar 2 segundos y recargar
				import time
				time.sleep(2)
				st.rerun()
			else:
				st.error("❌ Hubo un error al enviar el email. Por favor, inténtalo de nuevo.")
				
	except ValueError as ve:
		st.error(f"❌ Error de configuración: {str(ve)}")
		st.info("💡 Verifica que las credenciales SMTP estén correctamente configuradas en el servidor.")
		logger.error(f"Error de configuración SMTP: {ve}")
		
	except Exception as e:
		st.error(f"❌ Error inesperado al enviar el email: {str(e)}")
		logger.exception(f"Error enviando email: {e}")

# Punto de entrada cuando se ejecuta directamente
if __name__ == "__main__":
	main()