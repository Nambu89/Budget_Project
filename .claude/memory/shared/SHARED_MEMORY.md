# Memoria Compartida — Budget_Project

> Ultima actualizacion: 2026-07-05 | Por: Claude (feedback Jacobo 13/03 aplicado)

## Estado Actual del Proyecto

- **Fase**: Frontend React 19 funcional, JWT real implementado, tests OK
- **Backend**: FastAPI + Agent Framework + SQLite + JWT (PyJWT)
- **Frontend**: React 19 + Vite + React Bits en `frontend/` — build OK
- **Frontend viejo**: Streamlit ELIMINADO de `src/application/presentation/`
- **Deploy**: Railway (configurado en `railway.toml`)

## Arquitectura

- DDD: `domain/` -> `application/` -> `infrastructure/`
- 3 agentes de app: DataCollector, Calculator, Document
- 1 orquestador: BudgetCrew (flujo secuencial 4 fases)
- LLM: Azure AI Foundry / OpenAI (factory pattern)
- DB: SQLite (dev) / PostgreSQL (prod)
- Auth: JWT real con PyJWT (HS256, 30 dias, secret_key de settings)
- Frontend: React 19 + Vite (puerto 5173) proxy -> FastAPI (puerto 8000)

## Completado Recientemente

- [x] Migracion de CrewAI a Microsoft Agent Framework
- [x] Sistema multiagente de desarrollo (CLAUDE.md + agentes)
- [x] Ajuste geografico en CalculatorAgent
- [x] IVA unificado al 21%
- [x] **Migracion frontend Streamlit -> React 19 + Vite + React Bits (62 archivos)**
- [x] **JWT real implementado** (PyJWT, HS256, endpoints protegidos con Depends)
  - `src/infrastructure/api/dependencies.py` — create_jwt_token + get_current_user_id
  - Endpoints protegidos: guardar, mis-presupuestos, eliminar, /me
  - user_id viene del JWT, no de query params ni body
- [x] **50 tests arreglados** (79 passed, 0 failed, 44 skipped)
  - IVA hardcoded a 21% en assertions
  - PropertyType sin iva_aplicable/es_vivienda_habitual
  - PricingService/BudgetService signatures actualizadas
  - PDFGenerator: generar() -> generar_pdf()
  - Agent tests con skipif (requieren LLM API key)
- [x] **Streamlit eliminado** — archivos de presentation borrados

## Completado 2026-07-05 (feedback Jacobo 13/03)

- [x] Paso 1: "Fontanerias" revertido a "Banos" (PropertyForm.tsx)
- [x] 9 escapes unicode literales eliminados de JSX (Step4, EconomicSummary, PriceRangeTeaser, BudgetBreakdown)
- [x] Fix [object Object] en errores API (client.ts)
- [x] Fix PDF adjunto corrupto en email (routes/email.py: b64decode explicito)
- [x] Datos fiscales QUEBRADEROS 360 S.L en cabecera PDF junto a logo (pdf_generator.py)
- [x] Test display_name actualizado (35 passed)

## En Progreso

- [ ] Testing E2E del frontend contra FastAPI
- [ ] Redeploy Railway con estos fixes (capturas de Jacobo eran de version vieja)
- [ ] Deploy frontend en Railway (contenedor separado)

## Backlog

- [ ] Tests de integracion completos
- [ ] Documentacion completa de la API
- [ ] Optimizacion de prompts del CalculatorAgent
- [ ] Dashboard de metricas
- [ ] Responsive testing en dispositivos reales

## Problemas Conocidos

- Entorno LOCAL tiene agent-framework 1.9.0 pero el proyecto pinnea 1.0.0b260123 (1.9.0 no exporta ChatAgent) — tests que importan src.application fallan en local; deploy OK con el pin. No downgradear global sin revisar otros proyectos.
- TypeScript `erasableSyntaxOnly` activado por defecto en Vite 7
- Email presupuestos: funciona via Resend como SMTP relay (confirmado por Fernando 2026-07-05); codigo usa smtplib en email_service.py

## Decisiones Arquitectonicas

| Fecha | Decision | Contexto |
|-------|----------|----------|
| 2026-03 | Microsoft Agent Framework sobre CrewAI | CrewAI limitaba la integracion con Azure AI Foundry |
| 2026-03 | IVA unico 21% | Fase 1 simplificada, IVA reducido en fases futuras |
| 2026-03 | React 19 + Vite + React Bits para frontend | Streamlit limitaba personalizacion UX/UI |
| 2026-03 | CSS Modules + design tokens (no Tailwind) | Control total, glassmorphism custom, sin dependencia extra |
| 2026-03 | useReducer para wizard state (no Redux) | Complejidad adecuada, 5 pasos, todo local |
| 2026-03 | JWT real con PyJWT (HS256) | Reemplaza fake tokens, endpoints protegidos con Depends() |
| 2026-03 | user_id del JWT, no del body/query | Seguridad: evita que un usuario actue como otro |
