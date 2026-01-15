"""
Componente Results Display para Streamlit.

Muestra los resultados del presupuesto calculado
con desglose, totales y opciones de descarga.
"""

import streamlit as st
from typing import Optional
import base6

from src.domain.models import Budget
from src.domain.models.project import Project  # NUEVO IMPORT


def render_results(
	presupuesto: Budget,
	desglose: dict,
	sugerencias: list = None,
	estimaciones: dict = None,  # NUEVO parámetro FASE 
) -> None:
	"""
	Renderiza los resultados del presupuesto.
	
	Args:
		presupuesto: Presupuesto calculado
		desglose: Desglose detallado
		sugerencias: Lista de sugerencias de optimización
		estimaciones: Estimaciones inteligentes de IA (opcional)
	"""
	st.markdown("##  Resultados del Presupuesto")
	
	# Número y fecha
	col, col, col = st.columns()
	
	with col:
		st.metric(" Nº Presupuesto", presupuesto.numero_presupuesto)
	
	with col:
		st.metric(" Fecha", presupuesto.fecha_emision_str)
	
	with col:
		st.metric(" Válido hasta", presupuesto.fecha_validez_str)
	
	st.divider()
	
	# NUEVO FASE : Mostrar estimaciones IA si existen
	if estimaciones and presupuesto.proyecto.num_habitaciones:
		_render_estimaciones_ia_resumen(estimaciones, presupuesto.proyecto)
		st.divider()
	
	# Total destacado
	st.markdown(f"""
		<div class="total-display">
			 TOTAL: {presupuesto.total:,.f} €
			<br>
			<span style="font-size: 0.9rem; font-weight: normal;">
				(IVA {presupuesto.iva_porcentaje}% incluido)
			</span>
		</div>
	""", unsafe_allow_html=True)
	
	st.divider()
	
	# Desglose en columnas
	col, col = st.columns()
	
	with col:
		_render_desglose_partidas(presupuesto)
	
	with col:
		_render_desglose_totales(presupuesto, desglose)
	
	# Sugerencias de optimización
	if sugerencias:
		st.divider()
		_render_sugerencias(sugerencias)
	
	# Reglas aplicadas
	st.divider()
	_render_reglas_aplicadas(desglose)


def _render_estimaciones_ia_resumen(estimaciones: dict, proyecto: Project) -> None:
	"""
	Renderiza un resumen de las estimaciones IA.
	
	Args:
		estimaciones: Diccionario con estimaciones
		proyecto: Proyecto asociado
	"""
	st.markdown("###  Estimaciones Inteligentes Aplicadas")
	
	col, col, col, col = st.columns()
	
	with col:
		st.metric(
			label=" Habitaciones",
			value=f"{proyecto.num_habitaciones}",
			help="Habitaciones/salas del inmueble"
		)
	
	with col:
		st.metric(
			label=" Paredes",
			value=f"{estimaciones.get('m_paredes_estimado', 0):.f} m²",
			help="m² de paredes estimados"
		)
	
	with col:
		st.metric(
			label=" Rodapiés",
			value=f"{estimaciones.get('ml_rodapies_estimado', 0):.f} ml",
			help="Metros lineales estimados"
		)
	
	with col:
		st.metric(
			label=" Puertas",
			value=f"{estimaciones.get('num_puertas_estimado', 0)} ud",
			help="Puertas de paso estimadas"
		)
	
	# Mensaje de confianza
	metodo = estimaciones.get("metodo", "")
	if metodo == "llm":
		st.success(" Estimaciones calculadas con IA de alta precisión")
	else:
		st.info(" Estimaciones calculadas con fórmulas heurísticas")


def _render_desglose_partidas(presupuesto: Budget) -> None:
	"""Renderiza el desglose de partidas."""
	st.markdown("###  Desglose de partidas")
	
	if not presupuesto.partidas:
		st.info("No hay partidas en este presupuesto")
		return
	
	# Tabla de partidas
	for i, partida in enumerate(presupuesto.partidas, ):
		tipo_badge = "" if partida.es_paquete else ""
		
		with st.expander(
			f"{tipo_badge} {partida.descripcion[:0]}... - **{partida.subtotal:,.f}€**",
			expanded=False,
		):
			col, col = st.columns()
			
			with col:
				st.markdown(f"**Descripción:** {partida.descripcion}")
				st.markdown(f"**Categoría:** {partida.categoria_nombre}")
				st.markdown(f"**Calidad:** {partida.calidad_nombre}")
			
			with col:
				st.markdown(f"**Cantidad:** {partida.cantidad} {partida.unidad}")
				st.markdown(f"**Precio unitario:** {partida.precio_unitario:,.f}€/{partida.unidad}")
				st.markdown(f"**Subtotal:** {partida.subtotal:,.f}€")
			
			if partida.es_paquete:
				st.info(" Este es un paquete completo (sin markup)")
			else:
				st.warning(" Partida individual (+% markup aplicado)")
	
	# Resumen por categorías
	st.markdown("####  Por categoría")
	
	resumen = presupuesto.resumen_por_categorias()
	
	for categoria, importe in resumen.items():
		porcentaje = (importe / presupuesto.subtotal * 00) if presupuesto.subtotal > 0 else 0
		
		col, col, col = st.columns([, , ])
		
		with col:
			st.markdown(f"**{categoria}**")
		
		with col:
			st.markdown(f"{importe:,.f}€")
		
		with col:
			st.progress(porcentaje / 00)


def _render_desglose_totales(presupuesto: Budget, desglose: dict) -> None:
	"""Renderiza el desglose de totales."""
	st.markdown("###  Desglose económico")
	
	# Tabla de totales
	datos_totales = [
		("Subtotal (sin IVA)", presupuesto.subtotal),
	]
	
	if presupuesto.descuento_porcentaje > 0:
		datos_totales.append((
			f"Descuento ({presupuesto.descuento_porcentaje:.f}%)",
			-presupuesto.importe_descuento,
		))
	
	datos_totales.append(("Base imponible", presupuesto.base_imponible))
	
	# Redondeo al alza
	if "redondeo_importe" in desglose and desglose["redondeo_importe"] > 0:
		datos_totales.append((
			f"Redondeo ({desglose['redondeo_porcentaje']}%)",
			desglose["redondeo_importe"],
		))
		datos_totales.append(("Base con redondeo", desglose["base_imponible"]))
	
	datos_totales.append((
		"IVA (%)",
		desglose.get("iva_importe", presupuesto.importe_iva),
	))
	
	# Mostrar tabla
	for concepto, importe in datos_totales:
		col, col = st.columns([, ])
		
		with col:
			st.markdown(concepto)
		
		with col:
			if importe < 0:
				st.markdown(f"<span style='color: #ef;'>-{abs(importe):,.f}€</span>", 
						   unsafe_allow_html=True)
			else:
				st.markdown(f"{importe:,.f}€")
	
	st.divider()
	
	# Total final
	total_final = desglose.get("total", presupuesto.total)
	
	col, col = st.columns([, ])
	
	with col:
		st.markdown("### **TOTAL**")
	
	with col:
		st.markdown(f"### **{total_final:,.f}€**")
	
	# Info IVA
	st.info(" Se ha aplicado IVA general del % según normativa vigente")


def _render_sugerencias(sugerencias: list) -> None:
	"""Renderiza las sugerencias de optimización."""
	st.markdown("###  Sugerencias de ahorro")
	
	for sug in sugerencias:
		if sug.get("tipo") == "paquete":
			st.success(f"""
				**¿Sabías que puedes ahorrar {sug['ahorro']:,.f}€?**
				
				{sug['mensaje']}
			""")
		else:
			st.info(sug["mensaje"])


def _render_reglas_aplicadas(desglose: dict) -> None:
	"""Renderiza las reglas de negocio aplicadas."""
	with st.expander(" Reglas aplicadas a este presupuesto"):
		reglas = desglose.get("reglas_aplicadas", {})
		
		st.markdown(f"""
		- **Markup partidas individuales:** {reglas.get('markup_partidas', '%')}
		- **Redondeo:** {reglas.get('redondeo_alza', '%')}
		- **IVA aplicado:** {reglas.get('iva', '%')}
		
		*Los paquetes completos NO tienen markup, por eso son más económicos.*
		""")


def render_download_section(
	presupuesto: Budget,
	pdf_bytes: Optional[bytes] = None,
	resumen_texto: Optional[str] = None,
) -> None:
	"""
	Renderiza la sección de descargas.
	
	Args:
		presupuesto: Presupuesto
		pdf_bytes: PDF en bytes (opcional)
		resumen_texto: Resumen en texto (opcional)
	"""
	st.markdown("###  Descargar presupuesto")
	
	if pdf_bytes:
		st.download_button(
			label=" Descargar PDF",
			data=pdf_bytes,
			file_name=f"presupuesto_{presupuesto.numero_presupuesto}.pdf",
			mime="application/pdf",
			type="primary",
			use_container_width=True,
		)
	else:
		st.button(
			" Generar PDF",
			disabled=True,
			use_container_width=True,
		)


def render_empty_results() -> None:
	"""Renderiza mensaje cuando no hay resultados."""
	st.info("""
		###  Aquí aparecerá tu presupuesto
		
		Completa los pasos anteriores para generar tu presupuesto:
		
		.  Selecciona el tipo de inmueble
		.  Indica la superficie
		.  Elige los trabajos a realizar
		.  ¡Genera tu presupuesto!
	""")


def render_comparison(comparativa: dict) -> None:
	"""
	Renderiza una comparativa entre opciones.
	
	Args:
		comparativa: Datos de la comparativa
	"""
	st.markdown("###  Comparativa de opciones")
	
	col, col = st.columns()
	
	with col:
		st.markdown("####  Partidas individuales")
		st.metric(
			"Total",
			f"{comparativa['total_partidas']:,.f}€",
		)
	
	with col:
		st.markdown("####  Paquete completo")
		st.metric(
			"Total",
			f"{comparativa['total_paquete']:,.f}€",
			delta=f"-{comparativa['ahorro']:,.f}€" if comparativa['ahorro'] > 0 else None,
			delta_color="inverse",
		)
	
	if comparativa["ahorro"] > 0:
		st.success(f"""
			 **{comparativa['mensaje_recomendacion']}**
		""")
	else:
		st.info(comparativa["mensaje_recomendacion"])