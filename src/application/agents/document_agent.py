"""
Document Agent - Agente generador de documentos.

Genera el presupuesto final en diferentes formatos:
PDF profesional, resumen texto, etc.

MIGRADO A: Microsoft Agent Framework (sin CrewAI)
"""

from typing import Optional
from agent_framework import ChatAgent
from loguru import logger

from ...config.settings import settings
from ...config.pricing_data import DISCLAIMERS
from ...domain.models import Budget, Customer
from ...infrastructure.pdf import generar_pdf_presupuesto
from ...infrastructure.llm import get_chat_client
from ..services import BudgetService, get_budget_service
from .prompts import DOCUMENT_INSTRUCTIONS


# System prompt del agente
DOCUMENT_SYSTEM_PROMPT = """
Eres un experto en documentación profesional de presupuestos. Tu trabajo es:

1. GENERAR documentos claros y profesionales
2. INCLUIR todos los disclaimers legales necesarios
3. FORMATEAR la información de forma atractiva
4. PERSONALIZAR según los datos del cliente

El documento debe:
- Ser fácil de leer y entender
- Tener un aspecto profesional
- Incluir toda la información legal
- Destacar los totales de forma clara
- Mostrar IVA general del 21% para todos los inmuebles

Responde en español y con formato profesional.
"""


class DocumentAgent:
	"""
	Agente para generación de documentos.
	
	Genera presupuestos en diferentes formatos,
	incluyendo PDF profesional con todos los requisitos legales.
	
	Responsibilities:
	- Generar PDF del presupuesto
	- Crear resúmenes en texto
	- Incluir disclaimers legales
	- Personalizar con datos del cliente
	"""
	
	def __init__(self, budget_service: Optional[BudgetService] = None):
		"""
		Inicializa el agente de documentos.
		
		Args:
			budget_service: Servicio de presupuestos (opcional)
		"""
		self.budget_service = budget_service or get_budget_service()
		
		# Crear agente con Microsoft Agent Framework
		chat_client = get_chat_client()
		self.agent = ChatAgent(
			name="Especialista en Documentación",
			chat_client=chat_client,
			instructions=DOCUMENT_INSTRUCTIONS,
		)
		
		logger.info("✓ DocumentAgent inicializado (Microsoft Agent Framework)")
	
	def generar_pdf(
		self,
		presupuesto: Budget,
		output_path: Optional[str] = None,
	) -> bytes:
		"""
		Genera el PDF del presupuesto.
		
		Args:
			presupuesto: Presupuesto a documentar
			output_path: Ruta de salida (opcional)
			
		Returns:
			bytes: Contenido del PDF
		"""
		logger.info(f"Generando PDF para presupuesto {presupuesto.numero_presupuesto}...")
		
		pdf_bytes = self.budget_service.generar_pdf(
			presupuesto=presupuesto,
			output_path=output_path,
		)
		
		logger.info(f"PDF generado: {len(pdf_bytes)} bytes")
		return pdf_bytes
	
	def generar_resumen_texto(self, presupuesto: Budget) -> str:
		"""
		Genera un resumen en texto plano del presupuesto.
		
		Args:
			presupuesto: Presupuesto a resumir
			
		Returns:
			str: Resumen en texto
		"""
		# Manejar si resumen_texto es método o propiedad
		resumen_attr = getattr(presupuesto, 'resumen_texto', None)
		if callable(resumen_attr):
			return resumen_attr()
		elif resumen_attr is not None:
			return resumen_attr
		else:
			# Fallback: generar resumen básico
			return f"Presupuesto {presupuesto.numero_presupuesto} - Total: {presupuesto.total}€"
	
	def generar_resumen_detallado(self, presupuesto: Budget) -> str:
		"""
		Genera un resumen detallado con todas las secciones.
		
		Args:
			presupuesto: Presupuesto
			
		Returns:
			str: Resumen detallado
		"""
		lineas = []
		
		# Cabecera
		lineas.extend([
			"=" * 60,
			f"PRESUPUESTO DE REFORMA - {presupuesto.numero_presupuesto}",
			"=" * 60,
			"",
		])
		
		# Datos del presupuesto
		lineas.extend([
			f"📅 Fecha de emisión: {presupuesto.fecha_emision_str}",
			f"📅 Válido hasta: {presupuesto.fecha_validez_str}",
			"",
		])
		
		# Datos del proyecto
		lineas.extend([
			"─" * 40,
			"📋 DATOS DEL PROYECTO",
			"─" * 40,
			f"  Tipo: {presupuesto.proyecto.tipo_inmueble_nombre}",
			f"  Superficie: {presupuesto.proyecto.metros_cuadrados:.2f} m²",
			f"  Calidad: {presupuesto.proyecto.calidad_nombre}",
			f"  Estado: {presupuesto.proyecto.estado_actual.capitalize()}",
			f"  IVA aplicable: 21% (IVA general)",
			"",
		])
		
		# Datos del cliente
		if presupuesto.tiene_cliente:
			cliente = presupuesto.cliente
			lineas.extend([
				"─" * 40,
				"👤 DATOS DEL CLIENTE",
				"─" * 40,
				f"  Nombre: {cliente.nombre}",
				f"  Email: {cliente.email}",
				f"  Teléfono: {cliente.telefono_formateado}",
			])
			if cliente.direccion_obra:
				lineas.append(f"  Dirección: {cliente.direccion_obra}")
			lineas.append("")
		
		# Desglose de partidas
		lineas.extend([
			"─" * 40,
			"📊 DESGLOSE DE PARTIDAS",
			"─" * 40,
		])
		
		if presupuesto.partidas:
			for i, p in enumerate(presupuesto.partidas, 1):
				tipo = "[PKG]" if p.es_paquete else "[IND]"
				lineas.append(
					f"  {i}. {tipo} {p.descripcion[:40]}..."
					if len(p.descripcion) > 40 
					else f"  {i}. {tipo} {p.descripcion}"
				)
				lineas.append(
					f"      {p.cantidad:.2f} {p.unidad} x {p.precio_unitario:.2f}€ = {p.subtotal:.2f}€"
				)
		else:
			lineas.append("  (Sin partidas)")
		
		lineas.append("")
		
		# Resumen por categorías
		resumen = presupuesto.resumen_por_categorias()
		if resumen:
			lineas.extend([
				"─" * 40,
				"📈 RESUMEN POR CATEGORÍA",
				"─" * 40,
			])
			for cat, importe in resumen.items():
				lineas.append(f"  {cat}: {importe:,.2f}€")
			lineas.append("")
		
		# Totales
		lineas.extend([
			"─" * 40,
			"💰 TOTALES",
			"─" * 40,
			f"  Subtotal: {presupuesto.subtotal:,.2f}€",
		])
		
		if presupuesto.descuento_porcentaje > 0:
			lineas.append(
				f"  Descuento ({presupuesto.descuento_porcentaje:.1f}%): "
				f"-{presupuesto.importe_descuento:,.2f}€"
			)
		
		lineas.extend([
			f"  Base imponible: {presupuesto.base_imponible:,.2f}€",
			f"  IVA (21%): {presupuesto.importe_iva:,.2f}€",
			"",
			f"  {'─' * 30}",
			f"  TOTAL: {presupuesto.total:,.2f}€",
			"",
		])
		
		# Disclaimers resumidos
		lineas.extend([
			"─" * 40,
			"⚠️ CONDICIONES",
			"─" * 40,
			"  • Este presupuesto es una estimación orientativa",
			"  • Precios sujetos a visita técnica",
			f"  • Válido {presupuesto.dias_validez} días desde emisión",
			"  • IVA general del 21% incluido",
			"",
			"=" * 60,
		])
		
		return "\n".join(lineas)
	
	def generar_email_presupuesto(
		self,
		presupuesto: Budget,
		incluir_pdf: bool = True,
	) -> dict:
		"""
		Genera el contenido para enviar el presupuesto por email.
		
		Args:
			presupuesto: Presupuesto
			incluir_pdf: Si incluir el PDF como adjunto
			
		Returns:
			dict: Contenido del email (asunto, cuerpo, adjuntos)
		"""
		nombre_cliente = presupuesto.cliente.nombre if presupuesto.tiene_cliente else "Cliente"
		
		asunto = f"Presupuesto de reforma {presupuesto.numero_presupuesto} - {settings.empresa_nombre}"
		
		cuerpo = f"""
Estimado/a {nombre_cliente},

Adjunto le enviamos el presupuesto solicitado para su proyecto de reforma.

📋 Resumen del presupuesto:
- Número: {presupuesto.numero_presupuesto}
- Tipo de obra: {presupuesto.proyecto.tipo_inmueble_nombre}
- Superficie: {presupuesto.proyecto.metros_cuadrados:.2f} m²
- Total (IVA incluido): {presupuesto.total:,.2f}€

📅 Este presupuesto tiene una validez de {presupuesto.dias_validez} días.

Para cualquier consulta o para concertar una visita técnica, 
no dude en contactarnos:

📞 {settings.empresa_telefono}
✉️ {settings.empresa_email}
🌐 {settings.empresa_web}

Quedamos a su disposición.

Un cordial saludo,
{settings.empresa_nombre}

---
Este presupuesto es una estimación orientativa. 
El presupuesto definitivo se confirmará tras visita técnica.
"""
		
		resultado = {
			"asunto": asunto,
			"cuerpo": cuerpo.strip(),
			"adjuntos": [],
		}
		
		if incluir_pdf:
			pdf_bytes = self.generar_pdf(presupuesto)
			resultado["adjuntos"].append({
				"nombre": f"presupuesto_{presupuesto.numero_presupuesto}.pdf",
				"contenido": pdf_bytes,
				"tipo": "application/pdf",
			})
		
		return resultado
	
	def generar_mensaje_cliente(self, presupuesto: Budget) -> str:
		"""
		Genera un mensaje amigable para mostrar al cliente en la UI.
		
		Args:
			presupuesto: Presupuesto generado
			
		Returns:
			str: Mensaje para el cliente
		"""
		mensaje = f"""
## ✅ ¡Presupuesto generado!

Hemos preparado su presupuesto de reforma:

| Concepto | Valor |
|----------|-------|
| **Número** | {presupuesto.numero_presupuesto} |
| **Tipo de obra** | {presupuesto.proyecto.tipo_inmueble.icono} {presupuesto.proyecto.tipo_inmueble_nombre} |
| **Superficie** | {presupuesto.proyecto.metros_cuadrados:.2f} m² |
| **Calidad** | {presupuesto.proyecto.calidad_general.icono} {presupuesto.proyecto.calidad_nombre} |
| **Partidas** | {presupuesto.num_partidas} |

### 💰 Resumen económico

| Concepto | Importe |
|----------|---------|
| Subtotal | {presupuesto.subtotal:,.2f} € |
| IVA (21%) | {presupuesto.importe_iva:,.2f} € |
| **TOTAL** | **{presupuesto.total:,.2f} €** |

📅 **Validez:** {presupuesto.dias_validez} días (hasta {presupuesto.fecha_validez_str})

---

⚠️ *Este presupuesto es una estimación orientativa. 
El precio definitivo se confirmará tras visita técnica.*

¿Desea descargar el presupuesto en PDF?
"""
		return mensaje.strip()