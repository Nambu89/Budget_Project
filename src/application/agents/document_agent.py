"""
Document Agent - Agente generador de documentos.

Genera el presupuesto final en diferentes formatos:
PDF profesional, resumen texto, etc.
"""

from typing import Optional
from crewai import Agent, LLM, Task
from loguru import logger

from ...config.settings import settings
from ...config.pricing_data import DISCLAIMERS
from ...domain.models import Budget, Customer
from ...infrastructure.pdf import generar_pdf_presupuesto
from ..services import BudgetService, get_budget_service


def get_azure_llm() -> LLM:
    """
    Crea un LLM configurado para Azure AI Foundry.
    
    Returns:
        LLM: Instancia de LLM para CrewAI
    """
    model_name = f"azure/{settings.azure_openai_deployment_name}"
    
    return LLM(
        model=model_name,
        api_key=settings.azure_openai_api_key,
        base_url=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )


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
        
        # Crear LLM para Azure
        self.llm = get_azure_llm()
        
        # Crear agente CrewAI con Azure LLM
        self.agent = Agent(
            role="Especialista en Documentación",
            goal="Generar documentos profesionales y legalmente correctos",
            backstory="""
            Soy especialista en documentación comercial con experiencia
            en el sector de la construcción. Me aseguro de que cada
            presupuesto sea claro, profesional y cumpla con todos
            los requisitos legales.
            """,
            llm=self.llm,
            verbose=settings.debug,
            allow_delegation=False,
        )
        
        logger.info("✓ DocumentAgent inicializado")
    
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
            f"  Vivienda habitual: {'Sí' if presupuesto.proyecto.es_vivienda_habitual else 'No'}",
            f"  IVA aplicable: {presupuesto.proyecto.iva_aplicable}%",
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
            f"  IVA ({presupuesto.iva_porcentaje}%): {presupuesto.importe_iva:,.2f}€",
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
            "  • IVA no incluido en precios unitarios",
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
• Número: {presupuesto.numero_presupuesto}
• Tipo de obra: {presupuesto.proyecto.tipo_inmueble_nombre}
• Superficie: {presupuesto.proyecto.metros_cuadrados:.2f} m²
• Total (IVA incluido): {presupuesto.total:,.2f}€

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
| IVA ({presupuesto.iva_porcentaje}%) | {presupuesto.importe_iva:,.2f} € |
| **TOTAL** | **{presupuesto.total:,.2f} €** |

📅 **Validez:** {presupuesto.dias_validez} días (hasta {presupuesto.fecha_validez_str})

---

⚠️ *Este presupuesto es una estimación orientativa. 
El precio definitivo se confirmará tras visita técnica.*

¿Desea descargar el presupuesto en PDF?
"""
        return mensaje.strip()
    
    def asignar_cliente_y_generar(
        self,
        presupuesto: Budget,
        nombre: str,
        email: str,
        telefono: str,
        direccion_obra: Optional[str] = None,
        generar_pdf: bool = True,
    ) -> dict:
        """
        Asigna cliente al presupuesto y genera documentos.
        
        Args:
            presupuesto: Presupuesto
            nombre: Nombre del cliente
            email: Email
            telefono: Teléfono
            direccion_obra: Dirección
            generar_pdf: Si generar PDF
            
        Returns:
            dict: Resultado con documentos generados
        """
        # Asignar cliente
        self.budget_service.asignar_cliente(
            presupuesto=presupuesto,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion_obra=direccion_obra,
        )
        
        resultado = {
            "presupuesto": presupuesto,
            "resumen_texto": self.generar_resumen_texto(presupuesto),
            "mensaje_cliente": self.generar_mensaje_cliente(presupuesto),
            "pdf_bytes": None,
        }
        
        if generar_pdf:
            resultado["pdf_bytes"] = self.generar_pdf(presupuesto)
        
        logger.info(f"Documentos generados para {nombre}")
        return resultado
    
    def crear_task_documento(self, presupuesto: Budget) -> Task:
        """
        Crea una Task de CrewAI para personalización del documento.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            Task: Task de CrewAI
        """
        datos_presupuesto = presupuesto.to_dict_pdf()
        
        return Task(
            description=f"""
            Revisa el siguiente presupuesto y genera un mensaje personalizado
            para el cliente:
            
            {datos_presupuesto}
            
            1. Destaca los puntos fuertes del presupuesto
            2. Explica brevemente qué incluye
            3. Menciona la validez y próximos pasos
            4. Usa un tono profesional pero cercano
            
            El mensaje debe ser breve (máximo 200 palabras) y atractivo.
            """,
            agent=self.agent,
            expected_output="Mensaje personalizado para el cliente",
        )