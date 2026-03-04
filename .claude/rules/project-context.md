---
description: Contexto técnico del proyecto Budget_Project — auto-cargado en cada sesión
---

# Contexto del Proyecto

## Stack Backend
- Python 3.10+ (3.11 o 3.12 recomendado)
- Microsoft Agent Framework (`agent_framework.ChatAgent`)
- Pydantic v2 + pydantic-settings
- SQLAlchemy 2.0+ (SQLite dev / PostgreSQL prod)
- ReportLab (generación PDF)
- Loguru (logging)
- FastAPI (API REST en `src/infrastructure/api/`)

## Stack Frontend (en transición)
- Actual: Streamlit (`src/application/presentation/streamlit_app.py`)
- Target: React 19 + Vite + React Bits (animaciones modernas)

## LLM
- Azure AI Foundry o OpenAI directo (configurable via `LLM_PROVIDER`)
- Factory pattern en `src/infrastructure/llm/chat_client_factory.py`
- Modelos: GPT-5-mini (estimaciones), GPT-4 (tareas complejas)

## Arquitectura (DDD)
```
src/
├── domain/        → Modelos puros (Budget, Project, Customer, BudgetItem)
│   ├── models/    → Pydantic BaseModel
│   └── enums/     → PropertyType, QualityLevel, WorkCategory
├── application/   → Lógica de negocio
│   ├── agents/    → Agentes IA de la app (DataCollector, Calculator, Document)
│   ├── crews/     → Orquestador (BudgetCrew)
│   ├── services/  → BudgetService, PricingService, AuthService, EmailService
│   └── presentation/ → UI Streamlit (páginas, componentes, estilos)
├── infrastructure/ → Implementaciones técnicas
│   ├── llm/       → Clientes Azure/OpenAI con factory
│   ├── pdf/       → Generador PDF (ReportLab)
│   ├── database/  → SQLAlchemy engine + models
│   ├── api/       → FastAPI routes + schemas
│   └── logging/   → Métricas y logging
└── config/        → Settings (Pydantic), pricing_data
```

## Reglas de Negocio Clave
- IVA: 21% general (todos los inmuebles)
- Markup: 15% sobre partidas individuales (NO sobre paquetes)
- Redondeo al alza: 5% sobre el total
- Validez presupuesto: 30 días
- Paquetes: baño_completo, cocina_completa, reforma_integral_vivienda, reforma_integral_local

## Convenciones
- Variables/funciones: snake_case en inglés
- Clases: PascalCase
- UI + docs + comentarios: español
- Imports: relativos dentro de src/, absolutos para external
- Error handling: try/except con logger.exception()
