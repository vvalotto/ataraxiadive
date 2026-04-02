# Reporte de Implementación — US-3.5.3
## API GET /resultados/{torneo_id}/overall

**Fecha:** 2026-04-02
**Branch:** `feature/US-3.5.3-api-overall`
**Sprint:** SP3 — El Torneo
**Incremento:** INC-3.5

---

## Resumen

Implementación de la consulta pública del ranking overall de un torneo en el
BC `resultados`.

La US expone `GET /resultados/{torneo_id}/overall`, leyendo el último
`RankingOverallCalculado` del stream `ranking-overall-{torneo_id}` y
respondiendo siempre `200`:

- `calculado=true` si el overall ya existe
- `calculado=false` y `ranking=[]` si aún no fue calculado

---

## Artefactos Producidos

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `src/resultados/application/queries/obtener_overall.py` | Aplicación | Query + handler para leer el overall persistido |
| `src/resultados/api/router.py` | API | Endpoint `GET /resultados/{torneo_id}/overall` |
| `tests/unit/resultados/application/test_obtener_overall_handler.py` | Unit | Casos stream vacío, reconstitución y stream correcto |
| `tests/unit/resultados/api/test_router_overall.py` | Unit HTTP | Contrato JSON de overall calculado y no calculado |
| `tests/integration/resultados/test_obtener_overall_integration.py` | Integración | Reconstitución del overall desde SQLiteEventStore |
| `tests/features/US-3.5.3-api-overall.feature` | BDD | Escenarios observables del endpoint overall |
| `tests/features/steps/api_overall_steps.py` | Steps BDD | Ejecución observable del endpoint sobre SQLite temporal |
| `quality/reports/codeguard/US-3.5.3-quality.txt` | Quality gate | Evidencia de CodeGuard sobre componentes impactados |
| `docs/plans/sp3/US-3.5.3-plan.md` | Plan | Plan técnico aprobado para la US |

---

## Decisiones Técnicas

### Patrón de consulta

`ObtenerOverallHandler` sigue el mismo patrón de `ObtenerRankingHandler`:
lee desde Event Store, reconstituye el aggregate y proyecta DTOs para la capa
HTTP.

### Contrato HTTP

El endpoint responde siempre `200`, evitando distinguir por status code entre
"torneo inexistente" y "overall pendiente". El estado observable se comunica
mediante `calculado`.

### Shape de respuesta

Cada entrada del overall expone:

- `posicion`
- `atleta_id`
- `puntaje`
- `detalle`
- `en_podio`

El campo `detalle` preserva el mapa disciplina -> posición persistido por
`RankingOverallCalculado`.

---

## Tests

| Suite | Tests | Resultado |
|-------|-------|-----------|
| Unitarios focalizados | 5 | ✅ 5/5 |
| Integración focalizada | 1 | ✅ 1/1 |
| BDD focalizado | 4 | ✅ 4/4 |
| Regresión router + BDD | 6 | ✅ 6/6 |
| **Total ejecutado** | **16** | ✅ **16/16** |

Comandos validados:

```bash
./.venv/bin/pytest tests/unit/resultados/application/test_obtener_overall_handler.py tests/unit/resultados/api/test_router_overall.py -q
./.venv/bin/pytest tests/integration/resultados/test_obtener_overall_integration.py -q
./.venv/bin/pytest tests/features/steps/api_overall_steps.py -q
```

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| `py_compile` sobre código y tests nuevos | ✅ |
| `git diff --check` | ✅ |
| Pytest focalizado | ✅ 10/10 |
| CodeGuard sobre componentes impactados | ✅ 0 errores, 0 warnings |

**Artefacto:** `quality/reports/codeguard/US-3.5.3-quality.txt`

---

## Invariantes Cubiertos

| ID | Descripción | Estado |
|----|-------------|--------|
| `INV-OV-API-01` | Si el overall no fue calculado aún, responde `calculado=false` y `ranking=[]` | ✅ |
| `INV-OV-API-02` | El endpoint es público para SP3 | ✅ |
| `INV-OV-API-03` | Cada entrada expone `detalle` por disciplina | ✅ |

---

## Pendiente para la siguiente US

- Sin pendiente funcional inmediato dentro de `INC-3.5` desde esta API
