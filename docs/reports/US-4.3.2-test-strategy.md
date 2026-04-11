# Fases 4-6 — US-4.3.2
## Estrategia de tests y validacion para flujo juez + backend

`US-4.3.2` extiende un frontend React/Vite y expone endpoints nuevos en FastAPI.
El repositorio sigue sin harness automatizado de browser tests end-to-end, por lo
que la validacion queda repartida entre chequeos tecnicos y smoke test funcional.

- **Fase 4 (tests unitarios):** no se agregan suites nuevas; la cobertura tecnica
  del frontend queda en `tsc`, `vite build` y `eslint`.
- **Fase 5 (tests de integracion):** se ejecuta un smoke test con `TestClient`
  contra `src.app`, autenticando como juez y recorriendo:
  - `GET /competencia/{id}/grilla`
  - `POST /competencia/{id}/llamar`
  - `POST /competencia/{id}/registrar-resultado`
  - `POST /competencia/{id}/asignar-tarjeta`
- **Fase 6 (validacion BDD):** los escenarios del `.feature` se validan manualmente
  con backend corriendo y fixture local reseteable.

Cobertura aplicada:

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- `python -m compileall src`
- smoke test backend con `fastapi.testclient.TestClient`
- fixture local `scripts/setup_us_4_3_2_fixture.py` para resetear la competencia

Validacion manual confirmada:

- recorrido completo del wizard desde `/juez/grilla`;
- confirmacion de habilitado/deshabilitado en Paso 5;
- cierre correcto con `TARJETA BLANCA` y retorno a grilla.
