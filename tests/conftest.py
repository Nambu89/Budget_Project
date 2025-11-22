"""
Configuración compartida para tests.

Contiene fixtures y configuración común
para todos los tests del proyecto.
"""

import pytest
import sys
from pathlib import Path

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import Settings
from src.domain.enums import PropertyType, QualityLevel, WorkCategory
from src.domain.models import Project, Customer, BudgetItem, Budget


# ============================================
# Fixtures de configuración
# ============================================

@pytest.fixture
def settings_test():
    """Settings de prueba sin cargar .env real."""
    return Settings(
        llm_provider="azure",
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_api_key="test-key",
        azure_openai_deployment_name="gpt-4o-mini",
        environment="development",
        debug=True,
    )


# ============================================
# Fixtures de dominio
# ============================================

@pytest.fixture
def proyecto_piso():
    """Proyecto de ejemplo: piso estándar."""
    return Project(
        tipo_inmueble=PropertyType.PISO,
        metros_cuadrados=80.0,
        calidad_general=QualityLevel.ESTANDAR,
        es_vivienda_habitual=True,
        estado_actual="normal",
        ubicacion="Madrid",
    )


@pytest.fixture
def proyecto_local():
    """Proyecto de ejemplo: local comercial."""
    return Project(
        tipo_inmueble=PropertyType.LOCAL,
        metros_cuadrados=120.0,
        calidad_general=QualityLevel.BASICO,
        es_vivienda_habitual=False,
        estado_actual="antiguo",
    )


@pytest.fixture
def cliente_ejemplo():
    """Cliente de ejemplo."""
    return Customer(
        nombre="Juan García López",
        email="juan@example.com",
        telefono="612345678",
        direccion_obra="Calle Mayor 123, Madrid",
        es_vivienda_habitual=True,
    )


@pytest.fixture
def partida_albanileria():
    """Partida de ejemplo: albañilería."""
    return BudgetItem(
        categoria=WorkCategory.ALBANILERIA,
        codigo="ALB-ALIC",
        descripcion="Alicatado de paredes con azulejo",
        unidad="m2",
        cantidad=25.0,
        precio_unitario=47.5,
        calidad=QualityLevel.ESTANDAR,
        es_paquete=False,
    )


@pytest.fixture
def partida_fontaneria():
    """Partida de ejemplo: fontanería."""
    return BudgetItem(
        categoria=WorkCategory.FONTANERIA,
        codigo="FON-PLATO",
        descripcion="Plato de ducha con instalación completa",
        unidad="ud",
        cantidad=1.0,
        precio_unitario=700.0,
        calidad=QualityLevel.ESTANDAR,
        es_paquete=False,
    )


@pytest.fixture
def presupuesto_vacio(proyecto_piso):
    """Presupuesto vacío de ejemplo."""
    return Budget(
        proyecto=proyecto_piso,
        dias_validez=30,
    )


@pytest.fixture
def presupuesto_con_partidas(proyecto_piso, partida_albanileria, partida_fontaneria):
    """Presupuesto con partidas de ejemplo."""
    presupuesto = Budget(
        proyecto=proyecto_piso,
        dias_validez=30,
    )
    presupuesto.agregar_partida(partida_albanileria)
    presupuesto.agregar_partida(partida_fontaneria)
    return presupuesto


# ============================================
# Fixtures de datos de formulario
# ============================================

@pytest.fixture
def datos_formulario_completo():
    """Datos de formulario completo para testing."""
    return {
        "tipo_inmueble": "piso",
        "metros_cuadrados": 80.0,
        "calidad": "estandar",
        "es_vivienda_habitual": True,
        "estado_actual": "normal",
        "ubicacion": "Madrid",
        "partidas": [
            {
                "categoria": "albanileria",
                "partida": "alicatado_paredes",
                "cantidad": 25.0,
                "calidad": "estandar",
            },
            {
                "categoria": "fontaneria",
                "partida": "plato_ducha",
                "cantidad": 1.0,
                "calidad": "estandar",
            },
        ],
        "paquetes": [],
    }


@pytest.fixture
def datos_formulario_con_paquete():
    """Datos de formulario con paquete."""
    return {
        "tipo_inmueble": "piso",
        "metros_cuadrados": 60.0,
        "calidad": "estandar",
        "es_vivienda_habitual": True,
        "estado_actual": "normal",
        "partidas": [],
        "paquetes": ["bano_completo"],
    }


@pytest.fixture
def datos_cliente():
    """Datos de cliente para testing."""
    return {
        "nombre": "María López",
        "email": "maria@test.com",
        "telefono": "698765432",
        "direccion_obra": "Av. Principal 45, Barcelona",
    }