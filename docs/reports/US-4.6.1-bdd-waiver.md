# Waiver BDD — US-4.6.1
## API de audit log de performance

**Fecha:** `2026-04-16`
**Decisión:** `BDD no automatizado`

## Justificación

`US-4.6.1` sí introduce comportamiento observable y por eso se generó el feature
`tests/features/US-4.6.1-audit-log-performance.feature`, pero el repositorio no
cuenta hoy con step definitions reutilizables para autenticación por rol más
consulta HTTP de auditoría en `competencia`.

Implementar ese harness en esta US hubiera desviado el alcance hacia infraestructura
de testing transversal en lugar de la funcionalidad del incremento.

## Validación sustitutiva

- Tests unitarios de `ObtenerAuditLogHandler`
- Tests de integración HTTP del endpoint protegido
- Quality gate focalizado con `codeguard`

## Alcance del waiver

- Se mantiene Fase 1 con generación del `.feature`
- Se reemplaza la automatización de Fase 6 por validación unitaria + integración
- No exime Fases 7, 8 y 9
