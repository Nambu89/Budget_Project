"""
Tests de comunicación entre agentes.

Verifica que los agentes se comunican correctamente
y que el flujo de datos entre ellos funciona.

NOTA: Estos tests requieren un LLM configurado (Azure u OpenAI).
Se saltan automáticamente si no hay API key.
"""

import pytest
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import settings
from src.domain.enums import PropertyType, QualityLevel, WorkCategory

# Determinar si hay un LLM configurado
LLM_AVAILABLE = settings.is_azure_configured() or settings.is_openai_configured()
SKIP_REASON = "No hay LLM configurado (se requiere OPENAI_API_KEY o AZURE_OPENAI_API_KEY)"


@pytest.mark.skipif(not LLM_AVAILABLE, reason=SKIP_REASON)
class TestDataCollectorAgent:
    """Tests del agente recolector de datos."""

    def test_agent_initialization(self):
        """Test: El agente se inicializa correctamente."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        assert agent is not None
        print("DataCollectorAgent inicializado")

    def test_validar_tipo_inmueble_valido(self):
        """Test: Valida tipos de inmueble correctos."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        casos = [
            ("piso", PropertyType.PISO),
            ("vivienda", PropertyType.VIVIENDA),
            ("oficina", PropertyType.OFICINA),
            ("local", PropertyType.LOCAL),
            ("PISO", PropertyType.PISO),
            ("casa", PropertyType.VIVIENDA),
        ]

        for entrada, esperado in casos:
            valido, tipo, msg = agent.validar_tipo_inmueble(entrada)
            assert valido is True, f"Fallo para: {entrada}"
            assert tipo == esperado, f"Tipo incorrecto para: {entrada}"

        print("Validacion de tipos de inmueble correcta")

    def test_validar_tipo_inmueble_invalido(self):
        """Test: Rechaza tipos de inmueble incorrectos."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        valido, tipo, msg = agent.validar_tipo_inmueble("garaje")

        assert valido is False
        assert tipo is None
        print(f"Tipo invalido rechazado: {msg}")

    def test_validar_metros_validos(self):
        """Test: Valida metros cuadrados correctos."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        casos = [
            (80, 80.0),
            (80.5, 80.5),
            ("100", 100.0),
            (5, 5.0),
            (10000, 10000.0),
        ]

        for entrada, esperado in casos:
            valido, metros, msg = agent.validar_metros(entrada)
            assert valido is True, f"Fallo para: {entrada}"
            assert metros == esperado, f"Metros incorrectos para: {entrada}"

        print("Validacion de metros correcta")

    def test_validar_metros_invalidos(self):
        """Test: Rechaza metros cuadrados incorrectos."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        casos_invalidos = [0, -10, "abc", None]

        for entrada in casos_invalidos:
            valido, metros, msg = agent.validar_metros(entrada)
            assert valido is False, f"Deberia fallar para: {entrada}"

        print("Metros invalidos rechazados correctamente")

    def test_validar_calidad(self):
        """Test: Valida niveles de calidad."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        casos = [
            ("basico", QualityLevel.BASICO),
            ("estandar", QualityLevel.ESTANDAR),
            ("premium", QualityLevel.PREMIUM),
            ("ESTANDAR", QualityLevel.ESTANDAR),
            ("normal", QualityLevel.ESTANDAR),
        ]

        for entrada, esperado in casos:
            valido, calidad, msg = agent.validar_calidad(entrada)
            assert valido is True, f"Fallo para: {entrada}"
            assert calidad == esperado

        print("Validacion de calidad correcta")

    def test_procesar_formulario_completo(self, datos_formulario_completo):
        """Test: Procesa formulario completo correctamente."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        resultado = agent.procesar_formulario(datos_formulario_completo)

        assert resultado["exito"] is True
        assert resultado["proyecto"] is not None
        assert resultado["proyecto"]["tipo_inmueble"] == PropertyType.PISO
        assert resultado["proyecto"]["metros_cuadrados"] == 80.0
        assert len(resultado["partidas"]) == 2
        assert len(resultado["errores"]) == 0

        print(f"Formulario procesado: {resultado['proyecto']}")

    def test_procesar_formulario_incompleto(self):
        """Test: Detecta errores en formulario incompleto."""
        from src.application.agents import DataCollectorAgent
        agent = DataCollectorAgent()

        datos_incompletos = {
            "calidad": "estandar",
        }

        resultado = agent.procesar_formulario(datos_incompletos)

        assert resultado["exito"] is False
        assert len(resultado["errores"]) > 0
        print(f"Errores detectados: {resultado['errores']}")


@pytest.mark.skipif(not LLM_AVAILABLE, reason=SKIP_REASON)
class TestCalculatorAgent:
    """Tests del agente calculador."""

    def test_agent_initialization(self):
        """Test: El agente se inicializa correctamente."""
        from src.application.agents import CalculatorAgent
        agent = CalculatorAgent()

        assert agent is not None
        assert agent.budget_service is not None
        print("CalculatorAgent inicializado")

    def test_calcular_presupuesto_basico(self):
        """Test: Calcula presupuesto con partidas."""
        from src.application.agents import CalculatorAgent
        agent = CalculatorAgent()

        datos_proyecto = {
            "tipo_inmueble": PropertyType.PISO,
            "metros_cuadrados": 80.0,
            "calidad": QualityLevel.ESTANDAR,
            "es_vivienda_habitual": True,
            "estado_actual": "normal",
        }

        partidas = [
            {
                "categoria": WorkCategory.ALBANILERIA,
                "partida": "alicatado_paredes",
                "cantidad": 20.0,
                "calidad": QualityLevel.ESTANDAR,
            },
        ]

        presupuesto = agent.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=partidas,
        )

        assert presupuesto is not None
        assert presupuesto.num_partidas > 0
        assert presupuesto.subtotal > 0
        assert presupuesto.total > 0

        print(f"Presupuesto calculado: {presupuesto.total}")

    def test_calcular_presupuesto_con_paquete(self):
        """Test: Calcula presupuesto con paquete."""
        from src.application.agents import CalculatorAgent
        agent = CalculatorAgent()

        datos_proyecto = {
            "tipo_inmueble": PropertyType.PISO,
            "metros_cuadrados": 60.0,
            "calidad": QualityLevel.ESTANDAR,
            "es_vivienda_habitual": True,
            "estado_actual": "normal",
        }

        presupuesto = agent.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=[],
            paquetes=["bano_completo"],
        )

        assert presupuesto is not None
        assert presupuesto.num_partidas > 0
        assert presupuesto.total > 0
        assert presupuesto.partidas[0].es_paquete is True

        print(f"Presupuesto con paquete: {presupuesto.total}")

    def test_obtener_desglose_completo(self):
        """Test: Obtiene desglose detallado."""
        from src.application.agents import CalculatorAgent
        agent = CalculatorAgent()

        datos_proyecto = {
            "tipo_inmueble": PropertyType.PISO,
            "metros_cuadrados": 80.0,
            "calidad": QualityLevel.ESTANDAR,
            "es_vivienda_habitual": True,
            "estado_actual": "normal",
        }

        presupuesto = agent.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=[],
            paquetes=["bano_completo"],
        )

        desglose = agent.obtener_desglose_completo(presupuesto)

        assert "numero_presupuesto" in desglose
        assert "subtotal" in desglose
        assert "iva_porcentaje" in desglose
        assert "total" in desglose
        assert "reglas_aplicadas" in desglose

        print(f"Desglose obtenido: {desglose['total']}")

    def test_sugerir_optimizaciones(self):
        """Test: Sugiere optimizaciones."""
        from src.application.agents import CalculatorAgent
        agent = CalculatorAgent()

        datos_proyecto = {
            "tipo_inmueble": PropertyType.PISO,
            "metros_cuadrados": 80.0,
            "calidad": QualityLevel.ESTANDAR,
            "es_vivienda_habitual": False,
            "estado_actual": "normal",
        }

        presupuesto = agent.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=[],
            paquetes=["bano_completo"],
        )

        sugerencias = agent.sugerir_optimizaciones(presupuesto)

        assert isinstance(sugerencias, list)

        print(f"Sugerencias: {len(sugerencias)} encontradas")


@pytest.mark.skipif(not LLM_AVAILABLE, reason=SKIP_REASON)
class TestDocumentAgent:
    """Tests del agente de documentos."""

    def test_agent_initialization(self):
        """Test: El agente se inicializa correctamente."""
        from src.application.agents import DocumentAgent
        agent = DocumentAgent()

        assert agent is not None
        assert agent.budget_service is not None
        print("DocumentAgent inicializado")

    def test_generar_resumen_texto(self, presupuesto_con_partidas):
        """Test: Genera resumen en texto."""
        from src.application.agents import DocumentAgent
        agent = DocumentAgent()

        resumen = agent.generar_resumen_texto(presupuesto_con_partidas)

        assert resumen is not None
        assert len(resumen) > 0
        assert "Presupuesto" in resumen

        print(f"Resumen generado: {len(resumen)} caracteres")

    def test_generar_resumen_detallado(self, presupuesto_con_partidas):
        """Test: Genera resumen detallado."""
        from src.application.agents import DocumentAgent
        agent = DocumentAgent()

        resumen = agent.generar_resumen_detallado(presupuesto_con_partidas)

        assert resumen is not None
        assert "DATOS DEL PROYECTO" in resumen
        assert "DESGLOSE DE PARTIDAS" in resumen
        assert "TOTALES" in resumen

        print(f"Resumen detallado: {len(resumen)} caracteres")

    def test_generar_mensaje_cliente(self, presupuesto_con_partidas):
        """Test: Genera mensaje para cliente."""
        from src.application.agents import DocumentAgent
        agent = DocumentAgent()

        mensaje = agent.generar_mensaje_cliente(presupuesto_con_partidas)

        assert mensaje is not None
        assert "Presupuesto generado" in mensaje
        assert "TOTAL" in mensaje

        print("Mensaje cliente generado")

    def test_generar_pdf(self, presupuesto_con_partidas):
        """Test: Genera PDF."""
        from src.application.agents import DocumentAgent
        agent = DocumentAgent()

        pdf_bytes = agent.generar_pdf(presupuesto_con_partidas)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

        print(f"PDF generado: {len(pdf_bytes)} bytes")


@pytest.mark.skipif(not LLM_AVAILABLE, reason=SKIP_REASON)
class TestBudgetCrew:
    """Tests del crew de presupuestos."""

    def test_crew_initialization(self):
        """Test: El crew se inicializa correctamente."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        assert crew is not None
        assert crew.data_collector is not None
        assert crew.calculator is not None
        assert crew.document_agent is not None

        print("BudgetCrew inicializado con 3 agentes")

    def test_crew_singleton(self):
        """Test: get_budget_crew retorna singleton."""
        from src.application.crews import get_budget_crew
        crew1 = get_budget_crew()
        crew2 = get_budget_crew()

        assert crew1 is crew2
        print("Singleton funciona correctamente")

    def test_procesar_presupuesto_completo(self, datos_formulario_completo):
        """Test: Procesa presupuesto completo."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        resultado = crew.procesar_presupuesto(
            datos_formulario=datos_formulario_completo,
            generar_pdf=True,
        )

        assert resultado["exito"] is True
        assert resultado["presupuesto"] is not None
        assert resultado["desglose"] is not None
        assert resultado["pdf_bytes"] is not None
        assert len(resultado["errores"]) == 0

        print(f"Presupuesto procesado: {resultado['presupuesto'].total}")

    def test_procesar_presupuesto_con_paquete(self, datos_formulario_con_paquete):
        """Test: Procesa presupuesto con paquete."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        resultado = crew.procesar_presupuesto(
            datos_formulario=datos_formulario_con_paquete,
            generar_pdf=False,
        )

        assert resultado["exito"] is True
        assert resultado["presupuesto"] is not None
        assert resultado["presupuesto"].partidas[0].es_paquete is True

        print(f"Presupuesto con paquete: {resultado['presupuesto'].total}")

    def test_procesar_presupuesto_con_cliente(self, datos_formulario_completo, datos_cliente):
        """Test: Procesa presupuesto con datos de cliente."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        resultado = crew.procesar_presupuesto(
            datos_formulario=datos_formulario_completo,
            datos_cliente=datos_cliente,
            generar_pdf=True,
        )

        assert resultado["exito"] is True
        assert resultado["presupuesto"].tiene_cliente is True
        assert resultado["presupuesto"].cliente.nombre == datos_cliente["nombre"]

        print(f"Presupuesto con cliente: {resultado['presupuesto'].cliente.nombre}")

    def test_comparar_opciones(self, datos_formulario_completo):
        """Test: Compara partidas vs paquete."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        resultado = crew.comparar_opciones(
            datos_formulario=datos_formulario_completo,
            paquete_alternativo="bano_completo",
        )

        assert resultado["exito"] is True
        assert "comparativa" in resultado
        assert "total_partidas" in resultado["comparativa"]
        assert "total_paquete" in resultado["comparativa"]

        print(f"Comparativa: partidas={resultado['comparativa']['total_partidas']} vs paquete={resultado['comparativa']['total_paquete']}")

    def test_obtener_catalogo(self):
        """Test: Obtiene catalogo completo."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        catalogo = crew.obtener_catalogo()

        assert "categorias" in catalogo
        assert "paquetes" in catalogo
        assert len(catalogo["categorias"]) > 0
        assert len(catalogo["paquetes"]) > 0

        print(f"Catalogo: {len(catalogo['categorias'])} categorias, {len(catalogo['paquetes'])} paquetes")


@pytest.mark.skipif(not LLM_AVAILABLE, reason=SKIP_REASON)
class TestAgentCommunication:
    """Tests de comunicación entre agentes."""

    def test_flujo_completo_data_to_calculator(self):
        """Test: Datos fluyen de DataCollector a Calculator."""
        from src.application.agents import DataCollectorAgent, CalculatorAgent
        data_collector = DataCollectorAgent()
        calculator = CalculatorAgent()

        datos_formulario = {
            "tipo_inmueble": "piso",
            "metros_cuadrados": 80.0,
            "calidad": "estandar",
            "es_vivienda_habitual": True,
            "estado_actual": "normal",
            "partidas": [
                {"categoria": "albanileria", "partida": "pintura", "cantidad": 100.0},
            ],
        }

        resultado_validacion = data_collector.procesar_formulario(datos_formulario)

        assert resultado_validacion["exito"] is True

        presupuesto = calculator.calcular_presupuesto(
            datos_proyecto=resultado_validacion["proyecto"],
            partidas=resultado_validacion["partidas"],
        )

        assert presupuesto is not None
        assert presupuesto.total > 0

        print(f"Flujo DataCollector -> Calculator: {presupuesto.total}")

    def test_flujo_completo_calculator_to_document(self):
        """Test: Datos fluyen de Calculator a Document."""
        from src.application.agents import CalculatorAgent, DocumentAgent
        calculator = CalculatorAgent()
        document = DocumentAgent()

        datos_proyecto = {
            "tipo_inmueble": PropertyType.PISO,
            "metros_cuadrados": 80.0,
            "calidad": QualityLevel.ESTANDAR,
            "es_vivienda_habitual": True,
            "estado_actual": "normal",
        }

        presupuesto = calculator.calcular_presupuesto(
            datos_proyecto=datos_proyecto,
            partidas=[],
            paquetes=["bano_completo"],
        )

        pdf_bytes = document.generar_pdf(presupuesto)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000

        print(f"Flujo Calculator -> Document: PDF de {len(pdf_bytes)} bytes")

    def test_flujo_completo_crew(self):
        """Test: Flujo completo a traves del Crew."""
        from src.application.crews import BudgetCrew
        crew = BudgetCrew()

        datos = {
            "tipo_inmueble": "vivienda",
            "metros_cuadrados": 120.0,
            "calidad": "premium",
            "es_vivienda_habitual": True,
            "estado_actual": "antiguo",
            "partidas": [],
            "paquetes": ["reforma_integral_vivienda"],
        }

        cliente = {
            "nombre": "Test User",
            "email": "test@test.com",
            "telefono": "612345678",
        }

        resultado = crew.procesar_presupuesto(
            datos_formulario=datos,
            datos_cliente=cliente,
            generar_pdf=True,
        )

        assert resultado["exito"] is True
        assert resultado["presupuesto"] is not None
        assert resultado["presupuesto"].tiene_cliente is True
        assert resultado["desglose"] is not None
        assert resultado["pdf_bytes"] is not None
        assert len(resultado["errores"]) == 0

        print(f"Flujo completo Crew: {resultado['presupuesto'].numero_presupuesto}")
        print(f"   Total: {resultado['presupuesto'].total}")
        print(f"   Cliente: {resultado['presupuesto'].cliente.nombre}")
        print(f"   PDF: {len(resultado['pdf_bytes'])} bytes")


# ============================================
# Ejecutar tests directamente
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Tests de Comunicacion entre Agentes")
    print("=" * 60)

    pytest.main([__file__, "-v", "-s"])
