---
name: implement-us
description: Implementar una Historia de Usuario (US-IEDD) siguiendo las 10 fases del Claude Dev Kit. Uso: /implement-us US-X.Y.Z
disable-model-invocation: false
---

# Implementar Historia de Usuario

Lee y ejecuta el skill completo desde `.claude/skills/implement-us/skill.md`.

El argumento `$ARGUMENTS` contiene el identificador de la US (ej: `US-1.1.1`).

## Instrucciones

1. Leer `.claude/skills/implement-us/skill.md` para entender el flujo completo.
2. Leer `.claude/skills/implement-us/config.json` para obtener la configuración del perfil activo.
3. Leer `docs/plans/$ARGUMENTS.md` para obtener la definición de la US-IEDD.
4. Ejecutar las 10 fases en orden, leyendo cada agente desde `.claude/skills/implement-us/phases/phase-N-*.md`.
5. Respetar los puntos de STOP bloqueantes en Fase 2 (aprobación del plan) y Fase 9 (reporte en disco).

**US a implementar:** $ARGUMENTS
