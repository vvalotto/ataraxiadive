---
title: "US-4.5.4 — Política P-11: email a atletas al publicar resultados"
type: trazabilidad-us
sp: SP4
inc: INC-4.5
bc: notificaciones, resultados
estado: completado
fecha_cierre: "2026-04-18"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §16
---

# US-4.5.4 — Política P-11: email a atletas al publicar resultados

## Descripción

Implementa la política P-11: cuando se publican los resultados de una disciplina, el sistema notifica por email a todos los atletas que participaron en ella.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-NT-04 | Notificar a atletas cuando se publican resultados finales |

## Contenido implementado

- Política P-11 — listener de `ResultadosPublicados` → email a cada atleta de la disciplina
- Template `resultados_publicados` — email con link a resultados
- Idempotencia compuesta: `evento_fuente_id = "{evento.id}:{atleta_id}"` — una notificación por atleta por evento

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/notificaciones/application (P-11) | ✅ |

## Estado

✅ Completado — 2026-04-18 (PR #82)
