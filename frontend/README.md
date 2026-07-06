# Frontend — Calculadora de Presupuestos

Frontend en React 19 + Vite 7 + TypeScript. Wizard de 4 pasos que consume la
API FastAPI del backend (ver README de la raíz para la visión completa).

## Desarrollo

```bash
npm install
npm run dev      # puerto 5173, proxy /api -> http://localhost:8000
```

## Build

```bash
npm run build    # tsc + vite build -> dist/
```

## Estructura

- `src/components/steps/` — Los 4 pasos del wizard
- `src/components/budget/` — Selectores de paquetes/partidas, desglose, resumen
- `src/components/reactbits/` — Animaciones (Aurora, SplitText, CountUp...)
- `src/context/` — Estado del wizard (useReducer)
- `src/api/` — Fetch wrappers tipados
- `src/config/api.ts` — Endpoints consumidos
- `src/styles/` — CSS Modules + design tokens (`tokens.css`)

## Convenciones

- CSS Modules + design tokens, sin Tailwind
- `erasableSyntaxOnly` activo (Vite 7): no usar parameter properties de TS
- UI en español, código en inglés
