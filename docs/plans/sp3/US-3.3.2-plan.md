# Plan de Implementación — US-3.3.2
## Flujo E2E — inscribir atleta → AP → grilla

**Branch:** `feature/US-3.3.2-flujo-e2e-torneo-competencia`
**Estimación total:** 45 min

---

## Análisis

US sin código de producción nuevo. Entregable único: test de integración E2E
que valida el contrato implícito `atleta_id = participante_id` entre los 3 BCs.

**BCs involucrados:**
- `torneo` → `SQLiteTorneoRepository` + `CrearTorneoHandler` + `AbrirInscripcionHandler`
- `registro` → `SQLiteAtletaRepository` + `SQLiteInscripcionRepository` + `SQLiteTorneoConsulta` (ACL)
- `competencia` → `SQLiteEventStore` + handlers existentes

**Punto de integración clave:** `SQLiteTorneoConsulta` lee la misma `torneo.db` que escribe
`SQLiteTorneoRepository`. Los `tmp_path` deben coordinarse en un fixture compartido.

---

## Tareas

### T1 — Fixture E2E compartido (15 min)
Fixture `pytest_asyncio` que inicializa los 3 BCs con paths SQLite temporales coordinados:
- `tmp_path / "torneo.db"` → compartido entre `SQLiteTorneoRepository` y `SQLiteTorneoConsulta`
- `tmp_path / "registro.db"` → para `SQLiteAtletaRepository` e `SQLiteInscripcionRepository`
- `tmp_path / "competencia.db"` → para `SQLiteEventStore`

### T2 — Test E2E flujo completo (15 min)
`test_flujo_completo_inscripcion_ap_grilla`: flujo de 5 pasos según spec US-3.3.2.
Verifica INV-E2E-01, INV-E2E-02, INV-E2E-03.

### T3 — Test E2E atleta sin AP (5 min)
`test_atleta_sin_ap_no_aparece_en_grilla`: 2 atletas inscriptos, solo 1 con AP.
Verifica RF-PR-04.

### T4 — Test E2E orden por AP (5 min)
`test_multiples_atletas_ordenados_por_ap`: 3 atletas con APs 360s/300s/240s.
Verifica RF-PR-05 (STA: mayor AP primero).

### T5 — Steps BDD (5 min)
Step definitions para el `.feature` de US-3.3.2 usando el fixture compartido.

---

## Archivos a crear

```
tests/integration/e2e/test_flujo_torneo_competencia.py  ← tests T1–T4
tests/features/steps/test_US_3_3_2_steps.py             ← steps BDD T5
```

## Notas

- El fixture usa handlers directamente (no HTTP) — test de integración puro
- `Categoria` importada de `registro.domain.value_objects.categoria`
- `Disciplina` importada de `shared.domain.value_objects.disciplina`
- `obtener_grilla` retorna entradas con `atleta_id` (verificar nombre exacto del campo)
