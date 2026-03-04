---
description: Protocolo de memoria compartida e individual — auto-cargado en cada sesión
---

# Protocolo de Memoria

## Al INICIAR cada sesión

1. **Lee la memoria compartida**: `.claude/memory/shared/SHARED_MEMORY.md`
   - Revisa el estado actual del proyecto
   - Identifica tareas en progreso y completadas
   - Revisa problemas conocidos
2. **Lee tu memoria individual**: `.claude/memory/agents/<tu-agente>.memory.md`
   - Revisa tu última sesión
   - Retoma tareas pendientes
   - Revisa tus notas técnicas
3. **Confirma al usuario** que has leído ambas memorias y resume brevemente el estado

## Al FINALIZAR cada sesión

Ejecuta el skill `end-session` o sigue estos pasos manualmente:

1. **Actualiza tu memoria individual** (`.claude/memory/agents/<tu-agente>.memory.md`):
   - Fecha de la sesión
   - Qué hiciste (resumen conciso)
   - Qué queda pendiente
   - Problemas encontrados
   - Notas técnicas relevantes

2. **Actualiza la memoria compartida** (`.claude/memory/shared/SHARED_MEMORY.md`):
   - Mueve tareas de "En Progreso" a "Completadas" si terminaste
   - Actualiza "En Progreso" con tu avance
   - Añade nuevos "Problemas Conocidos" si los hay
   - Actualiza "Decisiones" si tomaste alguna decisión arquitectónica

3. **Añade entrada al changelog** (`.claude/memory/shared/CHANGELOG.md`):
   ```
   ## [FECHA] — [AGENTE]
   - Resumen de lo realizado
   - Archivos modificados/creados
   ```

4. **Self-correction** (si aplica):
   - Si cometiste un error durante la sesión, añade la lección al `CLAUDE.md` raíz en la sección "Self-Correction Log"

## Reglas de Escritura
- Sé **conciso**: cada entrada de memoria debe ser breve y útil
- Usa **bullet points**, no párrafos largos
- Incluye **paths de archivos** cuando referencien cambios
- Marca las tareas con `[ ]` (pendiente), `[/]` (en progreso), `[x]` (completada)
- Nunca borres historial, solo añade y actualiza estados
