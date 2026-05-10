# Plan de Implementacion: US-6.6.1 - Endpoint publico GET /api/torneos

**Patron:** Hexagonal DDD BC-first  
**Producto / BC:** torneo  
**Incremento:** INC-6.6 - Portal Publico  
**Estimacion total:** 1h 20m  
**Estado:** Implementacion completada - pendiente reporte final  
**Fecha implementacion:** 2026-05-10

## Objetivo

Exponer la lista publica de torneos sin autenticacion, manteniendo el contrato actual y excluyendo torneos en estado `CANCELADO`.

## Componentes a Modificar

### 1. API Router Torneo

- [x] `src/torneo/api/router.py` (10 min)
  - Mantener `listar_torneos()` sin dependencias de autenticacion.
  - Filtrar `EstadoTorneo.CANCELADO` antes de serializar la respuesta.
  - Importar `EstadoTorneo` si hace falta para evitar comparar strings sueltos.

### 2. Tests de Integracion HTTP

- [x] `tests/integration/torneo/test_torneos_publicos_api.py` (25 min)
  - Verificar `GET /torneos` sin `Authorization` retorna 200.
  - Verificar que torneos `CANCELADO` no aparecen.
  - Verificar campos requeridos por portal publico.
  - Verificar que llamada con override de organizador mantiene mismo contrato.

### 3. BDD

- [x] `tests/features/steps/torneos_publicos_steps.py` (20 min)
  - Implementar steps para `US-6.6.1-endpoint-publico-torneos.feature`.
  - Usar `TestClient` con DB temporal.
  - Crear torneos mediante API y transiciones para llegar a estados requeridos.

### 4. Validacion

- [x] Ejecutar tests de integracion de torneo enfocados (5 min)
  - `pytest tests/integration/torneo/test_torneos_publicos_api.py`
- [x] Ejecutar BDD de la US (5 min)
  - `pytest tests/features/steps/torneos_publicos_steps.py`
- [x] Ejecutar regresion acotada de router torneo (5 min)
  - `pytest tests/integration/torneo/test_grupos_etarios_api.py tests/integration/torneo/test_disciplinas_torneo_api.py`
- [x] Ejecutar quality gate de BC (10 min)
  - `codeguard src/torneo --config pyproject.toml` o comando equivalente disponible.

## Invariantes

- No agregar auth al endpoint `GET /torneos`.
- No modificar contrato de `TorneoResponse`.
- No tocar dominio ni repositorio para este filtro.
- No afectar endpoints privados con `OrganizadorDep`.

## Riesgos y Mitigaciones

- **Riesgo:** El filtro de cancelados afecte el panel organizador si consume el mismo endpoint.
  - **Mitigacion:** La spec acepta el mismo endpoint filtrado; validar contrato estable y documentar alcance.
- **Riesgo:** Diferencia entre `/api/torneos` documentado y `/torneos` interno FastAPI.
  - **Mitigacion:** Tests internos usan `/torneos`; el proxy/frontend podra montarlo bajo `/api`.

## Artefactos Esperados

- `src/torneo/api/router.py`
- `tests/integration/torneo/test_torneos_publicos_api.py`
- `tests/features/steps/torneos_publicos_steps.py`
- `quality/reports/codeguard/US-6.6.1-quality.txt`
- `docs/reports/US-6.6.1-report.md` (pendiente Fase 9)

## Evidencia de Validacion

- `.venv/bin/python -m pytest tests/integration/torneo/test_torneos_publicos_api.py` -> 4 passed.
- `.venv/bin/python -m pytest tests/integration/torneo/test_torneos_publicos_api.py tests/integration/torneo/test_grupos_etarios_api.py tests/integration/torneo/test_disciplinas_torneo_api.py` -> 20 passed.
- `.venv/bin/python -m pytest tests/features/steps/torneos_publicos_steps.py` -> 4 passed.
- `.venv/bin/codeguard src/torneo --config pyproject.toml` -> 0 errores, 0 advertencias.

## Documentacion Arquitectonica

No requiere ADR ni actualizacion de arquitectura: no se agregaron componentes ni integraciones nuevas. El cambio mantiene el router existente y acota el contrato publico de listado para excluir `CANCELADO`.

## Lecciones Aprendidas

- El endpoint ya era publico por firma y ausencia de middleware global; la US se resolvio como hardening contractual.
- Los escenarios BDD necesitaron normalizacion de conectores en espanol (`y`/`e`) para listas de estados.
