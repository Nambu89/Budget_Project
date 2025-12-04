"""
Componente de formulario para datos del inmueble/proyecto.

FASE 2: Incluye soporte para mostrar estimaciones IA en resumen
"""

import streamlit as st
from typing import Optional

from ....domain.enums.property_type import PropertyType
from ....domain.enums.quality_level import QualityLevel
from ....domain.models.project import Project


def render_property_form() -> Optional[Project]:
	"""
	Renderiza el formulario de datos del inmueble.
	
	Returns:
		Project si el formulario está completo, None en caso contrario
	"""
	st.subheader("📋 Datos del Inmueble")
	
	col1, col2 = st.columns(2)
	
	with col1:
		# Tipo de inmueble
		tipo_opciones = PropertyType.get_choices()
		tipo_labels = [label for _, label in tipo_opciones]
		tipo_values = [value for value, _ in tipo_opciones]
		
		tipo_seleccionado_idx = st.selectbox(
			"Tipo de inmueble",
			range(len(tipo_labels)),
			format_func=lambda i: tipo_labels[i],
			help="Selecciona el tipo de propiedad a reformar"
		)
		
		tipo_inmueble = PropertyType(tipo_values[tipo_seleccionado_idx])
		
		# Metros cuadrados
		metros_cuadrados = st.number_input(
			"Superficie total (m²)",
			min_value=10.0,
			max_value=10000.0,
			value=80.0,
			step=5.0,
			help="Superficie total del inmueble en metros cuadrados"
		)
		
		# FASE 2: Número de habitaciones
		num_habitaciones = st.number_input(
			"Número de habitaciones/salas (opcional)",
			min_value=0,
			max_value=50,
			value=0,
			step=1,
			help="Número total de habitaciones, salas o espacios diferenciados. Ayuda a calcular estimaciones más precisas."
		)
		
		# Estado actual
		estado_actual = st.selectbox(
			"Estado actual",
			["nuevo", "normal", "antiguo", "ruina"],
			index=1,
			help="Estado actual del inmueble (afecta al factor de dificultad)"
		)
	
	with col2:
		# Calidad general
		calidad_opciones = QualityLevel.get_choices()
		calidad_labels = [label for _, label in calidad_opciones]
		calidad_values = [value for value, _ in calidad_opciones]
		
		calidad_idx = st.selectbox(
			"Calidad general",
			range(len(calidad_labels)),
			format_func=lambda i: calidad_labels[i],
			index=1,  # Por defecto: Estándar
			help="Nivel de calidad de los materiales y acabados"
		)
		
		calidad_general = QualityLevel(calidad_values[calidad_idx])
		
		# Ubicación
		ubicacion = st.text_input(
			"Ubicación",
			placeholder="Ej: Madrid, Barcelona, Valencia...",
			help="Ciudad o zona donde se ubica el inmueble"
		)
	
	# Descripción adicional (ancho completo)
	descripcion = st.text_area(
		"Descripción adicional (opcional)",
		placeholder="Detalles relevantes sobre el proyecto...",
		max_chars=1000,
		help="Información adicional que consideres relevante para el presupuesto"
	)
	
	# Info box sobre estimaciones IA
	if num_habitaciones > 0:
		st.success(
			f"✨ **Estimaciones inteligentes activadas:** Con {num_habitaciones} habitaciones, "
			"el sistema calculará automáticamente m² de paredes, rodapiés y puertas estimadas usando IA."
		)
	else:
		st.info(
			"💡 **Tip:** Si añades el número de habitaciones, el sistema hará cálculos inteligentes "
			"de paredes, rodapiés y puertas automáticamente."
		)
	
	# Info box sobre IVA
	st.info(
		"ℹ️ **IVA aplicable:** Todos los presupuestos aplican IVA general del 21% "
		"según normativa vigente."
	)
	
	# Validación
	if not ubicacion or not ubicacion.strip():
		st.warning("⚠️ Por favor, indica la ubicación del inmueble")
		return None
	
	# Crear objeto Project
	try:
		proyecto = Project(
			tipo_inmueble=tipo_inmueble,
			metros_cuadrados=metros_cuadrados,
			num_habitaciones=num_habitaciones if num_habitaciones > 0 else None,
			calidad_general=calidad_general,
			estado_actual=estado_actual,
			descripcion=descripcion.strip() if descripcion else None,
			ubicacion=ubicacion.strip()
		)
		
		return proyecto
		
	except Exception as e:
		st.error(f"❌ Error al crear proyecto: {str(e)}")
		return None


def render_property_summary(proyecto: Project, estimaciones: dict = None) -> None:
	"""
	Muestra un resumen visual del proyecto.
	
	Args:
		proyecto: Objeto Project a resumir
		estimaciones: Estimaciones IA (opcional) - FASE 2
	"""
	st.markdown("---")
	st.subheader("📊 Resumen del Proyecto")
	
	col1, col2, col3 = st.columns(3)
	
	with col1:
		st.metric(
			label="Tipo",
			value=proyecto.tipo_inmueble_nombre,
			delta=None
		)
		st.metric(
			label="Superficie",
			value=f"{proyecto.metros_cuadrados:.0f} m²",
			delta=None
		)
	
	with col2:
		st.metric(
			label="Calidad",
			value=proyecto.calidad_nombre,
			delta=None
		)
		st.metric(
			label="Estado",
			value=proyecto.estado_actual.capitalize(),
			delta=None
		)
	
	with col3:
		st.metric(
			label="IVA aplicable",
			value="21%",
			delta=None,
			help="IVA general según normativa vigente"
		)
		st.metric(
			label="Ubicación",
			value=proyecto.ubicacion or "No especificada",
			delta=None
		)
	
	# FASE 2: Mostrar habitaciones si existen
	if proyecto.num_habitaciones:
		st.divider()
		col_hab = st.columns([1, 2])[0]
		with col_hab:
			st.metric(
				label="🏠 Habitaciones/Salas",
				value=f"{proyecto.num_habitaciones}",
				delta=None,
				help="Número de espacios diferenciados"
			)
	
	# FASE 2: Mostrar estimaciones IA si existen
	if estimaciones:
		st.divider()
		st.markdown("### ✨ Estimaciones Inteligentes con IA")
		
		col1, col2, col3 = st.columns(3)
		
		with col1:
			st.metric(
				label="🏠 m² de paredes",
				value=f"{estimaciones['m2_paredes_estimado']:.1f} m²",
				delta=None,
				help="Superficie total de paredes calculada por IA"
			)
		
		with col2:
			st.metric(
				label="📏 Rodapiés",
				value=f"{estimaciones['ml_rodapies_estimado']:.1f} ml",
				delta=None,
				help="Metros lineales de perímetro calculados por IA"
			)
		
		with col3:
			st.metric(
				label="🚪 Puertas",
				value=f"{estimaciones['num_puertas_estimado']} ud",
				delta=None,
				help="Número de puertas estimadas por IA"
			)
		
		# Mostrar razonamiento si está disponible
		if estimaciones.get("razonamiento"):
			with st.expander("🧠 Razonamiento de la IA"):
				st.info(estimaciones["razonamiento"])
		
		# Indicador de ajuste por ubicación
		if estimaciones.get("ubicacion"):
			st.caption(f"📍 Estimaciones ajustadas para: **{estimaciones['ubicacion']}**")
	
	if proyecto.descripcion:
		with st.expander("📝 Descripción del proyecto"):
			st.write(proyecto.descripcion)
	
	# Mostrar factor de estado si es diferente de 1.0
	if proyecto.factor_estado != 1.0:
		factor_pct = (proyecto.factor_estado - 1) * 100
		if factor_pct > 0:
			st.info(
				f"ℹ️ Por el estado '{proyecto.estado_actual}' del inmueble, "
				f"se aplicará un factor de ajuste de +{factor_pct:.0f}% en los precios."
			)
		else:
			st.success(
				f"✅ Por el estado '{proyecto.estado_actual}' del inmueble, "
				f"se aplicará un factor de ajuste de {factor_pct:.0f}% en los precios."
			)


def render_property_edit_form(proyecto_actual: Project) -> Optional[Project]:
	"""
	Renderiza formulario de edición de proyecto existente.
	
	Args:
		proyecto_actual: Proyecto a editar
		
	Returns:
		Project actualizado o None si se cancela
	"""
	st.subheader("✏️ Editar Datos del Inmueble")
	
	col1, col2 = st.columns(2)
	
	with col1:
		# Tipo de inmueble
		tipo_opciones = PropertyType.get_choices()
		tipo_labels = [label for _, label in tipo_opciones]
		tipo_values = [value for value, _ in tipo_opciones]
		
		# Encontrar índice actual
		tipo_actual_idx = tipo_values.index(proyecto_actual.tipo_inmueble.value)
		
		tipo_seleccionado_idx = st.selectbox(
			"Tipo de inmueble",
			range(len(tipo_labels)),
			format_func=lambda i: tipo_labels[i],
			index=tipo_actual_idx,
			help="Selecciona el tipo de propiedad a reformar"
		)
		
		tipo_inmueble = PropertyType(tipo_values[tipo_seleccionado_idx])
		
		# Metros cuadrados
		metros_cuadrados = st.number_input(
			"Superficie total (m²)",
			min_value=10.0,
			max_value=10000.0,
			value=float(proyecto_actual.metros_cuadrados),
			step=5.0,
			help="Superficie total del inmueble en metros cuadrados"
		)
		
		# FASE 2: Número de habitaciones
		num_habitaciones = st.number_input(
			"Número de habitaciones/salas (opcional)",
			min_value=0,
			max_value=50,
			value=proyecto_actual.num_habitaciones or 0,
			step=1,
			help="Número total de habitaciones, salas o espacios diferenciados"
		)
		
		# Estado actual
		estado_actual = st.selectbox(
			"Estado actual",
			["nuevo", "normal", "antiguo", "ruina"],
			index=["nuevo", "normal", "antiguo", "ruina"].index(proyecto_actual.estado_actual),
			help="Estado actual del inmueble (afecta al factor de dificultad)"
		)
	
	with col2:
		# Calidad general
		calidad_opciones = QualityLevel.get_choices()
		calidad_labels = [label for _, label in calidad_opciones]
		calidad_values = [value for value, _ in calidad_opciones]
		
		# Encontrar índice actual
		calidad_actual_idx = calidad_values.index(proyecto_actual.calidad_general.value)
		
		calidad_idx = st.selectbox(
			"Calidad general",
			range(len(calidad_labels)),
			format_func=lambda i: calidad_labels[i],
			index=calidad_actual_idx,
			help="Nivel de calidad de los materiales y acabados"
		)
		
		calidad_general = QualityLevel(calidad_values[calidad_idx])
		
		# Ubicación
		ubicacion = st.text_input(
			"Ubicación",
			value=proyecto_actual.ubicacion or "",
			placeholder="Ej: Madrid, Barcelona, Valencia...",
			help="Ciudad o zona donde se ubica el inmueble"
		)
	
	# Descripción adicional
	descripcion = st.text_area(
		"Descripción adicional (opcional)",
		value=proyecto_actual.descripcion or "",
		placeholder="Detalles relevantes sobre el proyecto...",
		max_chars=1000,
		help="Información adicional que consideres relevante para el presupuesto"
	)
	
	# Info box sobre IVA
	st.info(
		"ℹ️ **IVA aplicable:** Todos los presupuestos aplican IVA general del 21% "
		"según normativa vigente."
	)
	
	col_btn1, col_btn2 = st.columns(2)
	
	with col_btn1:
		if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
			try:
				proyecto_actualizado = Project(
					tipo_inmueble=tipo_inmueble,
					metros_cuadrados=metros_cuadrados,
					num_habitaciones=num_habitaciones if num_habitaciones > 0 else None,
					calidad_general=calidad_general,
					estado_actual=estado_actual,
					descripcion=descripcion.strip() if descripcion else None,
					ubicacion=ubicacion.strip() if ubicacion else None
				)
				
				st.success("✅ Proyecto actualizado correctamente")
				return proyecto_actualizado
				
			except Exception as e:
				st.error(f"❌ Error al actualizar proyecto: {str(e)}")
				return None
	
	with col_btn2:
		if st.button("❌ Cancelar", use_container_width=True):
			st.info("Edición cancelada")
			return None
	
	return None