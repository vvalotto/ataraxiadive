---
title: "Vista de Trazabilidad"
type: vista
last_updated: "2026-05-20"
sources:
  - docs/traceability/matrix.md
  - docs/plans/
  - docs/reports/
---

# Vista de Trazabilidad

> El sistema visto desde los requerimientos hacia la implementación.

## Propósito

Responder preguntas sobre qué implementa cada requerimiento, qué tests lo
verifican y qué evidencia existe de su cierre. Navegar la cadena completa
RF → US → código → tests → reporte. Es la vista para análisis de cobertura,
auditorías y comprensión de qué está implementado y con qué calidad.

## Stakeholder principal

QA, auditor, desarrollador implementando un cambio, responsable de calidad.

## Preguntas características

1. ¿Qué US implementa el requerimiento RF-CO-03?
2. ¿Qué tests cubren la historia US-3.3.1?
3. ¿Hay requerimientos funcionales sin tests asociados?
4. ¿Qué archivos de código implementan el registro de performance?
5. ¿Está cerrada y verificada la US-3.5.1?
6. ¿Qué US del BC Competencia están pendientes de implementación?
7. ¿Qué cobertura de tests tiene el SP3 completo?

## Mapa de subproyectos

| SP | Nombre | BCs involucrados | Estado estimado |
|----|--------|-----------------|-----------------|
| SP1 | La Performance | Competencia (core) | ✅ Cerrado |
| SP2 | La Competencia | Competencia (ampliado) | ✅ Cerrado |
| SP3 | El Torneo | Torneo + Registro | ✅ Cerrado |
| SP4 | La Plataforma | Identidad + Notificaciones | ✅ Cerrado |
| SP5 | La Puesta en Marcha | Todos + Resultados | En progreso |
| SP6+ | Incrementos adicionales | Varios | En progreso |

## Recorridos sugeridos

**Para verificar cobertura de un requerimiento:**
`[[estado/proyecto]]` → buscar RF en index → `[[trazabilidad/US-X.X.X]]`
→ tests asociados → `[[trazabilidad/US-X.X.X-report]]`

**Para entender qué cubre un BC:**
`[[competencia]]` → lista de US implementadas → páginas de trazabilidad
por US → reportes de cierre

**Para auditoría de cobertura total:**
`[[salud/lint-actual]]` → sección "requerimientos sin tests" → gaps identificados

## Páginas hub de esta vista

- [[estado/proyecto]] — punto de entrada al estado de implementación
- `wiki/trazabilidad/` — todas las US con su ciclo completo
- [[salud/lint-actual]] — gaps de trazabilidad detectados

---
*Vista pendiente de poblarse — requiere Fase 3 (ingest de estado)*
