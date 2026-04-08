# Waiver BDD — US-4.1.6
## Aliviar handlers de `competencia`

**Fecha:** `2026-04-08`
**Decisión:** `BDD omitido`

## Justificación

`US-4.1.6` es un refactoring técnico sobre handlers de aplicación del BC `competencia`.
No agrega comportamiento funcional nuevo ni cambia contratos externos de la API o del dominio.
Por la regla acordada para los ajustes técnicos de `INC-4.1`, esta US no requiere escenarios
BDD ejecutables.

## Validación sustitutiva

- Tests unitarios de handlers
- Tests de integración de comandos afectados
- Quality gates con `designreviewer` y `codeguard`

## Alcance del waiver

- Se omite Fase 1 como generación de `.feature`
- Se omite Fase 6 como validación BDD
- Se mantienen obligatorias Fases 4, 5, 7, 8 y 9
