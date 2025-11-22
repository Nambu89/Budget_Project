"""
Calculator Agent - Agente calculador de precios.

Calcula los precios de las partidas y paquetes aplicando
todas las reglas de negocio (markup, redondeo, IVA).
"""

from typing import Optional
from crewai import Agent, LLM, Task
from loguru import logger

from ...config.settings import settings
from ...domain.enums import PropertyType, QualityLevel, WorkCategory
from ...domain.models import Budget, Project
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
CALCULATOR_SYSTEM_PROMPT = """
Eres un experto calculista de presupuestos de reformas en España. Tu trabajo es:

1. CALCULAR precios precisos basados en la base de datos de precios
2. APLICAR las reglas de negocio correctamente:
   - Markup del 15% a partidas individuales (no a paquetes)
   - Redondeo al alza del 5% sobre el total
   - IVA del 10% para vivienda habitual, 21% para el resto
3. OPTIMIZAR sugiriendo paquetes cuando sean más económicos
4. DESGLOSAR claramente todos los conceptos

Siempre muestra:
- Subtotal por categoría
- Descuentos aplicados
- Base imponible
- IVA
- Total final

Responde en español y sé preciso con los números.
"""


class CalculatorAgent:
    """
    Agente para cálculo de precios.
    
    Utiliza el PricingService y BudgetService para calcular
    todos los precios aplicando las reglas de negocio.
    
    Responsibilities:
    - Calcular precios de partidas
    - Aplicar markup a partidas individuales
    - Calcular paquetes (sin markup)
    - Aplicar redondeo al alza
    - Calcular IVA según tipo de inmueble
    - Sugerir optimizaciones
    """
    
    def __init__(self, budget_service: Optional[BudgetService] = None):
        """
        Inicializa el agente calculador.
        
        Args:
            budget_service: Servicio de presupuestos (opcional)
        """
        self.budget_service = budget_service or get_budget_service()
        
        # Crear LLM para Azure
        self.llm = get_azure_llm()
        
        # Crear agente CrewAI con Azure LLM
        self.agent = Agent(
            role="Especialista en Cálculo de Presupuestos",
            goal="Calcular precios precisos aplicando todas las reglas de negocio",
            backstory="""
            Soy un calculista experto con más de 15 años de experiencia
            en el sector de la construcción. Conozco todos los precios
            del mercado español y aplico las reglas comerciales para
            ofrecer presupuestos competitivos pero rentables.
            """,
            llm=self.llm,
            verbose=settings.debug,
            allow_delegation=False,
        )
        
        logger.info("✓ CalculatorAgent inicializado")
    
    def calcular_presupuesto(
        self,
        datos_proyecto: dict,
        partidas: list[dict],
        paquetes: list[str] = None,
    ) -> Budget:
        """
        Calcula el presupuesto completo.
        
        Args:
            datos_proyecto: Datos validados del proyecto
            partidas: Lista de partidas a incluir
            paquetes: Lista de paquetes a incluir
            
        Returns:
            Budget: Presupuesto calculado
        """
        logger.info("Calculando presupuesto...")
        
        # Crear presupuesto base
        presupuesto = self.budget_service.crear_presupuesto(
            tipo_inmueble=datos_proyecto["tipo_inmueble"],
            metros_cuadrados=datos_proyecto["metros_cuadrados"],
            calidad=datos_proyecto.get("calidad", QualityLevel.ESTANDAR),
            es_vivienda_habitual=datos_proyecto.get("es_vivienda_habitual", False),
            estado_actual=datos_proyecto.get("estado_actual", "normal"),
            ubicacion=datos_proyecto.get("ubicacion"),
            descripcion=datos_proyecto.get("descripcion"),
        )
        
        # Agregar partidas individuales (con markup)
        if partidas:
            self.budget_service.agregar_partidas_multiples(presupuesto, partidas)
        
        # Agregar paquetes (sin markup)
        if paquetes:
            for paquete in paquetes:
                self.budget_service.agregar_paquete(
                    presupuesto=presupuesto,
                    paquete=paquete,
                    calidad=datos_proyecto.get("calidad"),
                    metros=datos_proyecto["metros_cuadrados"],
                )
        
        logger.info(f"Presupuesto calculado: {presupuesto.num_partidas} partidas, "
                   f"subtotal: {presupuesto.subtotal}€")
        
        return presupuesto
    
    def calcular_con_comparativa(
        self,
        datos_proyecto: dict,
        partidas: list[dict],
        paquete_alternativo: str,
    ) -> dict:
        """
        Calcula el presupuesto y lo compara con un paquete alternativo.
        
        Args:
            datos_proyecto: Datos del proyecto
            partidas: Partidas individuales
            paquete_alternativo: Paquete para comparar
            
        Returns:
            dict: Presupuesto con comparativa
        """
        # Calcular con partidas individuales
        presupuesto_partidas = self.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=partidas,
            paquetes=None,
        )
        
        # Calcular con paquete
        presupuesto_paquete = self.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=None,
            paquetes=[paquete_alternativo],
        )
        
        # Comparar
        ahorro = presupuesto_partidas.total - presupuesto_paquete.total
        ahorro_porcentaje = (ahorro / presupuesto_partidas.total * 100) if presupuesto_partidas.total > 0 else 0
        
        return {
            "presupuesto_partidas": presupuesto_partidas,
            "presupuesto_paquete": presupuesto_paquete,
            "total_partidas": presupuesto_partidas.total,
            "total_paquete": presupuesto_paquete.total,
            "ahorro": round(ahorro, 2),
            "ahorro_porcentaje": round(ahorro_porcentaje, 1),
            "recomendacion": "paquete" if ahorro > 0 else "partidas",
            "mensaje_recomendacion": self._generar_mensaje_recomendacion(
                ahorro, ahorro_porcentaje, paquete_alternativo
            ),
        }
    
    def _generar_mensaje_recomendacion(
        self,
        ahorro: float,
        ahorro_porcentaje: float,
        paquete: str,
    ) -> str:
        """Genera mensaje de recomendación para el cliente."""
        if ahorro > 0:
            return (
                f"💡 ¡Puede ahorrar {ahorro:,.2f}€ ({ahorro_porcentaje:.1f}%) "
                f"eligiendo el {paquete.replace('_', ' ').title()}! "
                "Los paquetes incluyen todos los trabajos necesarios con "
                "materiales de la misma calidad."
            )
        else:
            return (
                "Las partidas individuales seleccionadas son la mejor opción "
                "para su proyecto. El paquete incluiría trabajos que no necesita."
            )
    
    def obtener_desglose_completo(self, presupuesto: Budget) -> dict:
        """
        Obtiene el desglose completo del presupuesto.
        
        Args:
            presupuesto: Presupuesto calculado
            
        Returns:
            dict: Desglose detallado
        """
        totales = self.budget_service.calcular_totales(presupuesto)
        
        return {
            "numero_presupuesto": presupuesto.numero_presupuesto,
            "fecha_emision": presupuesto.fecha_emision_str,
            "fecha_validez": presupuesto.fecha_validez_str,
            
            # Proyecto
            "proyecto": {
                "tipo": presupuesto.proyecto.tipo_inmueble_nombre,
                "metros": presupuesto.proyecto.metros_cuadrados,
                "calidad": presupuesto.proyecto.calidad_nombre,
                "vivienda_habitual": presupuesto.proyecto.es_vivienda_habitual,
            },
            
            # Partidas
            "num_partidas": presupuesto.num_partidas,
            "partidas": [
                {
                    "descripcion": p.descripcion,
                    "cantidad": p.cantidad,
                    "unidad": p.unidad,
                    "precio_unitario": p.precio_unitario,
                    "subtotal": p.subtotal,
                    "es_paquete": p.es_paquete,
                }
                for p in presupuesto.partidas
            ],
            
            # Resumen por categorías
            "resumen_categorias": presupuesto.resumen_por_categorias(),
            
            # Totales
            "subtotal": presupuesto.subtotal,
            "descuento_porcentaje": presupuesto.descuento_porcentaje,
            "descuento_importe": presupuesto.importe_descuento,
            "base_imponible_sin_redondeo": presupuesto.base_imponible,
            "redondeo_porcentaje": totales["redondeo_porcentaje"],
            "redondeo_importe": totales["redondeo_importe"],
            "base_imponible": totales["base_imponible"],
            "iva_porcentaje": totales["iva_porcentaje"],
            "iva_importe": totales["iva_importe"],
            "total": totales["total"],
            
            # Metadata
            "reglas_aplicadas": {
                "markup_partidas": f"{settings.markup_partidas_individuales}%",
                "redondeo_alza": f"{settings.redondeo_alza}%",
                "iva": f"{totales['iva_porcentaje']}%",
            },
        }
    
    def sugerir_optimizaciones(self, presupuesto: Budget) -> list[dict]:
        """
        Sugiere optimizaciones para el presupuesto.
        
        Args:
            presupuesto: Presupuesto a analizar
            
        Returns:
            list: Lista de sugerencias
        """
        sugerencias = []
        
        # Analizar si hay muchas partidas de la misma categoría
        resumen = presupuesto.resumen_por_categorias()
        
        # Si hay partidas de fontanería significativas, sugerir paquete baño
        if "Fontanería" in resumen and resumen["Fontanería"] > 1000:
            comparativa = self.budget_service.comparar_con_paquete(
                presupuesto, "bano_completo"
            )
            if comparativa["ahorro"] > 0:
                sugerencias.append({
                    "tipo": "paquete",
                    "paquete": "bano_completo",
                    "ahorro": comparativa["ahorro"],
                    "mensaje": f"Considere el paquete Baño Completo para ahorrar {comparativa['ahorro']:,.2f}€",
                })
        
        # Si hay partidas de cocina significativas, sugerir paquete cocina
        if "Cocina" in resumen and resumen["Cocina"] > 2000:
            comparativa = self.budget_service.comparar_con_paquete(
                presupuesto, "cocina_completa"
            )
            if comparativa["ahorro"] > 0:
                sugerencias.append({
                    "tipo": "paquete",
                    "paquete": "cocina_completa",
                    "ahorro": comparativa["ahorro"],
                    "mensaje": f"Considere el paquete Cocina Completa para ahorrar {comparativa['ahorro']:,.2f}€",
                })
        
        # Si el total es muy alto, sugerir cambiar a calidad básica
        if presupuesto.total > 50000:
            sugerencias.append({
                "tipo": "calidad",
                "mensaje": "Para presupuestos elevados, considere calidad Básica en algunas partidas",
            })
        
        # Si es IVA general, recordar vivienda habitual
        if presupuesto.proyecto.iva_aplicable == 21:
            if presupuesto.proyecto.tipo_inmueble.es_vivienda_habitual:
                sugerencias.append({
                    "tipo": "iva",
                    "mensaje": "Si es su vivienda habitual, marque la opción para aplicar IVA reducido (10%)",
                })
        
        return sugerencias
    
    def crear_task_calculo(self, datos: dict) -> Task:
        """
        Crea una Task de CrewAI para cálculo con análisis IA.
        
        Args:
            datos: Datos del presupuesto
            
        Returns:
            Task: Task de CrewAI
        """
        return Task(
            description=f"""
            Analiza el siguiente presupuesto de reforma y proporciona:
            
            Datos del proyecto:
            {datos.get('proyecto', {})}
            
            Partidas:
            {datos.get('partidas', [])}
            
            1. Verifica que los precios sean coherentes con el mercado español
            2. Sugiere optimizaciones si las hay
            3. Explica el desglose de forma clara para el cliente
            4. Indica si hay alguna partida que parezca cara o barata
            
            Responde de forma profesional pero cercana.
            """,
            agent=self.agent,
            expected_output="Análisis del presupuesto con recomendaciones",
        )