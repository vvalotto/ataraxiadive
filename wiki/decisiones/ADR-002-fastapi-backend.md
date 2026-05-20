---
title: "ADR-002: FastAPI como framework backend"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-002-fastapi-backend.md
estado: Aceptada
fecha: 2026-03-14
bcs_afectados: [todos]
---

# ADR-002: FastAPI como framework backend

## Decisión

FastAPI como framework Python para el backend. Pydantic v2 integrado.

## Por qué

- Desarrollador Python con experiencia; herramientas (Software Limpio, Dev Kit) calibradas para Python.
- Async nativo, coherente con el modelo de concurrencia (50 usuarios concurrentes, AC-DS-02).
- Pydantic v2 permite expresar invariantes de dominio directamente en los modelos.
- OpenAPI automático como documentación viva del contrato de API.

## Consecuencias vigentes

- Los schemas de API viven en `<bc>/api/` y son **distintos** de los modelos de `domain/` — sin acoplamiento.
- `aiosqlite` como adaptador async para SQLite (ver [[ADR-007-sqlite-persistencia-bc]]).
- Todo el stack es Python — Software Limpio cubre backend y dominio con un solo conjunto de herramientas.
- Pydantic v2 tiene breaking changes respecto a v1 — documentación externa puede ser de v1.

## ADRs relacionados

- [[ADR-006-estructura-bc-first]] — cómo se organiza el código FastAPI por BC
- [[ADR-012-rfc7807-errores-http]] — convención de errores HTTP en la API
- [[ADR-013-exception-management]] — jerarquía de excepciones que la API maneja
