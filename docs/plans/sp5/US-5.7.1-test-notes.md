# Test Notes - US-5.7.1

## Tests Unitarios

No se agregan tests unitarios automatizados porque la US modifica una pagina React existente
y el repo no tiene harness de componentes para montar `AtletaTorneosPage` con mocks de
React Query/API.

La logica agregada queda cubierta por validacion de tipos en `npm run build`:

- derivacion de `misTorneos` desde `listarInscripcionesDeAtleta`
- exclusion de torneos inscriptos en `abiertos`
- render de disciplinas desde `InscriptoDto.disciplinas`

## Tests de Integracion

No aplica backend ni contrato HTTP nuevo. La integracion esperada usa endpoints existentes:

- `GET /registro/atletas/me`
- `GET /registro/atletas/{atleta_id}/inscripciones`
- `GET /torneos`
- `GET /torneos/{torneo_id}/disciplinas`

## BDD / UI

Escenarios documentados en `tests/features/US-5.7.1-mis-torneos.feature`.
La validacion UI es manual hasta que exista harness browser para el portal atleta.
