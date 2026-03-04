# Changelog — Budget_Project

Historial cronologico de todas las sesiones de trabajo del equipo multiagente.

---

## [2026-03-04] — Backend Dev (JWT real + 50 tests arreglados + limpieza)
- **JWT real implementado** (reemplaza fake tokens):
  - `requirements.txt` — anadido PyJWT>=2.8.0
  - `src/infrastructure/api/dependencies.py` — NUEVO: create_jwt_token() + get_current_user_id()
  - `src/infrastructure/api/routes/auth.py` — JWT en login/register, /me con Depends()
  - `src/infrastructure/api/routes/presupuesto.py` — guardar/listar/eliminar protegidos con JWT
  - `src/infrastructure/api/schemas/request.py` — eliminado user_id de GuardarPresupuestoRequest
  - Corregido acceso a dict en auth routes (user["id"] en vez de user.id)
- **50 tests arreglados** (79 passed, 0 failed, 44 skipped):
  - `tests/unit/test_models.py` — eliminados tests de PropertyType.iva_aplicable/es_vivienda_habitual, IVA a 21%
  - `tests/unit/test_services.py` — reescrito: signatures actualizadas, IVA 21%, dict keys correctas
  - `tests/unit/test_pdf.py` — generar() -> generar_pdf()
  - `tests/integration/test_agents_communication.py` — skipif no LLM configurado
  - `tests/integration/test_llm_connection.py` — skipif en get_provider_info
- **Limpieza de archivos obsoletos**:
  - Eliminado Streamlit presentation completo
  - Eliminado .streamlit/, railway.toml (Streamlit), scripts obsoletos
  - Eliminados __pycache__ dirs

## [2026-03-04] — Frontend Dev (migracion React completa)
- Migracion completa de Streamlit a React 19 + Vite + React Bits
- 62 archivos creados en `frontend/`
- Estructura:
  - `frontend/src/components/reactbits/` — 7 componentes animacion
  - `frontend/src/components/layout/` — Header, Footer, PageContainer
  - `frontend/src/components/wizard/` — WizardStepper, WizardNavigation, WizardLayout
  - `frontend/src/components/ui/` — GlassCard, SparkButton, AnimatedNumber, LoadingSpinner, Modal
  - `frontend/src/components/steps/` — Step1-5
  - `frontend/src/components/budget/` — PackageSelector, ItemSelector, WorkSummary, BudgetBreakdown, EconomicSummary, PriceRangeTeaser
  - `frontend/src/components/auth/` — RegistrationGate
  - `frontend/src/components/forms/` — PropertyForm, CustomerForm
  - `frontend/src/api/` — client, catalogos, presupuesto, auth
  - `frontend/src/context/` — WizardContext, AuthContext
  - `frontend/src/types/` — domain.ts, api.ts
  - `frontend/src/hooks/` — useWizard, useAuth, useCatalogos
  - `frontend/src/utils/` — formatters, validators
  - `frontend/src/styles/` — tokens.css, global.css, 14 CSS modules
  - `frontend/src/config/` — api.ts
- Fix: ApiError class reescrita sin parameter properties (erasableSyntaxOnly)
- Build OK: `tsc --noEmit` + `vite build` sin errores

## [2026-03-04] — Sistema (inicializacion)
- Creado el sistema multiagente de desarrollo (metodologia Boris Cherny)
- Archivos creados:
  - `CLAUDE.md` — instrucciones globales del proyecto
  - `.claude/commands/` — slash commands para 4 agentes
  - `.claude/rules/` — contexto auto-cargado (project-context, memory-protocol)
  - `.claude/skills/` — workflows on-demand (plan-and-execute, end-session)
  - `.claude/memory/` — memorias compartida e individuales
