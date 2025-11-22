"""
Base de datos de precios para reformas en España (2024-2025).

Este módulo contiene todos los precios de referencia para:
- Partidas individuales por categoría
- Paquetes completos (baño, cocina, reforma integral)
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
        "alicatado_paredes": {
            "basico": 30.0,
            "estandar": 47.5,
            "premium": 80.0,
            "unidad": "m2",
            "descripcion": "Alicatado de paredes con azulejo (material + mano de obra)",
        },
        "solado_porcelanico": {
            "basico": 30.0,
            "estandar": 47.5,
            "premium": 80.0,
            "unidad": "m2",
            "descripcion": "Solado con baldosa porcelánica (material + mano de obra)",
        },
        "solado_vinilico": {
            "basico": 20.0,
            "estandar": 35.0,
            "premium": 52.5,
            "unidad": "m2",
            "descripcion": "Solado con suelo vinílico (material + mano de obra)",
        },
        "alisado_paredes": {
            "basico": 13.5,
            "estandar": 20.0,
            "premium": 30.0,
            "unidad": "m2",
            "descripcion": "Alisado y enyesado de paredes",
        },
        "pintura": {
            "basico": 9.0,
            "estandar": 15.0,
            "premium": 30.0,
            "unidad": "m2",
            "descripcion": "Pintura de paredes (incluye imprimación)",
        },
        "demolicion": {
            "basico": 17.5,
            "estandar": 17.5,
            "premium": 17.5,
            "unidad": "m2",
            "descripcion": "Demolición y desescombro (precio único)",
        },
        "falso_techo_pladur": {
            "basico": 22.5,
            "estandar": 35.0,
            "premium": 52.5,
            "unidad": "m2",
            "descripcion": "Falso techo de pladur con estructura",
        },
        "tabique_pladur": {
            "basico": 35.0,
            "estandar": 45.0,
            "premium": 60.0,
            "unidad": "m2",
            "descripcion": "Tabique de pladur con aislamiento",
        },
    },
    
    "fontaneria": {
        "plato_ducha": {
            "basico": 400.0,
            "estandar": 700.0,
            "premium": 1600.0,
            "unidad": "ud",
            "descripcion": "Plato de ducha con instalación completa",
        },
        "mampara": {
            "basico": 250.0,
            "estandar": 450.0,
            "premium": 900.0,
            "unidad": "ud",
            "descripcion": "Mampara de ducha/bañera instalada",
        },
        "mueble_lavabo": {
            "basico": 300.0,
            "estandar": 550.0,
            "premium": 1200.0,
            "unidad": "ud",
            "descripcion": "Mueble de lavabo con lavabo y grifería",
        },
        "inodoro": {
            "basico": 200.0,
            "estandar": 400.0,
            "premium": 900.0,
            "unidad": "ud",
            "descripcion": "Inodoro completo con instalación",
        },
        "griferia_ducha": {
            "basico": 80.0,
            "estandar": 180.0,
            "premium": 450.0,
            "unidad": "ud",
            "descripcion": "Grifería de ducha/bañera",
        },
        "griferia_lavabo": {
            "basico": 60.0,
            "estandar": 120.0,
            "premium": 300.0,
            "unidad": "ud",
            "descripcion": "Grifería de lavabo",
        },
        "instalacion_fontaneria": {
            "basico": 800.0,
            "estandar": 1200.0,
            "premium": 2000.0,
            "unidad": "baño",
            "descripcion": "Instalación completa de fontanería por baño",
        },
        "calentador_agua": {
            "basico": 400.0,
            "estandar": 700.0,
            "premium": 1500.0,
            "unidad": "ud",
            "descripcion": "Calentador/termo eléctrico instalado",
        },
    },
    
    "electricidad": {
        "instalacion_completa": {
            "basico": 3500.0,
            "estandar": 4500.0,
            "premium": 7000.0,
            "unidad": "vivienda_100m2",
            "descripcion": "Instalación eléctrica completa (vivienda ~100m²)",
        },
        "punto_luz": {
            "basico": 45.0,
            "estandar": 65.0,
            "premium": 100.0,
            "unidad": "ud",
            "descripcion": "Punto de luz con cableado y mecanismo",
        },
        "cuadro_electrico": {
            "basico": 350.0,
            "estandar": 500.0,
            "premium": 800.0,
            "unidad": "ud",
            "descripcion": "Cuadro eléctrico completo con protecciones",
        },
        "toma_corriente": {
            "basico": 40.0,
            "estandar": 55.0,
            "premium": 85.0,
            "unidad": "ud",
            "descripcion": "Toma de corriente con cableado",
        },
        "punto_tv_datos": {
            "basico": 50.0,
            "estandar": 75.0,
            "premium": 120.0,
            "unidad": "ud",
            "descripcion": "Punto de TV/datos con cableado",
        },
    },
    
    "cocina": {
        "mobiliario_cocina": {
            "basico": 2500.0,
            "estandar": 4500.0,
            "premium": 9000.0,
            "unidad": "ml",
            "descripcion": "Mobiliario de cocina por metro lineal",
        },
        "encimera": {
            "basico": 150.0,
            "estandar": 300.0,
            "premium": 600.0,
            "unidad": "ml",
            "descripcion": "Encimera instalada por metro lineal",
        },
        "electrodomesticos_basicos": {
            "basico": 1200.0,
            "estandar": 2500.0,
            "premium": 5000.0,
            "unidad": "conjunto",
            "descripcion": "Pack electrodomésticos (horno, placa, campana, frigorífico)",
        },
        "fregadero_griferia": {
            "basico": 200.0,
            "estandar": 400.0,
            "premium": 800.0,
            "unidad": "ud",
            "descripcion": "Fregadero con grifería instalado",
        },
        "instalacion_gas": {
            "basico": 300.0,
            "estandar": 450.0,
            "premium": 650.0,
            "unidad": "ud",
            "descripcion": "Instalación/modificación de gas",
        },
    },
    
    "carpinteria": {
        "puerta_interior": {
            "basico": 180.0,
            "estandar": 300.0,
            "premium": 550.0,
            "unidad": "ud",
            "descripcion": "Puerta interior con marco y herrajes",
        },
        "puerta_entrada": {
            "basico": 400.0,
            "estandar": 700.0,
            "premium": 1500.0,
            "unidad": "ud",
            "descripcion": "Puerta de entrada blindada/acorazada",
        },
        "ventana_aluminio": {
            "basico": 250.0,
            "estandar": 400.0,
            "premium": 700.0,
            "unidad": "ud",
            "descripcion": "Ventana de aluminio con rotura de puente térmico",
        },
        "ventana_pvc": {
            "basico": 300.0,
            "estandar": 500.0,
            "premium": 850.0,
            "unidad": "ud",
            "descripcion": "Ventana de PVC con doble acristalamiento",
        },
        "armario_empotrado": {
            "basico": 350.0,
            "estandar": 550.0,
            "premium": 900.0,
            "unidad": "ml",
            "descripcion": "Armario empotrado por metro lineal",
        },
    },
}


# ============================================
# PAQUETES COMPLETOS
# ============================================
# Los paquetes tienen un descuento implícito vs partidas individuales

PACKAGES_DATA: Dict[str, Dict[str, Any]] = {
    "bano_completo": {
        "nombre": "Baño Completo",
        "descripcion": "Reforma integral de baño incluyendo sanitarios, alicatado, solado, fontanería y electricidad",
        "incluye": [
            "Demolición y desescombro",
            "Alicatado paredes",
            "Solado",
            "Plato de ducha o bañera",
            "Mampara",
            "Inodoro",
            "Mueble lavabo con grifería",
            "Instalación fontanería",
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
        "descripcion": "Reforma integral de cocina con mobiliario, electrodomésticos e instalaciones",
        "incluye": [
            "Demolición y desescombro",
            "Alicatado zona de trabajo",
            "Solado completo",
            "Mobiliario de cocina",
            "Encimera",
            "Electrodomésticos básicos",
            "Fregadero con grifería",
            "Instalación fontanería",
            "Instalación eléctrica cocina",
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
            "Demolición general y desescombro",
            "Tabiquería nueva (si aplica)",
            "Instalación eléctrica completa",
            "Instalación fontanería completa",
            "Solado toda la vivienda",
            "Alicatado zonas húmedas",
            "Pintura completa",
            "Carpintería interior",
            "Baño completo (1 ud)",
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
            "Demolición y desescombro",
            "Tabiquería/distribución",
            "Instalación eléctrica completa",
            "Climatización básica",
            "Solado completo",
            "Falso techo (si aplica)",
            "Pintura completa",
            "Aseo básico (1 ud)",
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
}


# ============================================
# DISCLAIMERS LEGALES PROFESIONALES
# ============================================

DISCLAIMERS: Dict[str, str] = {
    "principal": """
⚠️ CONDICIONES GENERALES DEL PRESUPUESTO

Este presupuesto es una ESTIMACIÓN ORIENTATIVA basada en la información 
proporcionada por el cliente sin visita presencial a la obra.

El presupuesto definitivo se emitirá tras:
• Visita técnica in situ
• Evaluación del estado real de las instalaciones
• Confirmación de mediciones exactas
• Verificación de cumplimiento normativo
""",

    "validez": """
📅 VALIDEZ
Este presupuesto tiene una validez de {dias_validez} días naturales desde 
su fecha de emisión. Transcurrido este plazo, los precios podrían sufrir 
variaciones.
""",

    "iva": """
💰 IMPUESTOS
• IVA del {iva_porcentaje}% NO incluido en los precios mostrados
• El IVA se añadirá al total del presupuesto
• Vivienda habitual: IVA reducido del 10% (bajo condiciones)
• Resto de inmuebles: IVA general del 21%
""",

    "forma_pago": """
💳 FORMA DE PAGO
Forma de pago habitual (negociable según contrato):
• 40% al inicio de los trabajos
• 40% a mitad de obra
• 20% a la finalización y conformidad
""",

    "variaciones": """
⚡ POSIBLES VARIACIONES
Los precios pueden variar en función de:
• Estado oculto de instalaciones (tuberías, cableado, estructura)
• Necesidades no detectables sin catas previas
• Cambios normativos o de permisos municipales
• Variaciones significativas en costes de materiales
• Modificaciones solicitadas por el cliente durante la obra
""",

    "no_incluido": """
❌ NO INCLUIDO (salvo indicación expresa)
• Licencias y tasas municipales
• Permisos de obra
• Contenedores de escombros
• Mudanzas o vaciado previo
• Mobiliario decorativo
• Electrodomésticos no especificados
""",

    "garantias": """
🛡️ GARANTÍAS
Los trabajos ejecutados contarán con las garantías establecidas por la 
legislación vigente:
• Ley 38/1999 de Ordenación de la Edificación
• Normativa de protección al consumidor aplicable
• Garantía de materiales según fabricante
""",

    "proteccion_datos": """
🔒 PROTECCIÓN DE DATOS
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