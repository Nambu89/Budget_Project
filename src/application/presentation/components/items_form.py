"""
Componente de formulario para añadir partidas al presupuesto.
"""

import streamlit as st
from typing import Optional

from ....domain.models.budget_item import BudgetItem
from ....domain.enums.work_category import WorkCategory
from ....domain.enums.quality_level import QualityLevel
from ....config.pricing_data import PRICING_DATA


def render_add_item_form(calidad_proyecto: QualityLevel) -> Optional[BudgetItem]:
	"""
	Renderiza formulario para añadir una partida.
	
	Args:
		calidad_proyecto: Calidad por defecto del proyecto
		
	Returns:
		BudgetItem si se completa el formulario, None en caso contrario
	"""
	st.subheader(" Añadir Partida")
	
	# Selector de categoría
	categorias = list(WorkCategory)
	categoria_nombres = [cat.display_name for cat in categorias]
	
	categoria_idx = st.selectbox(
		"Categoría",
		range(len(categorias)),
		format_func=lambda i: f"{categorias[i].icono} {categoria_nombres[i]}",
		help="Selecciona la categoría de trabajo"
	)
	
	categoria_seleccionada = categorias[categoria_idx]
	
	# Filtrar partidas por categoría
	partidas_categoria = {
		codigo: data for codigo, data in PRICING_DATA.items()
		if data.get("categoria") == categoria_seleccionada.value
	}
	
	if not partidas_categoria:
		st.warning(f"No hay partidas disponibles para la categoría '{categoria_seleccionada.display_name}'")
		return None
	
	# Selector de partida
	partida_codigos = list(partidas_categoria.keys())
	partida_nombres = [partidas_categoria[cod].get("nombre", cod) for cod in partida_codigos]
	
	partida_idx = st.selectbox(
		"Partida",
		range(len(partida_codigos)),
		format_func=lambda i: partida_nombres[i],
		help="Selecciona el tipo de trabajo específico"
	)
	
	codigo_seleccionado = partida_codigos[partida_idx]
	partida_data = partidas_categoria[codigo_seleccionado]
	
	# Mostrar descripción de la partida con aclaraciones
	descripcion_partida = partida_data.get("descripcion", "")
	st.info(f" **Descripción:** {descripcion_partida}")
	
	# Inputs de cantidad y calidad
	col1, col2 = st.columns(2)
	
	with col1:
		unidad = partida_data.get("unidad", "ud")
		
		# Personalizar el label según la unidad
		if unidad == "m²":
			label_cantidad = "Cantidad (m² de superficie)"
			help_text = "Introduce los metros cuadrados de superficie a trabajar (ancho × alto de cada área)"
		elif unidad == "ml":
			label_cantidad = "Cantidad (metros lineales)"
			help_text = "Introduce los metros lineales totales del perímetro"
		else:
			label_cantidad = f"Cantidad ({unidad})"
			help_text = f"Introduce la cantidad en {unidad}"
		
		cantidad = st.number_input(
			label_cantidad,
			min_value=0.0,
			max_value=10000.0,
			value=1.0,
			step=0.5 if unidad in ["m²", "ml"] else 1.0,
			help=help_text
		)
	
	with col1:
		# Calidad de la partida
		calidad_opciones = QualityLevel.get_choices()
		calidad_labels = [label for _, label in calidad_opciones]
		calidad_values = [value for value, _ in calidad_opciones]
		
		# Índice de la calidad del proyecto como default
		calidad_default_idx = calidad_values.index(calidad_proyecto.value)
		
		calidad_idx = st.selectbox(
			"Calidad",
			range(len(calidad_labels)),
			format_func=lambda i: calidad_labels[i],
			index=calidad_default_idx,
			help="Nivel de calidad de esta partida específica"
		)
		
		calidad = QualityLevel(calidad_values[calidad_idx])
	
	# Mostrar precio unitario
	precios = partida_data.get("precios", {})
	precio_unitario = precios.get(calidad.value, 0.0)
	
	st.metric(
		label=f"Precio unitario ({unidad})",
		value=f"{precio_unitario:.2f} €",
		help=f"Precio por {unidad} con calidad {calidad.display_name}"
	)
	
	# Calcular subtotal
	subtotal = cantidad * precio_unitario
	st.metric(
		label="Subtotal partida",
		value=f"{subtotal:.2f} €",
		delta=None
	)
	
	# Notas opcionales
	notas = st.text_area(
		"Notas (opcional)",
		placeholder="Detalles adicionales sobre esta partida...",
		max_chars=500,
		help="Información adicional que quieras incluir en el presupuesto"
	)
	
	# Botón de añadir
	if st.button(" Añadir al presupuesto", type="primary", use_container_width=True):
		try:
			partida = BudgetItem(
				codigo=codigo_seleccionado,
				descripcion=partida_data.get("nombre", ""),
				cantidad=cantidad,
				unidad=unidad,
				precio_unitario=precio_unitario,
				categoria=categoria_seleccionada,
				calidad=calidad,
				notas=notas.strip() if notas else None
			)
			
			st.success(f" Partida '{partida.descripcion}' añadida correctamente")
			return partida
			
		except Exception as e:
			st.error(f" Error al crear partida: {str(e)}")
			return None
	
	return None


def render_items_list(partidas: list[BudgetItem]) -> None:
	"""
	Muestra la lista de partidas añadidas al presupuesto.
	
	Args:
		partidas: Lista de partidas del presupuesto
	"""
	if not partidas:
		st.info(" No hay partidas añadidas. Añade la primera partida arriba.")
		return
	
	st.subheader(f" Partidas del Presupuesto ({len(partidas)})")
	
	# Calcular totales
	subtotal_total = sum(p.subtotal for p in partidas)
	
	# Tabla de partidas
	for idx, partida in enumerate(partidas):
		with st.expander(
			f"{partida.categoria.icono} {partida.descripcion} - {partida.subtotal:.2f} €",
			expanded=False
		):
			col, col, col = st.columns([1, 2, 1])
			
			with col1:
				st.write(f"**Cantidad:** {partida.cantidad} {partida.unidad}")
				st.write(f"**Precio unitario:** {partida.precio_unitario:.2f} €/{partida.unidad}")
			
			with col1:
				st.write(f"**Calidad:** {partida.calidad.display_name}")
				st.write(f"**Categoría:** {partida.categoria.display_name}")
			
			with col1:
				if st.button(" Eliminar", key=f"delete_{idx}", use_container_width=True):
					st.session_state[f"delete_item_{idx}"] = True
					st.rerun()
			
			if partida.notas:
				st.write(f"**Notas:** {partida.notas}")
	
	# Mostrar subtotal
	st.markdown("---")
	col, col = st.columns([1, 1])
	with col1:
		st.metric(
			label="Subtotal",
			value=f"{subtotal_total:.2f} €",
			help="Suma de todas las partidas (sin IVA ni descuentos)"
		)


def render_quick_add_common_items(calidad_proyecto: QualityLevel) -> Optional[list[BudgetItem]]:
	"""
	Renderiza selector rápido de partidas comunes.
	
	Args:
		calidad_proyecto: Calidad por defecto del proyecto
		
	Returns:
		Lista de BudgetItems o None
	"""
	st.subheader(" Añadir Partidas Comunes")
	
	# Partidas más comunes por categoría
	partidas_comunes = {
		"Pintura completa": "pintura",
		"Alicatado baño": "alicatado_paredes",
		"Suelo laminado": "suelo_laminado",
		"Puertas de paso": "puerta_paso",
		"Rodapiés": "rodapie",
	}
	
	col1, col2 = st.columns(2)
	
	partidas_seleccionadas = []
	
	for idx, (nombre, codigo) in enumerate(partidas_comunes.items()):
		col = col1 if idx % 2 == 0 else col2
		
		with col1:
			if st.button(f" {nombre}", key=f"quick_{codigo}", use_container_width=True):
				# Obtener datos de la partida
				if codigo in PRICING_DATA:
					partida_data = PRICING_DATA[codigo]
					
					# Valores por defecto
					cantidad_default = 10.0 if partida_data.get("unidad") == "m²" else 1.0
					precio = partida_data.get("precios", {}).get(calidad_proyecto.value, 0.0)
					
					partida = BudgetItem(
						codigo=codigo,
						descripcion=partida_data.get("nombre", nombre),
						cantidad=cantidad_default,
						unidad=partida_data.get("unidad", "ud"),
						precio_unitario=precio,
						categoria=WorkCategory(partida_data.get("categoria", "otros")),
						calidad=calidad_proyecto,
						notas="Añadida desde acceso rápido"
					)
					
					partidas_seleccionadas.append(partida)
					st.success(f" {nombre} añadida")
	
	return partidas_seleccionadas if partidas_seleccionadas else None