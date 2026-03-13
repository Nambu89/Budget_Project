# Budget Calculator - Calculadora de Presupuestos de Reformas

Sistema de generacion de presupuestos para reformas y obras en Espana, con frontend moderno en React y backend en FastAPI.

## Descripcion

Aplicacion web que permite generar presupuestos profesionales para reformas de viviendas, pisos, locales y oficinas. Flujo en 4 pasos:

1. **Tipo de inmueble** - Seleccion del inmueble y sus caracteristicas
2. **Trabajos** - Seleccion de paquetes y partidas individuales
3. **Datos de contacto** - Nombre, DNI, email y telefono
4. **Presupuesto** - Desglose completo + descarga PDF + envio por email/WhatsApp

### Caracteristicas principales

- Presupuestos para viviendas, pisos, locales y oficinas
- Tres niveles de calidad: Basico, Estandar y Premium
- Paquetes predefinidos (bano completo, reforma integral vivienda/local/aseo)
- Partidas individuales por categoria (albanileria, fontaneria, electricidad, pintura, carpinteria)
- Unidades visibles en cada partida (m2, ml, ud, punto)
- Campo de notas y asistencia de albanileria en electricidad
- IVA 21% general
- Markup 15% en partidas individuales (no en paquetes)
- Redondeo al alza 5% (interno, no visible en PDF)
- Generacion de PDF profesional con datos del cliente y DNI
- Envio por email con PDF adjunto
- Envio por WhatsApp con resumen del presupuesto
- Sin necesidad de registro

## Tecnologias

### Backend
- **Python 3.10+**
- **FastAPI** - API REST
- **Pydantic v2** - Validacion de datos
- **ReportLab** - Generacion de PDFs
- **SQLAlchemy 2.0** - Base de datos (SQLite dev / PostgreSQL prod)
- **Loguru** - Logging
- **PyJWT** - Autenticacion JWT (para endpoints protegidos)
- **Pytest** - Testing (79 tests)

### Frontend
- **React 19** - UI
- **Vite 7** - Build tool
- **TypeScript** - Tipado estatico
- **CSS Modules** - Estilos (design tokens, sin Tailwind)
- **React Bits** - Animaciones (Aurora, SplitText, GradientText, ShinyText)
- **Lucide React** - Iconos

## Estructura del Proyecto

```
Budget_Project/
├── src/                          # Backend Python (DDD)
│   ├── domain/
│   │   ├── enums/                # PropertyType, QualityLevel, WorkCategory
│   │   └── models/               # Budget, Project, Customer, BudgetItem
│   ├── application/
│   │   ├── agents/               # Agentes IA (DataCollector, Calculator, Document)
│   │   ├── crews/                # BudgetCrew (orquestador)
│   │   └── services/             # BudgetService, PricingService, EmailService
│   ├── infrastructure/
│   │   ├── api/                  # FastAPI routes + schemas
│   │   ├── pdf/                  # Generador PDF (ReportLab)
│   │   ├── database/             # SQLAlchemy
│   │   └── llm/                  # Clientes Azure/OpenAI
│   └── config/
│       ├── settings.py           # Configuracion (Pydantic)
│       └── pricing_data.py       # Base de datos de precios
├── frontend/                     # React 19 + Vite
│   └── src/
│       ├── components/           # Steps, forms, budget, wizard, layout, UI
│       ├── context/              # WizardContext (useReducer)
│       ├── api/                  # Fetch wrappers
│       ├── types/                # TypeScript types
│       └── styles/               # CSS Modules + tokens
├── tests/
│   ├── unit/                     # Tests unitarios
│   └── integration/              # Tests de integracion
└── README.md
```

## Instalacion

### Backend

```bash
# Clonar y entrar al proyecto
git clone <repo-url>
cd Budget_Project

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### Frontend

```bash
cd frontend
npm install
```

## Uso

### Desarrollo

```bash
# Backend (puerto 8000)
uvicorn src.infrastructure.api.main:app --reload

# Frontend (puerto 5173, proxy a backend)
cd frontend
npm run dev
```

### Produccion

```bash
# Build frontend
cd frontend
npm run build

# Backend sirve el frontend desde dist/
```

## Testing

```bash
# Tests backend
pytest tests/ -v

# Con cobertura
pytest --cov=src --cov-report=html
```

## Paquetes Disponibles

| Paquete | Descripcion |
|---------|-------------|
| `bano_completo` | Reforma integral de bano completo |
| `reforma_integral_vivienda` | Reforma completa de vivienda |
| `reforma_integral_local` | Reforma de local/oficina |
| `reforma_integral_aseo` | Reforma integral de aseo basico |

## Categorias de Partidas

| Categoria | Ejemplos |
|-----------|----------|
| Albanileria | Demolicion, tabiques, alicatado, solado, recrecido |
| Fontaneria | Puntos de agua, desagues, griferia, sanitarios |
| Electricidad | Puntos de luz, enchufes, cuadro electrico, tomas |
| Pintura | Pintura plastica, esmalte, gotele, lacado |
| Carpinteria | Suelos, puertas, armarios, rodapie, ventanas |

## Reglas de Negocio

- **IVA**: 21% general (todos los inmuebles)
- **Markup**: 15% sobre partidas individuales (NO sobre paquetes)
- **Redondeo al alza**: 5% sobre el total (interno, no visible al cliente)
- **Validez**: 30 dias desde emision

## Licencia

Proyecto privado. Desarrollado para ISI Obras y Servicios.

## Contacto

- **Email**: fernando.prada@proton.me

---

Fernando Prada - AI Engineer
