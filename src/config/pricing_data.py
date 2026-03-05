"""
Base de datos de precios para reformas en Espana (2025-2026).

Este modulo contiene todos los precios de referencia para:
- Partidas individuales por categoria
- Paquetes completos (bano, cocina, reforma integral)
- Disclaimers legales profesionales

Fuentes de precios: Cronoshare, Habitissimo, CYPE (referencia),
datos de mercado espanoles actualizados.
"""

from typing import Dict, Any


# ============================================
# PRECIOS POR PARTIDAS INDIVIDUALES
# ============================================
# Estructura: categoria -> partida -> {basico, estandar, premium, unidad, descripcion}

PRICING_DATA: Dict[str, Dict[str, Any]] = {
    "albanileria": {
        "alicatado_paredes": {
            "basico": 30.0,
            "estandar": 47.5,
            "premium": 80.0,
            "unidad": "m2",
            "descripcion": "Alicatado de paredes (m2 de superficie - ancho x alto)",
        },
        "solado_porcelanico": {
            "basico": 30.0,
            "estandar": 47.5,
            "premium": 80.0,
            "unidad": "m2",
            "descripcion": "Solado con baldosa porcelanica (m2 de superficie)",
        },
        "solado_vinilico": {
            "basico": 20.0,
            "estandar": 35.0,
            "premium": 52.5,
            "unidad": "m2",
            "descripcion": "Solado con suelo vinilico (m2 de superficie)",
        },
        "alisado_paredes": {
            "basico": 13.5,
            "estandar": 20.0,
            "premium": 30.0,
            "unidad": "m2",
            "descripcion": "Alisado y enyesado de paredes (m2 de superficie - ancho x alto)",
        },
        "pintura": {
            "basico": 9.0,
            "estandar": 15.0,
            "premium": 30.0,
            "unidad": "m2",
            "descripcion": "Pintura de paredes (m2 de superficie - ancho x alto, incluye imprimacion)",
        },
        "demolicion": {
            "basico": 17.5,
            "estandar": 17.5,
            "premium": 17.5,
            "unidad": "m2",
            "descripcion": "Demolicion y desescombro (m2 de superficie)",
        },
        "falso_techo_pladur": {
            "basico": 22.5,
            "estandar": 35.0,
            "premium": 52.5,
            "unidad": "m2",
            "descripcion": "Falso techo de pladur con estructura (m2 de superficie)",
        },
        "falso_techo_practicable": {
            "basico": 30.0,
            "estandar": 45.0,
            "premium": 65.0,
            "unidad": "m2",
            "descripcion": "Falso techo practicable/registrable con estructura (m2 de superficie)",
        },
        "tabique_pladur": {
            "basico": 35.0,
            "estandar": 45.0,
            "premium": 60.0,
            "unidad": "m2",
            "descripcion": "Tabique de pladur con aislamiento (m2 de superficie - ancho x alto)",
        },
        "tabique_ladrillo": {
            "basico": 28.0,
            "estandar": 38.0,
            "premium": 50.0,
            "unidad": "m2",
            "descripcion": "Tabique de ladrillo hueco doble con enlucido (m2 de superficie - ancho x alto)",
        },
        "rodapie_porcelanico": {
            "basico": 8.0,
            "estandar": 12.0,
            "premium": 18.0,
            "unidad": "ml",
            "descripcion": "Rodapie porcelanico instalado (ml - metros lineales del perimetro)",
        },
        "empotrado_rozas": {
            "basico": 12.0,
            "estandar": 18.0,
            "premium": 25.0,
            "unidad": "ml",
            "descripcion": "Apertura y tapado de rozas para instalaciones (ml - metros lineales)",
        },
        "refuerzo_esquinas": {
            "basico": 8.0,
            "estandar": 12.0,
            "premium": 18.0,
            "unidad": "ml",
            "descripcion": "Refuerzo de esquinas con guardavivos (ml - metros lineales)",
        },
        "nivelacion_suelo": {
            "basico": 12.0,
            "estandar": 18.0,
            "premium": 28.0,
            "unidad": "m2",
            "descripcion": "Nivelacion y regularizacion de suelo con mortero autonivelante (m2 de superficie)",
        },
        "instalacion_plato_ducha": {
            "basico": 180.0,
            "estandar": 280.0,
            "premium": 450.0,
            "unidad": "ud",
            "descripcion": "Instalacion de plato de ducha con impermeabilizacion (ud - unidad completa)",
        },
        "instalacion_banera": {
            "basico": 200.0,
            "estandar": 320.0,
            "premium": 500.0,
            "unidad": "ud",
            "descripcion": "Instalacion de banera con faldones y sellado (ud - unidad completa)",
        },
    },

    "fontaneria": {
        "plato_ducha": {
            "basico": 400.0,
            "estandar": 700.0,
            "premium": 1600.0,
            "unidad": "ud",
            "descripcion": "Plato de ducha con instalacion completa (ud - unidad completa instalada)",
        },
        "mampara": {
            "basico": 250.0,
            "estandar": 450.0,
            "premium": 900.0,
            "unidad": "ud",
            "descripcion": "Mampara de ducha/banera instalada (ud - unidad completa)",
        },
        "mueble_lavabo": {
            "basico": 300.0,
            "estandar": 550.0,
            "premium": 1200.0,
            "unidad": "ud",
            "descripcion": "Mueble de lavabo con lavabo y griferia (ud - unidad completa)",
        },
        "inodoro": {
            "basico": 200.0,
            "estandar": 400.0,
            "premium": 900.0,
            "unidad": "ud",
            "descripcion": "Inodoro completo con instalacion (ud - unidad completa)",
        },
        "griferia_ducha": {
            "basico": 80.0,
            "estandar": 180.0,
            "premium": 450.0,
            "unidad": "ud",
            "descripcion": "Griferia de ducha/banera (ud - unidad completa)",
        },
        "griferia_lavabo": {
            "basico": 60.0,
            "estandar": 120.0,
            "premium": 300.0,
            "unidad": "ud",
            "descripcion": "Griferia de lavabo (ud - unidad completa)",
        },
        "ejecucion_completa_bano": {
            "basico": 800.0,
            "estandar": 1200.0,
            "premium": 2000.0,
            "unidad": "ud",
            "descripcion": "Ejecucion completa de fontaneria por bano (ud - instalacion completa)",
        },
        "ejecucion_completa_cocina": {
            "basico": 600.0,
            "estandar": 900.0,
            "premium": 1500.0,
            "unidad": "ud",
            "descripcion": "Ejecucion completa de fontaneria de cocina (ud - instalacion completa)",
        },
        "saneamientos_reparaciones": {
            "basico": 250.0,
            "estandar": 400.0,
            "premium": 650.0,
            "unidad": "ud",
            "descripcion": "Reparacion y saneamiento de tuberias existentes (ud - intervencion completa)",
        },
        "instalacion_desague": {
            "basico": 120.0,
            "estandar": 180.0,
            "premium": 280.0,
            "unidad": "ud",
            "descripcion": "Instalacion de punto de desague nuevo (ud - unidad completa)",
        },
        "instalacion_toma_suministro": {
            "basico": 100.0,
            "estandar": 160.0,
            "premium": 250.0,
            "unidad": "ud",
            "descripcion": "Instalacion de toma de suministro de agua (ud - unidad completa)",
        },
    },

    "electricidad": {
        "instalacion_completa": {
            "basico": 3500.0,
            "estandar": 4500.0,
            "premium": 7000.0,
            "unidad": "vivienda_100m2",
            "descripcion": "Instalacion electrica completa (vivienda ~100m2)",
        },
        "punto_luz": {
            "basico": 45.0,
            "estandar": 65.0,
            "premium": 100.0,
            "unidad": "ud",
            "descripcion": "Punto de luz con cableado y mecanismo (ud - unidad completa)",
        },
        "cuadro_electrico": {
            "basico": 350.0,
            "estandar": 500.0,
            "premium": 800.0,
            "unidad": "ud",
            "descripcion": "Cuadro electrico completo con protecciones (ud - unidad completa)",
        },
        "enchufes": {
            "basico": 40.0,
            "estandar": 55.0,
            "premium": 85.0,
            "unidad": "ud",
            "descripcion": "Enchufe con cableado y mecanismo (ud - unidad completa)",
        },
        "interruptores": {
            "basico": 35.0,
            "estandar": 50.0,
            "premium": 80.0,
            "unidad": "ud",
            "descripcion": "Interruptor con cableado y mecanismo (ud - unidad completa)",
        },
        "toma_antena_tv": {
            "basico": 45.0,
            "estandar": 65.0,
            "premium": 100.0,
            "unidad": "ud",
            "descripcion": "Toma de antena TV con cableado coaxial (ud - unidad completa)",
        },
        "toma_internet": {
            "basico": 50.0,
            "estandar": 75.0,
            "premium": 120.0,
            "unidad": "ud",
            "descripcion": "Toma de internet/datos con cableado RJ45 Cat6 (ud - unidad completa)",
        },
    },

    "cocina": {
        "montaje_mobiliario": {
            "basico": 2500.0,
            "estandar": 4500.0,
            "premium": 9000.0,
            "unidad": "ml",
            "descripcion": "Montaje de mobiliario de cocina por metro lineal (ml - metro lineal)",
        },
        "encimera": {
            "basico": 150.0,
            "estandar": 300.0,
            "premium": 600.0,
            "unidad": "ml",
            "descripcion": "Encimera instalada por metro lineal (ml - metro lineal)",
        },
        "retirada_cocina_antigua": {
            "basico": 350.0,
            "estandar": 450.0,
            "premium": 600.0,
            "unidad": "ud",
            "descripcion": "Retirada de cocina antigua con desconexiones y desescombro (ud - unidad completa)",
        },
        "alicatado_frontal": {
            "basico": 30.0,
            "estandar": 50.0,
            "premium": 85.0,
            "unidad": "m2",
            "descripcion": "Alicatado frontal de cocina con material (m2 de superficie)",
        },
        "fontaneria_cocina": {
            "basico": 400.0,
            "estandar": 600.0,
            "premium": 950.0,
            "unidad": "ud",
            "descripcion": "Instalacion de fontaneria de cocina completa (ud - instalacion completa)",
        },
        "electricidad_cocina": {
            "basico": 350.0,
            "estandar": 550.0,
            "premium": 850.0,
            "unidad": "ud",
            "descripcion": "Instalacion electrica de cocina con circuitos independientes (ud - instalacion completa)",
        },
        "instalacion_electrodomesticos": {
            "basico": 200.0,
            "estandar": 350.0,
            "premium": 550.0,
            "unidad": "ud",
            "descripcion": "Instalacion y conexion de electrodomesticos (ud - conjunto completo)",
        },
        "instalacion_puertas_integrables": {
            "basico": 150.0,
            "estandar": 250.0,
            "premium": 400.0,
            "unidad": "ud",
            "descripcion": "Instalacion de puertas integrables para electrodomesticos (ud - unidad completa)",
        },
    },

    "carpinteria": {
        "puerta_interior": {
            "basico": 180.0,
            "estandar": 300.0,
            "premium": 550.0,
            "unidad": "ud",
            "descripcion": "Puerta interior con marco y herrajes (ud - unidad completa instalada)",
        },
        "puerta_entrada": {
            "basico": 400.0,
            "estandar": 700.0,
            "premium": 1500.0,
            "unidad": "ud",
            "descripcion": "Puerta de entrada blindada/acorazada (ud - unidad completa instalada)",
        },
        "ventana": {
            "basico": 280.0,
            "estandar": 450.0,
            "premium": 780.0,
            "unidad": "ud",
            "descripcion": "Ventana aluminio/PVC con RPT y doble acristalamiento (ud - unidad completa instalada)",
        },
        "armario_empotrado": {
            "basico": 350.0,
            "estandar": 550.0,
            "premium": 900.0,
            "unidad": "ml",
            "descripcion": "Armario empotrado por metro lineal (ml - metro lineal de frente)",
        },
        "suelo_laminado": {
            "basico": 18.0,
            "estandar": 28.0,
            "premium": 45.0,
            "unidad": "m2",
            "descripcion": "Suelo laminado instalado con base aislante (m2 de superficie)",
        },
        "suelo_vinilico_click": {
            "basico": 22.0,
            "estandar": 35.0,
            "premium": 55.0,
            "unidad": "m2",
            "descripcion": "Suelo vinilico en click instalado (m2 de superficie)",
        },
        "parquet": {
            "basico": 35.0,
            "estandar": 55.0,
            "premium": 90.0,
            "unidad": "m2",
            "descripcion": "Parquet macizo/multicapa instalado con lijado y barnizado (m2 de superficie)",
        },
        "rodapie_madera": {
            "basico": 6.0,
            "estandar": 10.0,
            "premium": 16.0,
            "unidad": "ml",
            "descripcion": "Rodapie de madera/MDF instalado (ml - metros lineales del perimetro)",
        },
    },

    "climatizacion": {
        "instalacion_caldera_gas": {
            "basico": 2200.0,
            "estandar": 3200.0,
            "premium": 5000.0,
            "unidad": "ud",
            "descripcion": "Caldera de gas de condensacion instalada con acometida (ud - unidad completa instalada)",
        },
        "circuito_radiadores": {
            "basico": 3000.0,
            "estandar": 4500.0,
            "premium": 7000.0,
            "unidad": "ud",
            "descripcion": "Circuito completo de radiadores para vivienda ~80-100m2 (ud - instalacion completa)",
        },
        "instalacion_aerotermia": {
            "basico": 6000.0,
            "estandar": 9000.0,
            "premium": 14000.0,
            "unidad": "ud",
            "descripcion": "Equipo de aerotermia instalado con deposito ACS (ud - unidad completa instalada)",
        },
        "suelo_radiante": {
            "basico": 45.0,
            "estandar": 65.0,
            "premium": 95.0,
            "unidad": "m2",
            "descripcion": "Instalacion de suelo radiante por m2 (m2 de superficie)",
        },
        "aire_acondicionado": {
            "basico": 800.0,
            "estandar": 1200.0,
            "premium": 2000.0,
            "unidad": "ud",
            "descripcion": "Split de aire acondicionado instalado con equipo e instalacion (ud - unidad completa instalada)",
        },
    },
}


# ============================================
# PAQUETES COMPLETOS
# ============================================
# Los paquetes tienen un descuento implicito vs partidas individuales

PACKAGES_DATA: Dict[str, Dict[str, Any]] = {
    "bano_completo": {
        "nombre": "Bano Completo",
        "descripcion": "Reforma integral de bano incluyendo sanitarios, alicatado, solado, fontaneria y electricidad",
        "incluye": [
            "Demolicion y desescombro",
            "Alicatado paredes",
            "Solado",
            "Plato de ducha o banera",
            "Mampara",
            "Inodoro",
            "Mueble lavabo con griferia",
            "Instalacion fontaneria",
            "Puntos de luz (3-4 uds)",
            "Pintura techo",
        ],
        "precios": {
            "basico": {
                "precio_base": 3500.0,
                "m2_referencia": 5,
                "precio_m2_adicional": 350.0,
            },
            "estandar": {
                "precio_base": 5500.0,
                "m2_referencia": 5,
                "precio_m2_adicional": 500.0,
            },
            "premium": {
                "precio_base": 9000.0,
                "m2_referencia": 5,
                "precio_m2_adicional": 750.0,
            },
        },
    },

    "cocina_completa": {
        "nombre": "Cocina Completa",
        "descripcion": "Reforma integral de cocina con mobiliario, electrodomesticos e instalaciones",
        "incluye": [
            "Demolicion y desescombro",
            "Alicatado zona de trabajo",
            "Solado completo",
            "Mobiliario de cocina",
            "Encimera",
            "Electrodomesticos basicos",
            "Fregadero con griferia",
            "Instalacion fontaneria",
            "Instalacion electrica cocina",
            "Pintura",
        ],
        "precios": {
            "basico": {
                "precio_base": 6000.0,
                "m2_referencia": 8,
                "precio_m2_adicional": 400.0,
            },
            "estandar": {
                "precio_base": 10000.0,
                "m2_referencia": 8,
                "precio_m2_adicional": 600.0,
            },
            "premium": {
                "precio_base": 18000.0,
                "m2_referencia": 8,
                "precio_m2_adicional": 900.0,
            },
        },
    },

    "reforma_integral_vivienda": {
        "nombre": "Reforma Integral Vivienda",
        "descripcion": "Reforma completa de vivienda incluyendo todas las estancias",
        "incluye": [
            "Demolicion general y desescombro",
            "Tabiqueria nueva (si aplica)",
            "Instalacion electrica completa",
            "Instalacion fontaneria completa",
            "Solado toda la vivienda",
            "Alicatado zonas humedas",
            "Pintura completa",
            "Carpinteria interior",
            "Bano completo (1 ud)",
            "Cocina completa",
        ],
        "precios": {
            "basico": {
                "precio_m2": 650.0,
            },
            "estandar": {
                "precio_m2": 950.0,
            },
            "premium": {
                "precio_m2": 1500.0,
            },
        },
    },

    "reforma_integral_local": {
        "nombre": "Reforma Integral Local/Oficina",
        "descripcion": "Reforma completa de local comercial u oficina",
        "incluye": [
            "Demolicion y desescombro",
            "Tabiqueria/distribucion",
            "Instalacion electrica completa",
            "Climatizacion basica",
            "Solado completo",
            "Falso techo (si aplica)",
            "Pintura completa",
            "Aseo basico (1 ud)",
        ],
        "precios": {
            "basico": {
                "precio_m2": 450.0,
            },
            "estandar": {
                "precio_m2": 700.0,
            },
            "premium": {
                "precio_m2": 1250.0,
            },
        },
    },

    # ============================================
    # NUEVOS PAQUETES 2026: SALON Y HABITACION
    # ============================================

    "salon_completo": {
        "nombre": "Reforma de Salon",
        "descripcion": "Reforma de salon incluyendo suelo, pintura, rodapies y puntos de luz",
        "incluye": [
            "Suelo laminado/vinilico",
            "Pintura de paredes y techo",
            "Rodapies",
            "Puntos de luz (2-3 uds)",
        ],
        "precios": {
            "basico": {
                "precio_base": 1200.0,
                "m2_referencia": 20,
                "precio_m2_adicional": 55.0,
            },
            "estandar": {
                "precio_base": 2000.0,
                "m2_referencia": 20,
                "precio_m2_adicional": 85.0,
            },
            "premium": {
                "precio_base": 3500.0,
                "m2_referencia": 20,
                "precio_m2_adicional": 130.0,
            },
        },
    },

    "habitacion_completa": {
        "nombre": "Reforma de Habitacion",
        "descripcion": "Reforma de habitacion/dormitorio con opcion de armario empotrado",
        "incluye": [
            "Suelo laminado/vinilico",
            "Pintura de paredes y techo",
            "Rodapies",
            "Puntos de luz (1-2 uds)",
        ],
        "opciones": {
            "armario_empotrado": {
                "descripcion": "Armario empotrado a medida (2.5m ancho)",
                "precios": {
                    "basico": 500.0,
                    "estandar": 950.0,
                    "premium": 1500.0,
                },
            },
        },
        "precios": {
            "basico": {
                "precio_base": 800.0,
                "m2_referencia": 12,
                "precio_m2_adicional": 50.0,
            },
            "estandar": {
                "precio_base": 1400.0,
                "m2_referencia": 12,
                "precio_m2_adicional": 80.0,
            },
            "premium": {
                "precio_base": 2400.0,
                "m2_referencia": 12,
                "precio_m2_adicional": 120.0,
            },
        },
    },
}

# ============================================
# DISCLAIMERS LEGALES PROFESIONALES
# ============================================

DISCLAIMERS: Dict[str, str] = {
    "principal": """
CONDICIONES GENERALES DEL PRESUPUESTO

Este presupuesto es una ESTIMACION ORIENTATIVA basada en la informacion
proporcionada por el cliente sin visita presencial a la obra.

El presupuesto definitivo se emitira tras:
- Visita tecnica in situ
- Evaluacion del estado real de las instalaciones
- Confirmacion de mediciones exactas
- Verificacion de cumplimiento normativo
""",

    "validez": """
VALIDEZ
Este presupuesto tiene una validez de {dias_validez} dias naturales desde
su fecha de emision. Transcurrido este plazo, los precios podrian sufrir
variaciones.
""",

    "iva": """
IMPUESTOS
- IVA del 21% incluido en los precios mostrados
- El IVA se anade al total del presupuesto
- Todos los inmuebles: IVA general del 21%
""",

    "forma_pago": """
FORMA DE PAGO
Forma de pago habitual (negociable segun contrato):
- 50% al inicio de los trabajos
- 30% a mitad de obra
- 20% a la finalizacion y conformidad
""",

    "variaciones": """
POSIBLES VARIACIONES
Los precios pueden variar en funcion de:
- Estado oculto de instalaciones (tuberias, cableado, estructura)
- Necesidades no detectables sin catas previas
- Cambios normativos o de permisos municipales
- Variaciones significativas en costes de materiales
- Modificaciones solicitadas por el cliente durante la obra
""",

    "no_incluido": """
NO INCLUIDO (salvo indicacion expresa)
- Licencias y tasas municipales
- Permisos de obra
- Contenedores de escombros
- Mudanzas o vaciado previo
- Mobiliario decorativo
- Electrodomesticos no especificados
""",

    "garantias": """
GARANTIAS
Los trabajos ejecutados contaran con las garantias establecidas por la
legislacion vigente:
- Ley 38/1999 de Ordenacion de la Edificacion
- Normativa de proteccion al consumidor aplicable
- Garantia de materiales segun fabricante
""",

    "proteccion_datos": """
PROTECCION DE DATOS
Los datos personales proporcionados seran tratados conforme al Reglamento
General de Proteccion de Datos (RGPD) y la Ley Organica 3/2018 de
Proteccion de Datos Personales y garantia de los derechos digitales.
""",

    "pie": """
---
Para presupuesto definitivo, contacte con nosotros para concertar visita tecnica.
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
    Obtiene el precio de una partida especifica.

    Args:
        categoria: Categoria de trabajo (albanileria, fontaneria, etc.)
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
    """Retorna lista de todas las categorias disponibles."""
    return list(PRICING_DATA.keys())


def get_partidas_categoria(categoria: str) -> list:
    """Retorna lista de partidas de una categoria."""
    return list(PRICING_DATA.get(categoria, {}).keys())


def get_todos_paquetes() -> list:
    """Retorna lista de todos los paquetes disponibles."""
    return list(PACKAGES_DATA.keys())
