# Memoria — Agente Backend

## Ultima sesion: 2026-03-04 (JWT real + tests + limpieza)

### Completado
- [x] Agente backend inicializado
- [x] JWT real implementado (PyJWT, HS256, 30 dias)
  - `dependencies.py`: create_jwt_token + get_current_user_id
  - Endpoints protegidos: guardar, mis-presupuestos, eliminar, /me
  - user_id del JWT (no body/query)
  - Auth routes: acceso a dict corregido (user["id"])
- [x] 50 tests arreglados (79 passed, 0 failed, 44 skipped)
  - IVA fijo 21% en todas las assertions
  - Signatures de PricingService/BudgetService actualizadas
  - PDFGenerator: generar() -> generar_pdf()
  - Agent tests: skipif sin LLM API key
- [x] GuardarPresupuestoRequest ya no tiene user_id (viene del JWT)
- [x] Limpieza de Streamlit y archivos obsoletos

### Pendiente
- [ ] Endpoint PDF accesible desde React (funciona pero no probado E2E)
- [ ] Endpoint email accesible desde React
- [ ] Deploy en Railway (backend container)

### Notas tecnicas
- Stack: Python 3.10+, Pydantic v2, SQLAlchemy, Agent Framework, ReportLab, PyJWT
- JWT: HS256, secret_key de settings.py, payload {sub, email, exp, iat}
- auth_service.register/login retornan dict (no Pydantic model)
- calcular_totales retorna keys: subtotal, base_sin_redondeo, base_con_redondeo, importe_redondeo, redondeo_porcentaje, iva_porcentaje, iva_importe, total
- PricingService.calcular_precio_unitario(codigo_partida, calidad) — codigo_partida es key top-level (categoria)
- PricingService.crear_partida(categoria: WorkCategory, partida: str, ...) — la forma correcta de obtener precios
- CORS: allow_origins=["*"] en main.py

### Problemas encontrados
- auth_service retorna dict pero auth routes usaban dot-access (user.id) — corregido a user["id"]
- PricingService pricing_data keyed by category, not partida name
