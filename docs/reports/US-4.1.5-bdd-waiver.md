# Waiver BDD — US-4.1.5
## Descomponer aggregate `Performance`

**Fecha:** `2026-04-08`
**Decisión:** `BDD omitido`

## Justificación

`US-4.1.5` es un ajuste técnico de refactoring interno sobre el aggregate `Performance`.
No introduce comportamiento funcional nuevo para usuario final ni altera el contrato
observable del caso de uso. Por instrucción explícita del incremento `INC-4.1`, para
este grupo de ajustes técnicos no se requieren escenarios BDD ejecutables.

## Validación sustitutiva

- Cobertura unitaria del aggregate `Performance`
- Cobertura de integración de handlers/event store vinculados a tarjeta y corrección
- Quality gates con `designreviewer` y `codeguard`

## Alcance del waiver

- Se omite Fase 1 como generación de `.feature`
- Se omite Fase 6 como ejecución de validación BDD
- Se mantienen obligatorias Fases 4, 5, 7, 8 y 9
