# Fases 4-6 — US-4.3.3
## Estrategia de tests y validacion para casos alternativos del juez

`US-4.3.3` extiende el flujo full-stack del juez incorporando ramas alternativas
de negocio: DNS, BKO/tarjeta roja y blanca con penalizaciones.

El repositorio sigue sin harness automatizado de UI end-to-end, por lo que la
validacion se reparte entre chequeos tecnicos y smoke tests de backend.

- **Fase 4 (tests unitarios):** no se agregan suites nuevas de frontend; la
  validacion estatica queda en `tsc`, `vite build` y `eslint`.
- **Fase 5 (tests de integracion):** se ejecuta smoke test con `TestClient`
  cubriendo:
  - `POST /registrar-dns`
  - BKO (`registrar-resultado` + `asignar-tarjeta` roja con blackout)
  - `BlancaConPenalizaciones` en `DNF`
- **Fase 6 (validacion BDD):** los escenarios del `.feature` quedan como contrato
  de aceptacion para validacion manual posterior.

Cobertura aplicada:

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- `./.venv/bin/python -m compileall src scripts/setup_us_4_3_3_fixture.py`
- smoke test full-stack con `TestClient`
- fixture local `scripts/setup_us_4_3_3_fixture.py`

Pendiente para cierre funcional completo:

- validacion manual UI de DNS;
- validacion manual UI de BKO;
- validacion manual UI de blanca con penalizaciones en `DNF`;
- confirmacion de selector deshabilitado para penalizaciones en `STA`.
