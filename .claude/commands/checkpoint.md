---
name: checkpoint
description: Guardar estado actual de la sesión en session-current.md. Usar proactivamente al completar tareas importantes.
disable-model-invocation: false
---

# Guardar Checkpoint de Sesión

Actualiza `session-current.md` con el estado actual del trabajo.

## Cuándo ejecutar este comando

Ejecutar **proactivamente** (sin esperar que el usuario lo pida) en estos momentos:
- Al completar una tarea o subtarea significativa
- Después de tomar una decisión de diseño o arquitectura importante
- Antes de una operación riesgosa (reset, refactor grande, cambio de enfoque)
- Al terminar de implementar una fase de una US-IEDD
- Cuando el usuario dice "listo", "ok", "seguimos", "next" o similar
- Cada ~30 minutos de trabajo continuo

## Instrucciones

### 1. Leer el estado actual

Leer `~/.claude/projects/-Users-victor-PycharmProjects-ataraxiadive/memory/session-current.md`
para entender qué había antes y no perder información previa.

### 2. Escribir el checkpoint

Agregar una nueva entrada al final de `session-current.md` con este formato:

```markdown
---

### ⚡ Checkpoint: <YYYY-MM-DD HH:MM>

**Branch:** <branch actual>
**US/Tarea en curso:** <identificador si aplica, ej: US-1.2.1 o "diseño context-map">

#### ✅ Completado en este bloque
- <item concreto completado>
- <item concreto completado>

#### 🔍 Decisiones tomadas
- <decisión y su razón, si hubo alguna>

#### 🎯 Estado actual
<Una línea describiendo dónde quedó el trabajo exactamente>

#### 🚀 Próximo paso inmediato
<El próximo paso concreto, suficientemente específico para retomarlo sin contexto>
```

### 3. Confirmar sin interrumpir

Después de guardar, mostrar al usuario **una sola línea**:
> `💾 Checkpoint guardado — <descripción de una línea de qué se guardó>`

No generar output largo. No pedir confirmación. Continuar con el trabajo.

## Notas

- **TODO en español**
- Ser específico: "implementé el aggregate Performance con sus invariantes" es útil, "trabajé en el código" no lo es
- Si no hubo decisiones relevantes, omitir esa sección
- El checkpoint no reemplaza el sistema de memoria (MEMORY.md) — ese es para conocimiento persistente entre proyectos; este es para el estado de la sesión actual
