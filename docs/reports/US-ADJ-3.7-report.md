# Reporte de Implementacion — US-ADJ-3.7
## Proyeccion `competencias_por_torneo`

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se materializo la proyeccion `competencias_por_torneo` dentro del BC
`competencia` para que la consulta `ObtenerCompetenciasPorTorneoHandler` deje
de escanear todos los streams historicos del event store.

La proyeccion se actualiza de forma sincronica al configurar
`IntervaloOTConfigurado` cuando la competencia pertenece a un torneo.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/competencia/domain/ports/competencias_por_torneo_port.py` | Dominio | Puerto de la proyeccion y record tipado |
| `src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py` | Infraestructura | Implementacion SQLite de la proyeccion |
| `src/competencia/application/commands/configurar_intervalo_ot.py` | Application | Actualiza la proyeccion al persistir el intervalo |
| `src/competencia/application/queries/obtener_competencias_por_torneo.py` | Application | Query handler refactorizado para leer la proyeccion |
| `src/competencia/api/router.py` | API | Wiring actualizado para inyectar la proyeccion |
| `docs/plans/sp-adj-03/US-ADJ-3.7-plan.md` | Plan | Plan tecnico de la US |
| `docs/reports/US-ADJ-3.7-report.md` | Reporte | Cierre documental de la US |
| `quality/reports/codeguard/US-ADJ-3.7-quality.txt` | Quality gate | Evidencia de CodeGuard de la US |

---

## Decisiones Tecnicas

### Puerto sin dependencia circular

Se evito importar `CompetenciaSummaryDTO` desde la capa de application al
puerto de dominio para no introducir una dependencia circular. En su lugar, el
puerto expone `CompetenciaPorTorneoRecord` y el query handler mapea ese record
al DTO publico.

### Proyeccion en la misma DB de Competencia

La tabla `competencias_por_torneo` se materializa en la misma
`COMPETENCIA_DB_PATH`. Esto evita sumar una configuracion adicional y mantiene
el patron actual del BC, donde SQLite aloja tanto el event store como los
read-models livianos.

### Actualizacion sincronica

`ConfigurarIntervaloOTHandler` persiste la proyeccion inmediatamente despues de
guardar el evento, solo cuando `torneo_id` no es `None`. Las competencias
standalone no se registran en la tabla.

---

## Invariantes Verificadas

| ID | Descripcion | Estado |
|----|-------------|--------|
| `INV-ADJ-3.7-1` | `ObtenerCompetenciasPorTorneoHandler` ya no usa `load_all_streams_with_prefix` | ✅ |
| `INV-ADJ-3.7-2` | la consulta por torneo mantiene el mismo resultado observable | ✅ |
| `INV-ADJ-3.7-3` | el wiring de API inyecta la proyeccion materializada | ✅ |
| `INV-ADJ-3.7-4` | los tests existentes del flujo torneo -> competencia pasan sin cambios funcionales | ✅ |

---

## Validacion Ejecutada

| Suite / Gate | Resultado |
|-------------|-----------|
| `tests/unit/competencia/application/test_configurar_intervalo_ot_handler.py` | ✅ |
| `tests/unit/competencia/application/test_obtener_competencias_por_torneo.py` | ✅ |
| `tests/integration/competencia/test_torneo_id_integration.py` | ✅ |
| `grep "load_all_streams_with_prefix"` sobre el query handler | ✅ 0 matches |
| `py_compile` de archivos impactados | ✅ |
| `git diff --check` | ✅ |
| `CodeGuard` sobre `ports`, `repositories`, `application` y `api` | ✅ 0 errores, 0 warnings |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/competencia/application/test_configurar_intervalo_ot_handler.py tests/unit/competencia/application/test_obtener_competencias_por_torneo.py tests/integration/competencia/test_torneo_id_integration.py -q
grep -n "load_all_streams_with_prefix" src/competencia/application/queries/obtener_competencias_por_torneo.py
./.venv/bin/python -m py_compile src/competencia/domain/ports/competencias_por_torneo_port.py src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py src/competencia/application/commands/configurar_intervalo_ot.py src/competencia/application/queries/obtener_competencias_por_torneo.py src/competencia/api/router.py
git diff --check
./.venv/bin/codeguard src/competencia/domain/ports/competencias_por_torneo_port.py src/competencia/infrastructure/repositories/sqlite_competencias_por_torneo.py src/competencia/application/commands/configurar_intervalo_ot.py src/competencia/application/queries/obtener_competencias_por_torneo.py src/competencia/api/router.py
```

Resultado consolidado:

- `25 passed` en validacion focalizada
- `CodeGuard` sin errores ni advertencias
- sin activos BDD nuevos generados para esta US

---

## Resultado

`US-ADJ-3.7` queda cerrada funcionalmente: la consulta de competencias por
torneo ya usa una proyeccion materializada, se elimina el scan O(n) sobre todos
los streams historicos y el flujo torneo -> competencia mantiene el mismo
comportamiento observable.
