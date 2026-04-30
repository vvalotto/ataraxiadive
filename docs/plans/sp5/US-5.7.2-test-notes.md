# Test Notes - US-5.7.2

## Tests Unitarios

No se agregan tests unitarios automatizados porque el frontend no tiene harness de
componentes React configurado para montar paginas con React Query y router.

La logica agregada queda validada por TypeScript y ESLint focalizado:

- identificacion de fila propia por `atleta_id`
- ordenamiento de grilla por `posicion`
- manejo de estado provisional por `grilla_confirmada`
- links con `competenciaId` y `disciplina`

## Tests de Integracion

No hay backend nuevo. La pagina consume contratos existentes:

- `GET /registro/atletas/me`
- `GET /competencia/{competencia_id}/grilla?disciplina=...`
- `GET /competencia/{competencia_id}/estado?disciplina=...`
- `GET /torneos/{torneo_id}`

## BDD / UI

Escenarios documentados en `tests/features/US-5.7.2-mi-grilla.feature`.
La validacion UI queda manual/smoke hasta incorporar harness browser.
