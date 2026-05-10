# Reporte de Implementacion: US-6.6.1

## Resumen Ejecutivo

- **Historia de Usuario:** US-6.6.1 - Endpoint publico `GET /api/torneos`
- **Incremento:** INC-6.6 - Portal Publico
- **Producto / BC:** torneo
- **Puntos estimados:** 2
- **Estado:** COMPLETADO
- **Fecha completado:** 2026-05-10

## Componentes Implementados

- `src/torneo/api/router.py`
  - `GET /torneos` se mantiene sin dependencia de autenticacion.
  - La respuesta excluye torneos con `EstadoTorneo.CANCELADO`.
  - `TorneoResponse` mantiene el contrato existente.

## Tests Implementados

- `tests/integration/torneo/test_torneos_publicos_api.py`
  - 4 tests HTTP para acceso publico, exclusion de cancelados, contrato del portal y compatibilidad con llamada autenticada.
- `tests/features/US-6.6.1-endpoint-publico-torneos.feature`
  - 4 escenarios BDD aprobados.
- `tests/features/steps/torneos_publicos_steps.py`
  - Steps ejecutables con `TestClient` y base SQLite temporal.

## Validacion Ejecutada

| Comando | Resultado |
|---|---|
| `.venv/bin/python -m pytest tests/integration/torneo/test_torneos_publicos_api.py` | 4 passed |
| `.venv/bin/python -m pytest tests/integration/torneo/test_torneos_publicos_api.py tests/integration/torneo/test_grupos_etarios_api.py tests/integration/torneo/test_disciplinas_torneo_api.py` | 20 passed |
| `.venv/bin/python -m pytest tests/features/steps/torneos_publicos_steps.py` | 4 passed |
| `.venv/bin/codeguard src/torneo --config pyproject.toml` | 0 errores, 0 advertencias |

## Criterios de Aceptacion

- [x] Visitante puede listar torneos sin `Authorization`.
- [x] Torneos `CANCELADO` no aparecen en la lista publica.
- [x] Cada torneo expone `torneo_id`, `nombre`, `fecha_inicio`, `fecha_fin`, `sede`, `estado` y `descripcion`.
- [x] La llamada con auth mantiene el mismo contrato que la llamada publica.

## Archivos Creados o Modificados

- `src/torneo/api/router.py`
- `tests/integration/torneo/test_torneos_publicos_api.py`
- `tests/features/US-6.6.1-endpoint-publico-torneos.feature`
- `tests/features/steps/torneos_publicos_steps.py`
- `docs/plans/sp6/US-6.6.1-fase0.md`
- `docs/plans/sp6/US-6.6.1-plan.md`
- `quality/reports/codeguard/US-6.6.1-quality.txt`
- `docs/reports/US-6.6.1-report.md`

## Notas

- No se agrego middleware ni excepcion de auth porque `src/app.py` no tiene autenticacion global y el endpoint ya era publico por firma.
- No se actualizo arquitectura ni ADR: el cambio es un ajuste contractual menor en un endpoint existente.
- El prefijo `/api` queda como responsabilidad del despliegue/proxy/frontend; en FastAPI el router se prueba como `/torneos`.
