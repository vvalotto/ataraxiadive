---
title: "Vista de Decisiones"
type: vista
last_updated: "2026-05-20"
sources:
  - docs/adr/
---

# Vista de Decisiones

> El sistema visto desde su historia de razonamiento técnico.

## Propósito

Responder preguntas sobre por qué el sistema fue construido de una manera
particular. Exponer las alternativas consideradas, los trade-offs evaluados
y el estado vigente de cada decisión. Evitar que el razonamiento arquitectónico
se pierda y que futuras sesiones rehagan análisis ya realizados.

## Stakeholder principal

Arquitecto, desarrollador senior, quien va a tomar la próxima decisión técnica.

## Preguntas características

1. ¿Por qué SQLite y no PostgreSQL?
2. ¿Por qué Event Sourcing solo en dos BCs (Competencia y Notificaciones)?
3. ¿Qué alternativas se descartaron para el frontend y por qué?
4. ¿Qué ADRs gobiernan el BC Competencia?
5. ¿Hay decisiones que se contradicen entre sí o que fueron superadas?
6. ¿Qué decisión justifica la estructura BC-first del código?
7. ¿Qué riesgos quedaron pendientes en las decisiones tomadas?

## ADRs por área de impacto

| Área | ADRs |
|------|------|
| Persistencia | [[ADR-007-sqlite]], [[ADR-008-event-store]], [[ADR-009-migraciones]] |
| Arquitectura interna | [[ADR-005-bounded-contexts]], [[ADR-006-estructura-bc-first]] |
| Frontend / offline | [[ADR-003-offline-first-pwa]] |
| Backend / framework | [[ADR-002-fastapi-backend]] |
| Dominio / reglas | [[ADR-001-event-sourcing]], [[ADR-004-reglas-como-datos]] |
| API / errores | [[ADR-012-rfc7807]], [[ADR-013-exception-management]] |
| Despliegue | [[ADR-010-docker-produccion]] |
| Observabilidad | [[ADR-011-structlog-logging]] |

## Recorridos sugeridos

**Para entender la arquitectura de persistencia:**
`[[ADR-007-sqlite]]` → `[[ADR-008-event-store]]` → `[[ADR-009-migraciones]]`
→ `[[competencia]]`

**Para entender la arquitectura interna:**
`[[ADR-005-bounded-contexts]]` → `[[ADR-006-estructura-bc-first]]`
→ `[[ADR-001-event-sourcing]]` → `[[competencia]]`

**Para una nueva decisión técnica:**
Buscar en esta vista qué ADRs cubren el área → leer las páginas de decisión
→ verificar si hay contradicciones detectadas en `[[lint-actual]]`

## Páginas hub de esta vista

- [[ADR-001-event-sourcing]] — decisión fundacional del core domain
- [[ADR-005-bounded-contexts]] — diseño estratégico DDD
- [[ADR-006-estructura-bc-first]] — materialización en código
- [[ADR-007-sqlite]] — decisión de persistencia con mayor impacto cruzado

---
*Vista pendiente de poblarse — requiere Fase 1 (ingest fundacional de ADRs)*
