"""
Budget Crew - Orquestación de agentes.

Coordina los tres agentes (DataCollector, Calculator, Document)
para generar presupuestos completos de forma automatizada.
"""

from typing import Optional
from crewai import Crew, Process
from loguru import logger

from ...config.settings import settings
from ...domain.models import Budget
from ..agents.data_collector_agent import DataCollectorAgent
from ..agents.calculator_agent import CalculatorAgent
from ..agents.document_agent import DocumentAgent


class BudgetCrew:
    """
    Crew para generación de presupuestos.
    
    Orquesta el flujo completo:
    1. DataCollectorAgent: Valida y estructura datos
    2. CalculatorAgent: Calcula precios y totales
    3. DocumentAgent: Genera documentos finales
    
    Puede ejecutarse de forma secuencial o usar CrewAI
    para tareas que requieran análisis con IA.
    """
    
    def __init__(self):
        """Inicializa el crew con sus agentes."""
        self.data_collector = DataCollectorAgent()
        self.calculator = CalculatorAgent()
        self.document_agent = DocumentAgent()
        
        # Crear Crew de CrewAI para tareas con IA
        self.crew = Crew(
            agents=[
                self.data_collector.agent,
                self.calculator.agent,
                self.document_agent.agent,
            ],
            process=Process.sequential,
            verbose=settings.debug,
        )
        
        logger.info("✓ BudgetCrew inicializado con 3 agentes")
    
    def procesar_presupuesto(
        self,
        datos_formulario: dict,
        datos_cliente: Optional[dict] = None,
        generar_pdf: bool = True,
    ) -> dict:
        """
        Procesa un presupuesto completo de principio a fin.
        
        Este es el método principal que ejecuta todo el flujo:
        1. Validar datos del formulario
        2. Calcular presupuesto
        3. Asignar cliente (si se proporcionan datos)
        4. Generar documentos
        
        Args:
            datos_formulario: Datos del formulario del usuario
            datos_cliente: Datos del cliente (opcional)
            generar_pdf: Si generar PDF al final
            
        Returns:
            dict: Resultado completo del proceso
        """
        logger.info("=" * 50)
        logger.info("Iniciando procesamiento de presupuesto...")
        logger.info("=" * 50)
        
        resultado = {
            "exito": False,
            "presupuesto": None,
            "desglose": None,
            "sugerencias": [],
            "mensaje_cliente": None,
            "pdf_bytes": None,
            "errores": [],
            "warnings": [],
        }
        
        try:
            # ==========================================
            # Fase 1: Recolección y validación de datos
            # ==========================================
            logger.info("📋 Fase 1: Validando datos...")
            
            datos_validados = self.data_collector.procesar_formulario(datos_formulario)
            
            if not datos_validados["exito"]:
                resultado["errores"] = datos_validados["errores"]
                resultado["warnings"] = datos_validados["warnings"]
                logger.error(f"Validación fallida: {datos_validados['errores']}")
                return resultado
            
            resultado["warnings"].extend(datos_validados["warnings"])
            logger.info("✓ Datos validados correctamente")
            
            # ==========================================
            # Fase 2: Cálculo del presupuesto
            # ==========================================
            logger.info("🧮 Fase 2: Calculando presupuesto...")
            
            presupuesto = self.calculator.calcular_presupuesto(
                datos_proyecto=datos_validados["proyecto"],
                partidas=datos_validados["partidas"],
                paquetes=datos_validados.get("paquetes"),
            )
            
            resultado["presupuesto"] = presupuesto
            resultado["desglose"] = self.calculator.obtener_desglose_completo(presupuesto)
            resultado["sugerencias"] = self.calculator.sugerir_optimizaciones(presupuesto)
            
            logger.info(f"✓ Presupuesto calculado: {presupuesto.total:,.2f}€")
            
            # ==========================================
            # Fase 3: Asignación de cliente (opcional)
            # ==========================================
            if datos_cliente:
                logger.info("👤 Fase 3: Asignando cliente...")
                
                self.document_agent.budget_service.asignar_cliente(
                    presupuesto=presupuesto,
                    nombre=datos_cliente["nombre"],
                    email=datos_cliente["email"],
                    telefono=datos_cliente["telefono"],
                    direccion_obra=datos_cliente.get("direccion_obra"),
                    es_vivienda_habitual=datos_cliente.get("es_vivienda_habitual"),
                    logo_path=datos_cliente.get("logo_path"),
                    notas=datos_cliente.get("notas"),
                )
                
                logger.info(f"✓ Cliente asignado: {datos_cliente['nombre']}")
            
            # ==========================================
            # Fase 4: Generación de documentos
            # ==========================================
            logger.info("📄 Fase 4: Generando documentos...")
            
            resultado["mensaje_cliente"] = self.document_agent.generar_mensaje_cliente(presupuesto)
            
            if generar_pdf:
                resultado["pdf_bytes"] = self.document_agent.generar_pdf(presupuesto)
                logger.info(f"✓ PDF generado: {len(resultado['pdf_bytes'])} bytes")
            
            # ==========================================
            # Finalización
            # ==========================================
            resultado["exito"] = True
            logger.info("=" * 50)
            logger.info(f"✅ Presupuesto completado: {presupuesto.numero_presupuesto}")
            logger.info(f"   Total: {presupuesto.total:,.2f}€")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.exception(f"Error procesando presupuesto: {e}")
            resultado["errores"].append(f"Error interno: {str(e)}")
        
        return resultado
    
    def procesar_presupuesto_rapido(
        self,
        tipo_inmueble: str,
        metros_cuadrados: float,
        paquete: str,
        calidad: str = "estandar",
        es_vivienda_habitual: bool = False,
    ) -> dict:
        """
        Procesa un presupuesto rápido con un paquete predefinido.
        
        Ideal para presupuestos sencillos sin partidas individuales.
        
        Args:
            tipo_inmueble: Tipo de inmueble
            metros_cuadrados: Superficie
            paquete: Paquete a aplicar
            calidad: Nivel de calidad
            es_vivienda_habitual: Si aplica IVA reducido
            
        Returns:
            dict: Resultado del proceso
        """
        datos_formulario = {
            "tipo_inmueble": tipo_inmueble,
            "metros_cuadrados": metros_cuadrados,
            "calidad": calidad,
            "es_vivienda_habitual": es_vivienda_habitual,
            "paquetes": [paquete],
        }
        
        return self.procesar_presupuesto(
            datos_formulario=datos_formulario,
            generar_pdf=False,
        )
    
    def comparar_opciones(
        self,
        datos_formulario: dict,
        paquete_alternativo: str,
    ) -> dict:
        """
        Compara partidas individuales vs paquete.
        
        Args:
            datos_formulario: Datos con partidas individuales
            paquete_alternativo: Paquete para comparar
            
        Returns:
            dict: Comparativa detallada
        """
        logger.info(f"Comparando partidas vs {paquete_alternativo}...")
        
        # Validar datos
        datos_validados = self.data_collector.procesar_formulario(datos_formulario)
        
        if not datos_validados["exito"]:
            return {
                "exito": False,
                "errores": datos_validados["errores"],
            }
        
        # Calcular comparativa
        comparativa = self.calculator.calcular_con_comparativa(
            datos_proyecto=datos_validados["proyecto"],
            partidas=datos_validados["partidas"],
            paquete_alternativo=paquete_alternativo,
        )
        
        return {
            "exito": True,
            "comparativa": comparativa,
        }
    
    def obtener_catalogo(self) -> dict:
        """
        Obtiene el catálogo completo de categorías, partidas y paquetes.
        
        Útil para poblar la UI.
        
        Returns:
            dict: Catálogo completo
        """
        pricing = self.calculator.budget_service.pricing
        
        return {
            "categorias": pricing.listar_categorias(),
            "paquetes": pricing.listar_paquetes(),
        }
    
    def ejecutar_con_ia(
        self,
        datos_formulario: dict,
        analisis_profundo: bool = True,
    ) -> dict:
        """
        Ejecuta el flujo completo usando las capacidades de IA de CrewAI.
        
        Este método usa los agentes de CrewAI para hacer análisis
        más profundos que van más allá del cálculo determinista.
        
        Args:
            datos_formulario: Datos del formulario
            analisis_profundo: Si hacer análisis con IA
            
        Returns:
            dict: Resultado con análisis de IA
        """
        # Primero ejecutar el flujo normal
        resultado = self.procesar_presupuesto(
            datos_formulario=datos_formulario,
            generar_pdf=False,
        )
        
        if not resultado["exito"] or not analisis_profundo:
            return resultado
        
        # Añadir análisis con IA
        logger.info("🤖 Ejecutando análisis con IA...")
        
        try:
            # Crear tasks para análisis
            tasks = [
                self.data_collector.crear_task_validacion(datos_formulario),
                self.calculator.crear_task_calculo(resultado["desglose"]),
                self.document_agent.crear_task_documento(resultado["presupuesto"]),
            ]
            
            # Ejecutar crew
            crew_result = self.crew.kickoff(tasks=tasks)
            
            resultado["analisis_ia"] = {
                "ejecutado": True,
                "resultado": str(crew_result),
            }
            
            logger.info("✓ Análisis con IA completado")
            
        except Exception as e:
            logger.warning(f"Análisis con IA falló (no crítico): {e}")
            resultado["analisis_ia"] = {
                "ejecutado": False,
                "error": str(e),
            }
        
        return resultado


# Instancia singleton
_budget_crew: Optional[BudgetCrew] = None


def get_budget_crew() -> BudgetCrew:
    """
    Obtiene la instancia del crew (singleton).
    
    Returns:
        BudgetCrew: Instancia del crew
    """
    global _budget_crew
    if _budget_crew is None:
        _budget_crew = BudgetCrew()
    return _budget_crew