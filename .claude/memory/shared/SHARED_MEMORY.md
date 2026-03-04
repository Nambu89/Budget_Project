# Memoria Compartida — Budget_Project

> Ultima actualizacion: 2026-03-04 | Por: Backend Dev (JWT real + tests)

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

## En Progreso

- [ ] Testing E2E del frontend contra FastAPI
- [ ] Conectar descarga PDF y envio email (Step 5 botones)
- [ ] Deploy frontend en Railway (contenedor separado)

## Backlog

- [ ] Tests de integracion completos
- [ ] Documentacion completa de la API
- [ ] Optimizacion de prompts del CalculatorAgent
- [ ] Dashboard de metricas
- [ ] Responsive testing en dispositivos reales

## Problemas Conocidos

- `requirements.txt` referencia `agent-framework==1.0.0b251120` (beta)
- TypeScript `erasableSyntaxOnly` activado por defecto en Vite 7
- Step 5 botones "Descargar PDF" y "Enviar email" aun no conectados a API

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
