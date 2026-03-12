# 🏗️ Budget Calculator - Calculadora de Presupuestos de Reformas

Sistema inteligente de generación de presupuestos para reformas y obras en España, desarrollado con **CrewAI** y **Azure AI Foundry**.

## 📋 Descripción

Esta aplicación permite generar presupuestos profesionales para reformas de viviendas, locales y oficinas. Utiliza un sistema multi-agente basado en CrewAI que:

1. **Valida** los datos del proyecto
2. **Calcula** precios aplicando reglas de negocio españolas
3. **Genera** documentos PDF profesionales

### Características principales

- ✅ Presupuestos interactivos para viviendas, pisos, locales y oficinas (soporta nº de plantas, habitaciones, salas, aseos)
- ✅ Tres niveles de calidad: Básico, Estándar y Premium
- ✅ Paquetes predefinidos inteligentes filtrados por tipo de inmueble
- ✅ Partidas individuales personalizables (ej. checkbox de asistencia de albañilería)
- ✅ Cálculo automático de IVA (21% general en FASE 1)
- ✅ Markup del 15% en partidas individuales
- ✅ Generación de PDF profesional transparente (ocultando redondeos internos)
- ✅ Interfaces separadas: APIs potentes en Backend y transición hacia React moderno en Frontend

## 🛠️ Tecnologías

- **Python 3.10+**
- **CrewAI** - Orquestación de agentes IA
- **Azure AI Foundry** - Modelos de lenguaje (GPT-4, GPT-5-mini)
- **Streamlit** - Interfaz de usuario web
- **ReportLab** - Generación de PDFs
- **Pydantic** - Validación de datos
- **Pytest** - Testing

## 📁 Estructura del Proyecto

```
budget_calculator/
├── src/
│   ├── application/
│   │   ├── agents/              # Agentes CrewAI
│   │   │   ├── data_collector_agent.py
│   │   │   ├── calculator_agent.py
│   │   │   └── document_agent.py
│   │   ├── crews/               # Orquestación
│   │   │   └── budget_crew.py
│   │   └── services/            # Lógica de negocio
│   │       ├── budget_service.py
│   │       └── pricing_service.py
│   ├── config/
│   │   ├── settings.py          # Configuración
│   │   └── pricing_data.py      # Base de datos de precios
│   ├── domain/
│   │   ├── enums/               # Enumeraciones
│   │   └── models/              # Modelos de datos
│   ├── infrastructure/
│   │   ├── llm/                 # Clientes LLM
│   │   │   ├── azure_client.py
│   │   │   ├── openai_client.py
│   │   │   └── llm_factory.py
│   │   └── pdf/                 # Generador de PDF
│   │       └── pdf_generator.py
│   └── presentation/
│       ├── app.py               # Aplicación Streamlit
│       ├── pages/               # Páginas de la app
│       └── components/          # Componentes UI
├── tests/
│   ├── unit/                    # Tests unitarios
│   └── integration/             # Tests de integración
├── .env.example                 # Ejemplo de configuración
├── requirements.txt             # Dependencias
├── run_tests.py                 # Script de testing
└── README.md
```

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/budget_calculator.git
cd budget_calculator
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de Azure AI Foundry:

```env
# Proveedor LLM
LLM_PROVIDER=azure

# Azure AI Foundry
AZURE_OPENAI_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=tu-api-key-aqui
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-mini
```

## 💻 Uso

### Ejecutar la aplicación web

```bash
streamlit run src/presentation/app.py
```

La aplicación estará disponible en `http://localhost:8501`

### Uso programático

```python
from src.application.crews import BudgetCrew

# Crear crew
crew = BudgetCrew()

# Datos del formulario
datos = {
    "tipo_inmueble": "piso",
    "metros_cuadrados": 80.0,
    "calidad": "estandar",
    "es_vivienda_habitual": True,
    "habitaciones": 3,
    "banos": 2,
    "paquetes": ["bano_completo"],
}

# Datos del cliente
cliente = {
    "nombre": "Juan García",
    "email": "juan@email.com",
    "telefono": "666 123 456",
    "direccion_obra": "Calle Mayor 1, Madrid",
}

# Procesar presupuesto
resultado = crew.procesar_presupuesto(
    datos_formulario=datos,
    datos_cliente=cliente,
    generar_pdf=True,
)

if resultado["exito"]:
    print(f"Total: {resultado['presupuesto'].total}€")
    
    # Guardar PDF
    with open("presupuesto.pdf", "wb") as f:
        f.write(resultado["pdf_bytes"])
```

## 🧪 Testing

### Ejecutar todos los tests

```bash
python run_tests.py
```

### Ejecutar tests específicos

```bash
# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v

# Con cobertura
pytest --cov=src --cov-report=html
```

## 📊 Paquetes Disponibles

| Paquete | Descripción | Precio Base (Estándar) |
|---------|-------------|------------------------|
| `bano_completo` | Reforma integral de baño completo | 5.500€ + 500€/m² adicional |
| `cocina_completa` | Reforma integral de cocina completa | 10.000€ + 600€/m² adicional |
| `reforma_integral_vivienda` | Reforma completa vivienda | 950€/m² |
| `reforma_integral_local` | Reforma local/oficina | 700€/m² |
| `reforma_integral_aseo` | Reforma integral de aseo básico | 3.000€ + 300€/m² adicional |

## 💰 Reglas de Negocio

- **Markup**: 15% sobre partidas individuales (NO sobre paquetes)
- **Redondeo al alza**: 5% sobre el total
- **IVA Reducido**: 10% para vivienda habitual
- **IVA General**: 21% para resto de inmuebles
- **Validez**: 30 días desde emisión

## 🔧 Configuración Avanzada

### Variables de entorno disponibles

| Variable | Descripción | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Proveedor LLM (azure/openai) | `azure` |
| `AZURE_OPENAI_ENDPOINT` | Endpoint de Azure | - |
| `AZURE_OPENAI_API_KEY` | API Key de Azure | - |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Nombre del deployment | `gpt-5-mini` |
| `IVA_GENERAL` | IVA general (%) | `21` |
| `IVA_REDUCIDO` | IVA reducido (%) | `10` |
| `MARKUP_PARTIDAS_INDIVIDUALES` | Markup partidas (%) | `15` |
| `REDONDEO_ALZA` | Redondeo al alza (%) | `5` |
| `VALIDEZ_PRESUPUESTO_DIAS` | Días de validez | `30` |

## 📄 Licencia

Este proyecto es privado y confidencial. Desarrollado para Easy Obras y Servicios.

## 👥 Contacto

- **Email**: fernando.prada@proton.me

---

Fernando Prada - AI Engineer - Senior Consultor

Desarrollado usando CrewAI