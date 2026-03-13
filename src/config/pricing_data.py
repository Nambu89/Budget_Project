"""
Base de datos de precios para reformas en España (2025-2026).

Este módulo contiene todos los precios de referencia para:
- Partidas individuales por categoría
- Paquetes completos (baño, reforma integral)
- Disclaimers legales profesionales

Fuentes de precios: Cronoshare, Habitissimo, CYPE (referencia),
datos de mercado españoles actualizados.
"""

from typing import Dict, Any


# ============================================
# PRECIOS POR PARTIDAS INDIVIDUALES
# ============================================
# Estructura: categoria -> partida -> {basico, estandar, premium, unidad, descripcion}

PRICING_DATA: Dict[str, Dict[str, Any]] = {
    "albanileria": {
        "demolicion": {
            "basico": 17.5, "estandar": 17.5, "premium": 17.5,
            "unidad": "m2", "descripcion": "Demolición y desescombro (m2)"
        },
        "alisado_paredes": {
            "basico": 13.5, "estandar": 20.0, "premium": 30.0,
            "unidad": "m2", "descripcion": "Alisado paredes (m2)"
        },
        "empotrado_rozas": {
            "basico": 12.0, "estandar": 18.0, "premium": 25.0,
            "unidad": "ml", "descripcion": "Empotrado/rozas para trabajos de electricidad fontanería (ml)"
        },
        "refuerzo_esquinas": {
            "basico": 8.0, "estandar": 12.0, "premium": 18.0,
            "unidad": "ud", "descripcion": "Refuerzo esquinas (ud/s)"
        },
        "pintura": {
            "basico": 12.0, "estandar": 12.0, "premium": 12.0,
            "unidad": "m2", "descripcion": "Pintura (m2)"
        },
        "tabique_pladur": {
            "basico": 35.0, "estandar": 45.0, "premium": 60.0,
            "unidad": "m2", "descripcion": "Tabique de pladur (m2)"
        },
        "tabique_ladrillo": {
            "basico": 28.0, "estandar": 38.0, "premium": 50.0,
            "unidad": "m2", "descripcion": "Tabique de ladrillo (m2)"
        },
        "falso_techo_pladur": {
            "basico": 22.5, "estandar": 35.0, "premium": 52.5,
            "unidad": "m2", "descripcion": "Falso techo de pladur (m2)"
        },
        "falso_techo_practicable": {
            "basico": 30.0, "estandar": 45.0, "premium": 65.0,
            "unidad": "m2", "descripcion": "Falso techo practicable (m2)"
        },
        "alicatado_paredes": {
            "basico": 30.0, "estandar": 47.5, "premium": 80.0,
            "unidad": "m2", "descripcion": "Alicatado de paredes (m2)"
        },
        "solado_suelo": {
            "basico": 30.0, "estandar": 47.5, "premium": 80.0,
            "unidad": "m2", "descripcion": "Solado de suelo (m2)"
        },
        "instalacion_rodapie_porcelanico": {
            "basico": 8.0, "estandar": 12.0, "premium": 18.0,
            "unidad": "m2", "descripcion": "Instalación rodapié porcelánico (m2)"
        },
        "nivelacion_suelo": {
            "basico": 12.0, "estandar": 18.0, "premium": 28.0,
            "unidad": "m2", "descripcion": "Nivelación de suelo (m2)"
        },
        "sustitucion_plato_ducha": {
            "basico": 180.0, "estandar": 280.0, "premium": 450.0,
            "unidad": "ud", "descripcion": "Sustitución de plato de ducha (ud/s)"
        },
        "sustitucion_banera_plato_ducha": {
            "basico": 200.0, "estandar": 320.0, "premium": 500.0,
            "unidad": "ud", "descripcion": "Sustitución de bañera por plato de ducha (ud/s)"
        },
    },

    "fontaneria": {
        "ejecucion_completa_bano": {
            "basico": 800.0, "estandar": 1200.0, "premium": 2000.0,
            "unidad": "m2", "descripcion": "Ejecución completa baño (especificar nº lavabos, sanitarios, duchas/bañeras)"
        },
        "ejecucion_completa_cocina": {
            "basico": 600.0, "estandar": 900.0, "premium": 1500.0,
            "unidad": "m2", "descripcion": "Ejecución completa cocina (especificar nº fregadero y electrodomésticos con agua)"
        },
        "instalacion_desague": {
            "basico": 120.0, "estandar": 180.0, "premium": 280.0,
            "unidad": "ud", "descripcion": "Instalación de desagüe (ud/s)"
        },
        "instalacion_toma_suministro": {
            "basico": 100.0, "estandar": 160.0, "premium": 250.0,
            "unidad": "ud", "descripcion": "Instalación de tomas de suministro de agua (ud)"
        },
        "instalacion_griferia_ducha": {
            "basico": 80.0, "estandar": 180.0, "premium": 450.0,
            "unidad": "ud", "descripcion": "Instalación grifería ducha (ud/s)"
        },
        "instalacion_grifo_lavabo": {
            "basico": 60.0, "estandar": 120.0, "premium": 300.0,
            "unidad": "ud", "descripcion": "Instalación grifo lavabo (ud/s)"
        },
        "instalacion_mueble_lavabo": {
            "basico": 300.0, "estandar": 550.0, "premium": 1200.0,
            "unidad": "ud", "descripcion": "Instalación mueble lavabo (ud/s)"
        },
        "instalacion_inodoro": {
            "basico": 200.0, "estandar": 400.0, "premium": 900.0,
            "unidad": "ud", "descripcion": "Instalación inodoro (ud/s)"
        },
        "instalacion_mampara": {
            "basico": 250.0, "estandar": 450.0, "premium": 900.0,
            "unidad": "ud", "descripcion": "Instalación mampara (ud/s)"
        },
    },

    "electricidad": {
        "instalacion_completa": {
            "basico": 3500.0, "estandar": 4500.0, "premium": 7000.0,
            "unidad": "m2", "descripcion": "Instalación completa (m2 de piso)"
        },
        "instalacion_enchufes": {
            "basico": 40.0, "estandar": 55.0, "premium": 85.0,
            "unidad": "ud", "descripcion": "Instalación de enchufes (ud/s)"
        },
        "instalacion_interruptores": {
            "basico": 35.0, "estandar": 50.0, "premium": 80.0,
            "unidad": "ud", "descripcion": "Instalación de interruptores (ud/s)"
        },
        "instalacion_puntos_luz": {
            "basico": 45.0, "estandar": 65.0, "premium": 100.0,
            "unidad": "ud", "descripcion": "Instalación puntos de luz (ud/s)"
        },
        "toma_antena_tv": {
            "basico": 45.0, "estandar": 65.0, "premium": 100.0,
            "unidad": "ud", "descripcion": "Instalación de tomas de antena TV (ud/s)"
        },
        "toma_internet": {
            "basico": 50.0, "estandar": 75.0, "premium": 120.0,
            "unidad": "ud", "descripcion": "Instalación de tomas de internet (ud/s)"
        },
    },

    "carpinteria": {
        "instalacion_suelo_laminado": {
            "basico": 18.0, "estandar": 28.0, "premium": 45.0,
            "unidad": "m2", "descripcion": "Instalación de suelo laminado (m2) + Rodapié"
        },
        "instalacion_vinilico_click": {
            "basico": 22.0, "estandar": 35.0, "premium": 55.0,
            "unidad": "m2", "descripcion": "Instalación de vinílico en click (m2) + Rodapié"
        },
        "instalacion_suelo_parquet": {
            "basico": 35.0, "estandar": 55.0, "premium": 90.0,
            "unidad": "m2", "descripcion": "Instalación de suelo de parquet (m2) + Rodapié"
        },
        "instalacion_rodapie": {
            "basico": 6.0, "estandar": 10.0, "premium": 16.0,
            "unidad": "ml", "descripcion": "Instalación de rodapié (ml)"
        },
        "puerta_interior_abatible": {
            "basico": 120.0, "estandar": 120.0, "premium": 120.0,
            "unidad": "ud", "descripcion": "Instalación de puerta interior de paso abatible (ud/s)"
        },
        "puerta_entrada_blindada": {
            "basico": 400.0, "estandar": 400.0, "premium": 400.0,
            "unidad": "ud", "descripcion": "Instalación de puerta de entrada blindada abatible (ud/s) SIN IVA"
        },
        "puerta_corredera_superficie": {
            "basico": 120.0, "estandar": 120.0, "premium": 120.0,
            "unidad": "ud", "descripcion": "Instalación de puerta corredera de superficie (ud/s) SIN IVA"
        },
        "puerta_corredera_integrada": {
            "basico": 360.0, "estandar": 360.0, "premium": 360.0,
            "unidad": "ud", "descripcion": "Instalación de puerta corredera integrada (ud/s) SIN IVA"
        },
        "armario_medida": {
            "basico": 350.0, "estandar": 550.0, "premium": 900.0,
            "unidad": "m", "descripcion": "Instalación de armario a medida (ancho x alto) en m"
        },
        "instalacion_ventana": {
            "basico": 250.0, "estandar": 250.0, "premium": 250.0,
            "unidad": "ud", "descripcion": "Instalación de ventana (ud/s)"
        },
    },
}

# ============================================
# PAQUETES COMPLETOS
# ============================================
# Los paquetes tienen un descuento implícito vs partidas individuales

PACKAGES_DATA: Dict[str, Dict[str, Any]] = {
    "bano_completo": {
        "nombre": "Reforma integral baño completo",
        "descripcion": "Reforma integral de baño",
        "incluye": [
            "Demolición y desescombro",
            "Alicatado paredes",
            "Solado",
            "Plato de ducha o bañera",
            "Mampara",
            "Inodoro",
            "Mueble lavabo con grifería",
            "Instalación fontanería",
            "Puntos de luz",
            "Pintura techo",
        ],
        "precios": {
            "basico": {"precio_base": 3500.0, "m2_referencia": 5, "precio_m2_adicional": 350.0},
            "estandar": {"precio_base": 5500.0, "m2_referencia": 5, "precio_m2_adicional": 500.0},
            "premium": {"precio_base": 9000.0, "m2_referencia": 5, "precio_m2_adicional": 750.0},
        },
    },

    "reforma_integral_vivienda": {
        "nombre": "Reforma integral vivienda completa",
        "descripcion": "Reforma completa de vivienda incluyendo todas las estancias",
        "incluye": [
            "Demolición general y desescombro",
            "Tabiquería nueva (si aplica)",
            "Instalación eléctrica completa",
            "Instalación fontanería completa",
            "Solado toda la vivienda",
            "Alicatado zonas húmedas",
            "Pintura completa",
            "Carpintería interior",
        ],
        "precios": {
            "basico": {"precio_m2": 650.0},
            "estandar": {"precio_m2": 950.0},
            "premium": {"precio_m2": 1500.0},
        },
    },

    "reforma_integral_local": {
        "nombre": "Reforma integral Local/Oficina",
        "descripcion": "Reforma completa de local comercial u oficina",
        "incluye": [
            "Demolición y desescombro",
            "Tabiquería/distribución",
            "Instalación eléctrica completa",
            "Solado completo",
            "Pintura completa",
        ],
        "precios": {
            "basico": {"precio_m2": 450.0},
            "estandar": {"precio_m2": 700.0},
            "premium": {"precio_m2": 1250.0},
        },
    },

    "reforma_integral_aseo": {
        "nombre": "Reforma integral aseo",
        "descripcion": "Reforma de aseo básico",
        "incluye": [
            "Alicatado",
            "Solado",
            "Inodoro y lavabo",
            "Fontanería",
            "Pintura",
        ],
        "precios": {
            "basico": {"precio_base": 2000.0, "m2_referencia": 3, "precio_m2_adicional": 200.0},
            "estandar": {"precio_base": 3000.0, "m2_referencia": 3, "precio_m2_adicional": 300.0},
            "premium": {"precio_base": 5000.0, "m2_referencia": 3, "precio_m2_adicional": 500.0},
        },
    },
}

DISCLAIMERS: Dict[str, str] = {
    "principal": """
CONDICIONES GENERALES DEL PRESUPUESTO

Este presupuesto es una ESTIMACIÓN ORIENTATIVA basada en la información
proporcionada por el cliente sin visita presencial a la obra.

El presupuesto definitivo se emitirá tras:
- Visita técnica in situ
- Evaluación del estado real de las instalaciones
- Confirmación de mediciones exactas
- Verificación de cumplimiento normativo
""",

    "validez": """
VALIDEZ
Este presupuesto tiene una validez de {dias_validez} días naturales desde
su fecha de emisión. Transcurrido este plazo, los precios podrían sufrir
variaciones.
""",

    "iva": """
IMPUESTOS
- IVA del 21% incluido en los precios mostrados
- El IVA se añade al total del presupuesto
- Todos los inmuebles: IVA general del 21%
""",

    "forma_pago": """
FORMA DE PAGO
Forma de pago habitual (negociable según contrato):
- 50% al inicio de los trabajos
- 30% a mitad de obra
- 20% a la finalización y conformidad
""",

    "variaciones": """
POSIBLES VARIACIONES
Los precios pueden variar en función de:
- Estado oculto de instalaciones (tuberías, cableado, estructura)
- Necesidades no detectables sin catas previas
- Cambios normativos o de permisos municipales
- Variaciones significativas en costes de materiales
- Modificaciones solicitadas por el cliente durante la obra
""",

    "no_incluido": """
NO INCLUIDO (salvo indicación expresa)
- Licencias y tasas municipales
- Permisos de obra
- Contenedores de escombros
- Mudanzas o vaciado previo
- Mobiliario decorativo
- Electrodomésticos no especificados
""",

    "garantias": """
GARANTÍAS
Los trabajos ejecutados contarán con las garantías establecidas por la
legislación vigente:
- Ley 38/1999 de Ordenación de la Edificación
- Normativa de protección al consumidor aplicable
- Garantía de materiales según fabricante
""",

    "proteccion_datos": """
PROTECCIÓN DE DATOS
Los datos personales proporcionados serán tratados conforme al Reglamento
General de Protección de Datos (RGPD) y la Ley Orgánica 3/2018 de
Protección de Datos Personales y garantía de los derechos digitales.
""",

    "pie": """
---
Para presupuesto definitivo, contacte con nosotros para concertar visita técnica.
Este documento NO constituye oferta contractual vinculante.
""",
}


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def get_precio_partida(
    categoria: str,
    partida: str,
    calidad: str = "estandar"
) -> float:
    """
    Obtiene el precio de una partida específica.

    Args:
        categoria: Categoría de trabajo (albanileria, fontaneria, etc.)
        partida: Nombre de la partida
        calidad: Nivel de calidad (basico, estandar, premium)

    Returns:
        float: Precio de la partida o 0.0 si no existe
    """
    try:
        return PRICING_DATA[categoria][partida][calidad]
    except KeyError:
        return 0.0


def get_precio_paquete(
    paquete: str,
    calidad: str = "estandar",
    metros: float = None
) -> float:
    """
    Obtiene el precio de un paquete completo.

    Args:
        paquete: Nombre del paquete
        calidad: Nivel de calidad (basico, estandar, premium)
        metros: Metros cuadrados (para reformas integrales)

    Returns:
        float: Precio del paquete
    """
    try:
        precios = PACKAGES_DATA[paquete]["precios"][calidad]

        # Paquetes por m2 (reformas integrales)
        if "precio_m2" in precios:
            return precios["precio_m2"] * (metros or 0)

        # Paquetes con precio base + m2 adicionales
        precio = precios["precio_base"]
        if metros and metros > precios.get("m2_referencia", 0):
            m2_extra = metros - precios["m2_referencia"]
            precio += m2_extra * precios.get("precio_m2_adicional", 0)

        return precio

    except KeyError:
        return 0.0


def get_todas_categorias() -> list:
    """Retorna lista de todas las categorías disponibles."""
    return list(PRICING_DATA.keys())


def get_partidas_categoria(categoria: str) -> list:
    """Retorna lista de partidas de una categoría."""
    return list(PRICING_DATA.get(categoria, {}).keys())


def get_todos_paquetes() -> list:
    """Retorna lista de todos los paquetes disponibles."""
    return list(PACKAGES_DATA.keys())
