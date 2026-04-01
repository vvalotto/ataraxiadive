# Reporte de Implementación — US-3.3.2
## Flujo E2E — inscribir atleta → AP → grilla

**Fecha:** 2026-04-01
**Branch:** `feature/US-3.3.2-flujo-e2e-torneo-competencia`
**Sprint:** SP3 — El Torneo
**Incremento:** INC-3.3

---

## Resumen

US sin código de producción nuevo. Entregable: test de integración E2E
que valida el contrato implícito `atleta_id = participante_id` entre los 3 BCs
incorporados en INC-3.1, INC-3.2 e INC-3.3.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `tests/integration/e2e/test_flujo_torneo_competencia.py` | Test E2E async | 3 tests con handlers directos + SQLite real |
| `tests/features/US-3.3.2-flujo-e2e-torneo-competencia.feature` | BDD | 3 escenarios Gherkin |
| `tests/features/steps/test_US_3_3_2_steps.py` | Steps BDD | asyncio.run() en steps síncronos |
| `docs/plans/sp3/US-3.3.2-plan.md` | Plan | Plan de implementación |

---

## Tests

| Test | Tipo | Invariante | Resultado |
|------|------|------------|-----------|
| `test_flujo_completo_inscripcion_ap_grilla` | E2E | INV-E2E-01/02/03 | ✅ |
| `test_atleta_sin_ap_no_aparece_en_grilla` | E2E | RF-PR-04 | ✅ |
| `test_multiples_atletas_ordenados_por_ap_descendente` | E2E | RF-PR-05 | ✅ |
| `test_flujo_completo` (BDD) | BDD | INV-E2E-01/02/03 | ✅ |
| `test_atleta_sin_ap` (BDD) | BDD | RF-PR-04 | ✅ |
| `test_orden_ap` (BDD) | BDD | RF-PR-05 | ✅ |

**Total nuevos:** 6 tests | **Total suite:** 674 | **Regresiones:** 0

---

## Decisiones Técnicas

### Coordinación de DBs entre BCs
`SQLiteTorneoConsulta` (ACL de Registro) lee la misma `torneo.db` que escribe
`SQLiteTorneoRepository`. El fixture comparte el mismo path `tmp_path / "torneo.db"`.

### Patrón BDD: asyncio.run() en steps síncronos
pytest-bdd 8.x no soporta `async def` steps. Se usa `asyncio.run(coro)` dentro
de steps síncronos, consistente con el patrón establecido en `flujo_e2e_steps.py`.

### Contrato implícito documentado
`atleta_id` (Registro) == `participante_id` (Competencia) en SP3.
El ACL formal (`AtletaInscripto → ParticipanteHabilitado`) queda para SP4.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Black | ✅ |
| isort | ✅ |
| CodeGuard | ✅ 0 errores |
| Tests (674) | ✅ 0 fallos |

---

## Métricas de Tiempo (estimadas)

| Fase | Estimado | Real |
|------|----------|------|
| Fase 0 — Validación | 10 min | ~8 min |
| Fase 1 — BDD | 15 min | ~5 min |
| Fase 2 — Plan | 20 min | ~5 min |
| Fase 3 — Implementación | 45 min | ~30 min |
| Fase 7 — Quality Gates | 10 min | ~5 min |
| Fase 8 — Documentación | 10 min | ~5 min |
| **Total** | **110 min** | **~58 min** |
