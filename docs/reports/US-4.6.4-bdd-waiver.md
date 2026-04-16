# Waiver BDD — US-4.6.4
## Exportación de resultados CSV y JSON

**Fecha:** `2026-04-16`
**Decisión:** `BDD no automatizado`

## Justificación

`US-4.6.4` agrega comportamiento observable en HTTP y por eso se generó el
feature `tests/features/US-4.6.4-exportacion-resultados.feature`, pero el
repositorio no cuenta hoy con step definitions reutilizables para exportación
de archivos con `Content-Disposition`, ACLs cross-BC y control de autenticación
por rol dentro del router de `resultados`.

Implementar ese harness BDD para esta US hubiera desviado el alcance hacia
infraestructura de testing transversal en lugar de cerrar la exportación del
incremento.

## Validación sustitutiva

- Tests unitarios del handler `ExportarResultadosHandler`
- Tests HTTP del router de `resultados` para `json`, `csv`, `400`, `403` y `404`
- Quality gate focalizado con `codeguard`

## Alcance del waiver

- Se mantiene Fase 1 con generación del `.feature`
- Se reemplaza la automatización de Fase 6 por validación unitaria + HTTP
- No exime Fases 7, 8 y 9
