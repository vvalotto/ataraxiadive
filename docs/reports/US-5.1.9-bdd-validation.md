# Validacion BDD - US-5.1.9

## Feature

`tests/features/US-5.1.9-bloquear-jueces-sin-grilla.feature`

## Resultado

Waiver de ejecucion automatizada.

Los escenarios BDD fueron materializados desde la spec, pero el frontend no tiene
steps ejecutables para montar la UI React con DOM/browser y mocks HTTP.

## Criterios cubiertos por revision manual

- Selector habilitado solo con competencia en estado de grilla generada.
- Selector bloqueado para disciplina sin competencia.
- Asignacion existente visible aunque la fila este bloqueada.
- Mensaje `Generar grilla antes de asignar juez` visible en filas bloqueadas.
