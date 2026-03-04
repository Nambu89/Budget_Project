---
description: Workflow Plan → Execute → Verify (metodología Boris Cherny)
---

# Plan and Execute

Workflow para cualquier tarea no trivial. Sigue estos pasos en orden.

## Paso 1: PLAN (obligatorio)

Antes de tocar cualquier archivo de código:

1. Lee la tarea asignada
2. Analiza los archivos relevantes del proyecto
3. Presenta un plan al usuario con:
   - **Qué** vas a cambiar
   - **Dónde** (archivos específicos)
   - **Cómo** (enfoque técnico)
   - **Riesgos** potenciales
4. Espera aprobación del usuario antes de continuar

> No escribas ni una línea de código sin plan aprobado.

## Paso 2: EXECUTE

Una vez aprobado el plan:

1. Implementa los cambios siguiendo el plan exactamente
2. Si necesitas desviarte del plan, informa al usuario primero
3. Haz commits atómicos (un commit por cambio lógico)
4. Formato de commit: `tipo(scope): descripción en español`
   - Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

## Paso 3: VERIFY (obligatorio)

Después de implementar:

1. **Tests**: Ejecuta `python -m pytest tests/ -v` (backend)
2. **Lint**: Verifica que no hay errores de tipo o formato
3. **Build**: Si hay frontend, ejecuta `npm run build` para verificar
4. **Revisión manual**: Lee tus propios cambios como si fueras un reviewer
5. Si algo falla:
   - Corrige el problema
   - Vuelve a verificar
   - Documenta el error en tus notas si fue un patrón nuevo

## Al finalizar

Ejecuta el skill `end-session` para actualizar memorias.
