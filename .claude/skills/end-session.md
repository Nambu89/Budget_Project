---
description: Workflow de cierre de sesión — actualiza memorias compartida e individual
---

# End Session

Ejecuta este workflow al finalizar cualquier sesión de trabajo.

## Paso 1: Actualizar memoria individual

Abre `.claude/memory/agents/<tu-agente>.memory.md` y actualiza:

```markdown
## Última sesión: [FECHA]

### Completado
- [x] Descripción de lo que hiciste

### Pendiente
- [ ] Lo que queda por hacer

### Notas técnicas
- Aprendizajes o decisiones relevantes

### Problemas encontrados
- Bugs o dificultades (si las hubo)
```

## Paso 2: Actualizar memoria compartida

Abre `.claude/memory/shared/SHARED_MEMORY.md` y:

1. Mueve tareas completadas de `🔄 En Progreso` a `✅ Completado`
2. Actualiza porcentajes o estados en `🔄 En Progreso`
3. Añade nuevos items a `⚠️ Problemas Conocidos` si hay
4. Actualiza `📌 Decisiones Arquitectónicas` si tomaste alguna

## Paso 3: Añadir al changelog

Abre `.claude/memory/shared/CHANGELOG.md` y añade al INICIO del archivo:

```markdown
## [YYYY-MM-DD] — Agente [NOMBRE]
- Resumen conciso de lo realizado
- Archivos clave: `path/al/archivo.py`
```

## Paso 4: Self-correction (si aplica)

Si cometiste algún error durante la sesión:

1. Abre `CLAUDE.md` (raíz del proyecto)
2. En la sección `## Self-Correction Log`, añade:
   ```
   - [FECHA] [AGENTE] No hacer X porque causa Y. En su lugar, hacer Z.
   ```

## Confirmar

Informa al usuario: "Memorias actualizadas. Sesión cerrada."
