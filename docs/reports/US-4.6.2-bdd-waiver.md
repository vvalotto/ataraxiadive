# Waiver BDD — US-4.6.2
## Hash SHA-256 al cierre de disciplina

**Fecha:** `2026-04-16`
**Decisión:** `BDD no automatizado`

## Justificación

`US-4.6.2` sí agrega comportamiento observable y por eso se generó el feature
`tests/features/US-4.6.2-hash-cierre-disciplina.feature`, pero el escenario
relevante ocurre dentro de la política automática `P-08` y depende de la
finalización encadenada desde handlers existentes.

Automatizar ese flujo en BDD para esta US hubiera requerido construir un harness
transversal adicional para sembrar event store, disparar cierre automático y
validar el payload persistido de `CompetenciaFinalizada`.

## Validación sustitutiva

- Tests unitarios del servicio `CalculadorHashCompetencia`
- Tests unitarios del aggregate `Competencia` y de la política `P-08`
- Tests de integración del cierre real y del callback `P-09`
- Quality gate focalizado con `codeguard`

## Alcance del waiver

- Se mantiene Fase 1 con generación del `.feature`
- Se reemplaza la automatización de Fase 6 por validación unitaria + integración
- No exime Fases 7, 8 y 9
