# Test Notes - US-5.7.3

## Tests Unitarios

No se agregan tests unitarios automatizados porque el frontend no tiene harness de
componentes React configurado para montar paginas con React Query y mocks de API.

La logica agregada queda validada por TypeScript y ESLint focalizado:

- busqueda de resultado propio por `atleta_id`
- tratamiento de ranking no calculado como pendiente
- mapeo de tarjeta/DNS a estado visual
- calculo de diferencia AP-RP con signo

## Tests de Integracion

No hay backend nuevo. La pagina consume contratos existentes:

- `loadAtletaPortalSnapshot()`
- `GET /resultados/{competencia_id}/ranking?disciplina=...`

## BDD / UI

Escenarios documentados en `tests/features/US-5.7.3-mis-resultados.feature`.
La validacion UI queda manual/smoke hasta incorporar harness browser.
