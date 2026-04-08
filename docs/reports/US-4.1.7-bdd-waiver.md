# Waiver BDD — US-4.1.7
## Simplificar `GrillaDeSalida` y `RankingCompetencia`

**Fecha:** `2026-04-08`
**Decisión:** `BDD omitido`

## Justificación

`US-4.1.7` es un refactoring técnico de métodos largos y colaboradores de dominio/
infraestructura. No agrega comportamiento funcional nuevo; solo reorganiza lógica ya
existente preservando resultados observables.

Por la regla acordada para los ajustes técnicos de `INC-4.1`, esta US no requiere
escenarios BDD ejecutables.

## Validación sustitutiva

- Tests unitarios de grilla y ranking
- Tests de integración de generación de grilla y cálculo de ranking
- Quality gates con `designreviewer` y `codeguard`

## Alcance del waiver

- Se omite Fase 1 como generación de `.feature`
- Se omite Fase 6 como validación BDD
- Se mantienen obligatorias Fases 4, 5, 7, 8 y 9
