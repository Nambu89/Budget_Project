# CLAUDE.md — Budget_Project

## Identity
Formas parte de un equipo multiagente de desarrollo para **Budget_Project** — una calculadora de presupuestos de reformas para España. El equipo tiene 4 agentes especializados coordinados por un humano-arquitecto.

## Mission
Generar presupuestos profesionales de reformas (viviendas, pisos, locales, oficinas) con cálculos de IVA (21%), markup (15%), redondeo al alza (5%), y generación de PDF. Target: mercado español.

## Current Phase
Migración activa de CrewAI → Microsoft Agent Framework. Frontend en transición de Streamlit → React 19 + Vite + React Bits.

## Agents Available
| Comando | Agente | Especialidad |
|---------|--------|-------------|
| `/coordinator` | Coordinador | Orquesta tareas, descompone trabajo, asigna agentes |
| `/backend` | Backend Dev | Python, Pydantic, SQLAlchemy, Agent Framework, pytest |
| `/frontend` | Frontend Dev | React 19, Vite, React Bits, CSS moderno |
| `/docs` | Documentación | Docstrings, README, changelog, ADRs |

## Key Locations
- `src/domain/` — Modelos (Budget, Project, Customer) y enums
- `src/application/agents/` — Agentes de la app (DataCollector, Calculator, Document)
- `src/application/services/` — BudgetService, PricingService, AuthService, EmailService
- `src/application/crews/` — BudgetCrew (orquestador de agentes de la app)
- `src/infrastructure/` — LLM clients, PDF generator, database, API
- `src/config/` — Settings (Pydantic), pricing_data
- `tests/` — Tests unitarios e integración (pytest)
- `.claude/memory/shared/` — Memoria compartida del equipo
- `.claude/memory/agents/` — Memorias individuales de cada agente

## Principles
- **Idioma**: UI, docs y comentarios en español. Código (variables, funciones) en inglés
- **Type hints**: Obligatorios en todas las funciones
- **Docstrings**: Google style, en español
- **Logging**: Usar `loguru` (nunca `print()`)
- **Models**: Pydantic v2 BaseModel para todo dato estructurado
- **Tests**: pytest, mantener cobertura existente
- **Commits**: Conventional Commits en español (feat:, fix:, docs:, refactor:)
- **Plan Mode First**: SIEMPRE planificar antes de codificar (Shift+Tab x2)
- **Verify**: Ejecutar tests/lint/build después de cada cambio

## Self-Correction Log
<!-- Cuando cometas un error, añade la lección aquí para no repetirlo -->
<!-- Formato: - [FECHA] [AGENTE] Lección aprendida -->
- [2026-03-04] [Frontend] Vite 7 + TypeScript tiene `erasableSyntaxOnly` activado por defecto. No usar `public` parameter properties en constructores de clases. Declarar campos explicitamente.
