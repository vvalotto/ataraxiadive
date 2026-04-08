# Waiver BDD — US-4.1.8
## Limpiar `Torneo`, `SQLiteTorneoRepository` y objetos de soporte

**Fecha:** `2026-04-08`
**Decisión:** `BDD omitido`

## Justificación

`US-4.1.8` es un refactoring técnico sobre aggregate, repositorio y value objects de soporte.
No agrega comportamiento funcional nuevo ni cambia contratos públicos esperados.

Por la regla acordada para los ajustes técnicos de `INC-4.1`, esta US no requiere
escenarios BDD ejecutables.

## Validación sustitutiva

- Tests unitarios de `torneo` y `disciplina_descriptor`
- Tests de integración de repositorio y API de `torneo`
- Quality gates con `designreviewer` y `codeguard`

## Alcance del waiver

- Se omite Fase 1 como generación de `.feature`
- Se omite Fase 6 como validación BDD
- Se mantienen obligatorias Fases 4, 5, 7, 8 y 9
