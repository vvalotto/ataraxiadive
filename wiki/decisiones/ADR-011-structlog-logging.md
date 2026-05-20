---
title: "ADR-011: structlog para logging estructurado"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-011-structlog-logging.md
estado: Aceptada
fecha: 2026-03-20
bcs_afectados: [todos]
---

# ADR-011: structlog para logging estructurado

## Decisión

`structlog` como librería de logging. JSON en producción, texto legible en desarrollo. Context variables por request.

## Por qué

- FastAPI + Uvicorn producen logs en texto plano — no parseables en Google Cloud Logging / Fly.io.
- El logging estándar de Python no provee context variables (request_id, user_id) de forma ergonómica.

## Consecuencias vigentes

- Configuración en `src/shared/logging.py` — diferencia entornos por variable de env.
- `structlog.contextvars.bind_contextvars(request_id=...)` en middleware HTTP propaga el `request_id` a todos los logs del request.
- Integra con el `logging` estándar de Python — captura logs de librerías externas.

## ADRs relacionados

- [[ADR-021-fly-io]] — plataforma de producción donde los logs JSON son consumidos
