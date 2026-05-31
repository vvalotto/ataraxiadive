---
title: "Competencia — Query Handlers"
type: arquitectura-componente
bc: competencia
capa: application
tipo_componente: handler
responsabilidad: "9 handlers de consulta: read models sobre el Event Store para grilla, estado, progreso y audit log"
interfaces_out:
  - EventStorePort
  - AtletaNombrePort
  - PerformancesEstadoPort
  - CompetenciaEstadoPort
adr_refs: [ADR-001]
last_updated: "2026-05-23"
sources:
  - src/competencia/application/queries/
us_origen:
  - US-1.3.1-read-models-performance-actual-proximos-atletas
  - US-4.6.1-obtener-audit-log-por-performance
  - US-5.1.6-ejecucion-panel-monitor-de-competencias-activas
  - US-5.2.1-torneo-competencias-page-maestro-detalle-por-disciplina
  - US-5.7.2-mi-grilla-posicion-del-atleta-por-disciplina
tests:
  - tests/features/US-1.3.1-interfaz-juez.feature
  - tests/integration/competencia/test_api_interfaz_juez.py
  - tests/features/US-4.6.1-audit-log-performance.feature
  - tests/integration/competencia/test_audit_log_api.py
  - tests/features/US-5.7.2-mi-grilla.feature
---

# Query Handlers

## Responsabilidad

9 handlers de consulta que construyen **read models** a partir de eventos del Event Store. No modifican estado — solo leen y proyectan.

## Handlers

| Handler | Propósito |
|---------|----------|
| `ObtenerGrillaHandler` | Read model de la grilla: entradas con nombre de atleta (requiere [[atleta-nombre-port]]), OT, andarivel, juez |
| `ObtenerEstadoCompetenciaHandler` | Estado actual de la competencia (`Preparacion`, `Confirmada`, etc.) y metadata |
| `ObtenerProgresoHandler` | Conteo de performances por estado: ejecutadas / DNS / pendientes |
| `ObtenerPerformanceActualHandler` | Performance en estado `Llamada` (atleta en pista) |
| `ObtenerProximasPerformancesHandler` | Próximas N performances según OT programado |
| `ObtenerAndarivelActivos Handler` | Andariveles actualmente ocupados (INV-C-05: sin conflicto de andarivel) |
| `ObtenerCompetenciasPorTorneoHandler` | Lista de competencias asociadas a un torneo |
| `ObtenerEventosHandler` | Stream completo de eventos de una competencia (para audit/debug) |
| `ObtenerAuditLogHandler` | Log de auditoría filtrado por competencia — usa el Event Store directamente |

## Patrón de implementación

Las queries leen streams del Event Store y reconstituyen aggregates, o bien proyectan directamente los eventos sin reconstituir cuando solo necesitan datos de superficie (e.g., `ObtenerEventosHandler`).

`ObtenerGrillaHandler` es el más costoso: reconstituye `Competencia`, resuelve nombres de atletas via [[atleta-nombre-port]] (una llamada async por atleta).

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

- Todos consumen [[event-store-port]]
- `ObtenerGrillaHandler` usa [[atleta-nombre-port]]
- Son invocados desde [[router-competencia]]
- El read model de grilla es el principal insumo del panel del juez (Frontend)

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/application/queries/` |  |
