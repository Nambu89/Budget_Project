# Changelog — Budget_Project

Historial cronologico de todas las sesiones de trabajo del equipo multiagente.

---

## [2026-07-06] — Claude (limpieza para entrega a Jacobo)
- **12-Factor Agents aplicado** (Factor 2 own your prompts): prompts centralizados en `src/application/agents/prompts.py`; los 3 agentes importan de ahi. calculator_agent 346 -> 214 lineas
- **Mapeos de validacion** de DataCollector a constantes de modulo (MAPEO_TIPO_INMUEBLE, MAPEO_CALIDAD, MAPEO_CATEGORIA)
- **Bug latente arreglado**: `Project` no tiene campo `num_habitaciones` (es `habitaciones`) — crear_presupuesto lo descartaba silenciosamente (Pydantic extra=ignore) y calcular_estimaciones_inteligentes crasheaba
- **Codigo muerto eliminado**: PriceRangeTeaser.tsx, endpoints auth/guardar sin uso en frontend config, extract_pdf.py, rewrite_pricing.py, carpetas vacias auth/pages
- **Docs**: README raiz actualizado (agentes IA + tabla, deploy Railway real con URLs, nota pin agent-framework), frontend/README.md reescrito (era template Vite), .env.example creado, .gitignore ampliado
- Verificado: 79 passed 44 skipped, build OK, E2E produccion tras redeploy
- Commit 4954fa9

## [2026-07-05] — Claude (E2E contra produccion real)
- URL frontend produccion: https://presupuestos.isiobrasyservicios.com (dominio custom, proxy /api al backend)
- E2E Playwright headed 27/27 PASS contra produccion real (frontend + backend desplegados)
- Video grabado: `e2e_produccion.webm` en raiz del proyecto (no commitear)
- Verificado build nuevo desplegado: favicon.png/ico live, label Banos, dropdown Fontaneria, PDF con datos fiscales, WhatsApp, sin errores consola
- Falsa alarma TOTAL 0,00€: CountUp usa IntersectionObserver (threshold 0.3) — anima al entrar al viewport; tras scroll muestra total correcto (verificado 6.987,75€)
- Fix aplicado (1a2e368): CountUp anima al montar — TOTAL visible sin scroll. Verificado en produccion (6.987,75€ sin scrollear)

## [2026-07-05] — Claude (deploy + E2E Playwright + 2 bugs criticos backend)
- **Deploy**: 3 commits pusheados a main (6656b8f feedback+favicon, 36e0aa9 WorkCategory, cfb97e5 paquetes dict) — Railway auto-deploy OK
- **Bug critico 1**: `data_collector_agent.py` referenciaba WorkCategory.COCINA/CLIMATIZACION (eliminados del enum) — AttributeError en CADA calculo. Este era el verdadero "punto 4 no funciona" de Jacobo
- **Bug critico 2**: `calculator_agent.py` esperaba paquetes list[str] pero el frontend envia dicts {id, cantidad, metros} — 'unhashable type: dict'
- **Bug precio**: paquete sin metros usaba m2 de TODO el inmueble (bano en piso 80m2 = 43.000€). Ahora: paquetes precio_base usan m2_referencia (bano 5.500€), solo reformas integrales usan m2 proyecto (`budget_service.py`, `pricing_service.py`)
- **E2E Playwright 27/27 PASS**: frontend local (codigo nuevo, vite proxy) + backend PRODUCCION. Flujo completo usuario: 4 pasos, dropdown Fontaneria, m2 negrita, PDF descargado con datos fiscales QUEBRADEROS, WhatsApp wa.me OK, modal email OK, sin errores consola
- Backend produccion verificado: https://budgetproject-production.up.railway.app (calculo OK, PDF OK, email 422 con base64 invalido)
- URL del frontend desplegado NO localizada (Railway CLI sin login) — pendiente verificar con Fernando
- Nota: mojibake aparente en curl era encoding cp1252 de la consola Windows, API correcta

## [2026-07-05] — Claude (favicon multi-formato)
- `frontend/public/` — favicon.png (64px), apple-touch-icon.png (180px), favicon.ico (16/32/48) generados desde `Logo/Favicon.jpeg`; eliminado favicon.jpeg (JPEG no soportado como favicon en Safari)
- `frontend/index.html` — links icon actualizados (ico + png + apple-touch-icon)
- Nota: email de presupuestos confirmado funcionando via Resend (SMTP relay); el fix b64decode sigue aplicando

## [2026-07-05] — Claude (feedback Jacobo 13/03: fixes restantes)
- **Paso 1 revertido**: label "Fontanerías" -> "Baños" (cambio mal aplicado; el rename correcto era el desplegable de partidas, ya hecho en 8d0c3ae)
  - `frontend/src/components/forms/PropertyForm.tsx`
- **Unicode escapado eliminado** (9 escapes literales `\uXXXX` en JSX que se renderizaban tal cual):
  - `frontend/src/components/steps/Step4BudgetFinal.tsx`, `budget/EconomicSummary.tsx`, `budget/PriceRangeTeaser.tsx`, `budget/BudgetBreakdown.tsx`
- **Fix `[object Object]`**: `frontend/src/api/client.ts` — detail no-string ya no se pasa como message
- **Fix email con PDF corrupto**: `src/infrastructure/api/routes/email.py` — pdf_bytes ahora str base64 + b64decode explícito (Pydantic `bytes` encodeaba el base64 como utf-8, adjunto ilegible)
- **Datos fiscales en PDF**: `src/infrastructure/pdf/pdf_generator.py` — cabecera con tabla logo (izq) + QUEBRADEROS 360 S.L / CIF B26686212 / Tomás Bretón 7 1ºH, 50005 Zaragoza (der). Verificado renderizando PDF real.
- **Test actualizado**: `tests/unit/test_models.py` — display_name FONTANERIA "Baño" -> "Fontanería" (35 passed)
- **Verificado**: build frontend OK (tsc + vite). Suite completa backend bloqueada en local: agent-framework instalado es 1.9.0, pin del proyecto 1.0.0b260123 (sin ChatAgent en 1.9.0) — solo afecta entorno local, deploy usa el pin.

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
