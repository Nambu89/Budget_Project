# Memoria — Agente Frontend

## Ultima sesion: 2026-03-04 (migracion React completa)

### Completado
- [x] Agente frontend inicializado
- [x] Planificar migracion Streamlit -> React 19 + Vite
- [x] Definir sistema de diseno (tokens CSS, componentes base)
- [x] Configurar proyecto Vite + React 19 + lucide-react
- [x] Integrar React Bits para animaciones (7 componentes)
- [x] Implementar WizardStepper con pulse + ShinyText en numero activo
- [x] Implementar 5 steps del wizard completo
- [x] API client con auth headers + modulos (catalogos, presupuesto, auth)
- [x] WizardContext (useReducer) + AuthContext
- [x] Glassmorphism cards + Aurora background
- [x] Build production OK (229KB JS gzip 72KB)

### Pendiente
- [ ] Conectar boton "Descargar PDF" a endpoint de generacion PDF
- [ ] Conectar boton "Enviar email" a endpoint de email
- [ ] Deploy en Railway (Caddy + Nixpacks, env: BACKEND_URL, NODE_ENV)
- [ ] Responsive testing en dispositivos reales
- [ ] Lazy loading de steps para optimizar bundle
- [ ] Manejo de errores de red mas robusto (retry, offline)
- [ ] Accesibilidad (aria labels, keyboard navigation en stepper)

### Notas tecnicas
- **Directorio**: `frontend/` (raiz del proyecto)
- **Vite proxy**: `/api` -> `http://localhost:8000` (vite.config.ts)
- **Design tokens**: `src/styles/tokens.css` (:root variables)
- **Font**: Rubik via Google Fonts import en tokens.css
- **Colores**: primary #F39200, bg #0f0f1a, surface rgba(255,255,255,0.05)
- **Stepper**: Circulo activo 52px con `pulse-glow` animation + ShinyText
- **TypeScript**: `erasableSyntaxOnly` activo — NO usar `public` en constructor params
- **State**: useReducer en WizardContext (SET_STEP, NEXT/PREV, SET_PROYECTO, ADD/REMOVE paquetes/partidas, SET_PRESUPUESTO, SET_CLIENTE, RESET)
- **Auth**: Token en localStorage, user serializado en localStorage
- **CSS**: Modules (.module.css) + global tokens, NO Tailwind

### Problemas encontrados
- `erasableSyntaxOnly` en tsconfig de Vite 7 impide parameter properties (`public status: number` en constructor) — solucion: declarar campos explicitamente
