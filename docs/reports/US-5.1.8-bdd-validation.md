# Validacion BDD - US-5.1.8

## Feature

`tests/features/US-5.1.8-componer-competencias.feature`

## Resultado

Waiver de ejecucion automatizada.

Los escenarios BDD fueron materializados desde la spec, pero el frontend no tiene
steps ejecutables para montar la UI React con DOM/browser y mocks HTTP.

## Criterios cubiertos por revision manual

- Se renderiza una card por disciplina configurada.
- La competencia materializada enriquece la card correspondiente.
- `Ver auditoria` queda habilitado solo con `competencia_id`.
- El estado pendiente reemplaza el falso vacio cuando aun no hay competencias.
