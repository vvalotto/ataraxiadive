# Validacion BDD - US-5.1.7

## Feature

`tests/features/US-5.1.7-politica-tabs.feature`

## Resultado

Waiver de ejecucion automatizada.

Los escenarios BDD fueron materializados desde la spec, pero el frontend no tiene
steps ejecutables para montar la UI React en navegador o DOM simulado. No se agregan
steps ad hoc para evitar introducir infraestructura de test fuera del alcance de
INC-5.1-ADJ.

## Criterios cubiertos por revision manual

- Tabs habilitadas por estado.
- Tabs deshabilitadas visibles y no clickeables.
- `activeTab` reseteado a `Detalle` cuando el estado invalida la tab activa.
- Estado `CANCELADO` sin paneles operativos ni acciones de fase.
