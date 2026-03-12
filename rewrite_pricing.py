import sys

with open('src/config/pricing_data.py', 'r', encoding='utf-8') as f:
    original_lines = f.readlines()

import re
content = "".join(original_lines)

new_pricing = """
PRICING_DATA: Dict[str, Dict[str, Any]] = {
    "albanileria": {
        "demolicion": {
            "basico": 17.5, "estandar": 17.5, "premium": 17.5,
            "unidad": "m2", "descripcion": "Demolicion y desescombro (m2)"
        },
        "alisado_paredes": {
            "basico": 13.5, "estandar": 20.0, "premium": 30.0,
            "unidad": "m2", "descripcion": "Alisado paredes (m2)"
        },
        "empotrado_rozas": {
            "basico": 12.0, "estandar": 18.0, "premium": 25.0,
            "unidad": "ml", "descripcion": "Empotrado/rozas para trabajos de electricidad fontaneria (ml)"
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
            "unidad": "m2", "descripcion": "Instalacion rodapie porcelanico (m2)"
        },
        "nivelacion_suelo": {
            "basico": 12.0, "estandar": 18.0, "premium": 28.0,
            "unidad": "m2", "descripcion": "Nivelacion de suelo (m2)"
        },
        "sustitucion_plato_ducha": {
            "basico": 180.0, "estandar": 280.0, "premium": 450.0,
            "unidad": "ud", "descripcion": "Sustitucion de plato de ducha (ud/s)"
        },
        "sustitucion_banera_plato_ducha": {
            "basico": 200.0, "estandar": 320.0, "premium": 500.0,
            "unidad": "ud", "descripcion": "Sustitucion de banera por plato de ducha (ud/s)"
        },
    },

    "fontaneria": {
        "ejecucion_completa_bano": {
            "basico": 800.0, "estandar": 1200.0, "premium": 2000.0,
            "unidad": "ud", "descripcion": "Ejecucion completa bano (especificar n lavabos, sanitarios, duchas/baneras)"
        },
        "ejecucion_completa_cocina": {
            "basico": 600.0, "estandar": 900.0, "premium": 1500.0,
            "unidad": "ud", "descripcion": "Ejecucion completa cocina (especificar n fregadero y electrodomesticos con agua)"
        },
        "instalacion_desague": {
            "basico": 120.0, "estandar": 180.0, "premium": 280.0,
            "unidad": "ud", "descripcion": "Instalacion de desague (ud/s)"
        },
        "instalacion_toma_suministro": {
            "basico": 100.0, "estandar": 160.0, "premium": 250.0,
            "unidad": "ud", "descripcion": "Instalacion de tomas de suministro de agua (ud)"
        },
        "instalacion_griferia_ducha": {
            "basico": 80.0, "estandar": 180.0, "premium": 450.0,
            "unidad": "ud", "descripcion": "Instalacion griferia ducha (ud/s)"
        },
        "instalacion_grifo_lavabo": {
            "basico": 60.0, "estandar": 120.0, "premium": 300.0,
            "unidad": "ud", "descripcion": "Instalacion grifo lavabo (ud/s)"
        },
        "instalacion_mueble_lavabo": {
            "basico": 300.0, "estandar": 550.0, "premium": 1200.0,
            "unidad": "ud", "descripcion": "Instalacion mueble lavabo (ud/s)"
        },
        "instalacion_inodoro": {
            "basico": 200.0, "estandar": 400.0, "premium": 900.0,
            "unidad": "ud", "descripcion": "Instalacion inodoro (ud/s)"
        },
        "instalacion_mampara": {
            "basico": 250.0, "estandar": 450.0, "premium": 900.0,
            "unidad": "ud", "descripcion": "Instalacion mampara (ud/s)"
        },
    },

    "electricidad": {
        "instalacion_completa": {
            "basico": 3500.0, "estandar": 4500.0, "premium": 7000.0,
            "unidad": "m2", "descripcion": "Instalacion completa (m2 de piso)"
        },
        "instalacion_enchufes": {
            "basico": 40.0, "estandar": 55.0, "premium": 85.0,
            "unidad": "ud", "descripcion": "Instalacion de enchufes (ud/s)"
        },
        "instalacion_interruptores": {
            "basico": 35.0, "estandar": 50.0, "premium": 80.0,
            "unidad": "ud", "descripcion": "Instalacion de interruptores (ud/s)"
        },
        "instalacion_puntos_luz": {
            "basico": 45.0, "estandar": 65.0, "premium": 100.0,
            "unidad": "ud", "descripcion": "Instalacion puntos de luz (ud/s)"
        },
        "toma_antena_tv": {
            "basico": 45.0, "estandar": 65.0, "premium": 100.0,
            "unidad": "ud", "descripcion": "Instalacion de tomas de antena TV (ud/s)"
        },
        "toma_internet": {
            "basico": 50.0, "estandar": 75.0, "premium": 120.0,
            "unidad": "ud", "descripcion": "Instalacion de tomas de internet (ud/s)"
        },
    },

    "carpinteria": {
        "instalacion_suelo_laminado": {
            "basico": 18.0, "estandar": 28.0, "premium": 45.0,
            "unidad": "m2", "descripcion": "Instalacion de suelo laminado (m2) + Rodapie"
        },
        "instalacion_vinilico_click": {
            "basico": 22.0, "estandar": 35.0, "premium": 55.0,
            "unidad": "m2", "descripcion": "Instalacion de vinilico en click (m2) + Rodapie"
        },
        "instalacion_suelo_parquet": {
            "basico": 35.0, "estandar": 55.0, "premium": 90.0,
            "unidad": "m2", "descripcion": "Instalacion de suelo de parquet (m2) + Rodapie"
        },
        "instalacion_rodapie": {
            "basico": 6.0, "estandar": 10.0, "premium": 16.0,
            "unidad": "ml", "descripcion": "Instalacion de rodapie (ml)"
        },
        "puerta_interior_abatible": {
            "basico": 120.0, "estandar": 120.0, "premium": 120.0,
            "unidad": "ud", "descripcion": "Instalacion de puerta interior de paso abatible (ud/s)"
        },
        "puerta_entrada_blindada": {
            "basico": 400.0, "estandar": 400.0, "premium": 400.0,
            "unidad": "ud", "descripcion": "Instalacion de puerta de entrada blindada abatible (ud/s) SIN IVA"
        },
        "puerta_corredera_superficie": {
            "basico": 120.0, "estandar": 120.0, "premium": 120.0,
            "unidad": "ud", "descripcion": "Instalacion de puerta corredera de superficie (ud/s) SIN IVA"
        },
        "puerta_corredera_integrada": {
            "basico": 360.0, "estandar": 360.0, "premium": 360.0,
            "unidad": "ud", "descripcion": "Instalacion de puerta corredera integrada (ud/s) SIN IVA"
        },
        "armario_medida": {
            "basico": 350.0, "estandar": 550.0, "premium": 900.0,
            "unidad": "m", "descripcion": "Instalacion de armario a medida (ancho x alto) en m"
        },
    },
}

# ============================================
# PAQUETES COMPLETOS
# ============================================
# Los paquetes tienen un descuento implicito vs partidas individuales

PACKAGES_DATA: Dict[str, Dict[str, Any]] = {
    "bano_completo": {
        "nombre": "Reforma integral bano completo",
        "descripcion": "Reforma integral de bano",
        "incluye": [
            "Demolicion y desescombro",
            "Alicatado paredes",
            "Solado",
            "Plato de ducha o banera",
            "Mampara",
            "Inodoro",
            "Mueble lavabo con griferia",
            "Instalacion fontaneria",
            "Puntos de luz",
            "Pintura techo",
        ],
        "precios": {
            "basico": {"precio_base": 3500.0, "m2_referencia": 5, "precio_m2_adicional": 350.0},
            "estandar": {"precio_base": 5500.0, "m2_referencia": 5, "precio_m2_adicional": 500.0},
            "premium": {"precio_base": 9000.0, "m2_referencia": 5, "precio_m2_adicional": 750.0},
        },
    },

    "cocina_completa": {
        "nombre": "Reforma integral cocina completa",
        "descripcion": "Reforma integral de cocina con mobiliario e instalaciones",
        "incluye": [
            "Demolicion y desescombro",
            "Alicatado zona de trabajo",
            "Solado completo",
            "Mobiliario de cocina",
            "Encimera",
            "Instalacion fontaneria",
            "Instalacion electrica cocina",
            "Pintura",
        ],
        "precios": {
            "basico": {"precio_base": 6000.0, "m2_referencia": 8, "precio_m2_adicional": 400.0},
            "estandar": {"precio_base": 10000.0, "m2_referencia": 8, "precio_m2_adicional": 600.0},
            "premium": {"precio_base": 18000.0, "m2_referencia": 8, "precio_m2_adicional": 900.0},
        },
    },

    "reforma_integral_vivienda": {
        "nombre": "Reforma integral vivienda completa",
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
            "Demolicion y desescombro",
            "Tabiqueria/distribucion",
            "Instalacion electrica completa",
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
        "descripcion": "Reforma de aseo basico",
        "incluye": [
            "Alicatado",
            "Solado",
            "Inodoro y lavabo",
            "Fontaneria",
            "Pintura",
        ],
        "precios": {
            "basico": {"precio_base": 2000.0, "m2_referencia": 3, "precio_m2_adicional": 200.0},
            "estandar": {"precio_base": 3000.0, "m2_referencia": 3, "precio_m2_adicional": 300.0},
            "premium": {"precio_base": 5000.0, "m2_referencia": 3, "precio_m2_adicional": 500.0},
        },
    },
}
"""

start_str = "PRICING_DATA: Dict[str, Dict[str, Any]] = {"
end_str = "DISCLAIMERS: Dict[str, str] = {"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_content = content[:start_idx] + new_pricing.strip() + "\n\n" + content[end_idx:]

with open('src/config/pricing_data.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Pricing data rewritten via python.")
