# Revisión de Calidad — Cierre SP3
## DesignReviewer — Hallazgos y Análisis

**Fecha:** 2026-04-02
**Comando:** `designreviewer src/ --config pyproject.toml`
**Resultado:** 0 CRITICAL · 111 WARNING · 0 INFO

---

## Resultado global

**0 CRITICAL** — no hay bloqueantes. El cierre formal no está impedido por quality gates de DesignReviewer.

Thresholds vigentes en `pyproject.toml` (calibrados en SP2/INC-3.3):
| Parámetro | Valor | Justificación registrada |
|-----------|-------|--------------------------|
| `max_cbo` | 25 | Performance/Competencia crecen legítimamente con cada US |
| `max_wmc` | 65 | Competencia WMC=64 al cerrar INC-3.3 |
| `max_god_object_lines` | 540 | Competencia.py ~535 líneas al cierre SP2 |
| `max_god_object_methods` | 28 | Performance 22 métodos al cierre INC-2.1 |

---

## WARNING por paquete

### aggregates (24 warnings)

| Clase | Analyzer | Val/Umbral | Observación |
|-------|----------|------------|-------------|
| Torneo | LCOM | 3/1 | Nuevo en SP3 — aggregate CRUD con disciplinas y jueces como subconjuntos independientes |
| Competencia | LongMethod ×7 | 30–127/20 | Pre-existente SP2. El peor: `ajustar_grilla` 127 líneas — candidato SP-ADJ-03 |
| Performance | LongMethod ×8 | 28–54/20 | Pre-existente SP2 — métodos `_apply_*` son verbosos por diseño ES |
| RankingOverall | LongMethod ×2 | 27–32/20 | Nuevo SP3 — `calcular` y módulo |
| RankingCompetencia | LCOM + LongMethod | 2/1, 39–57/20 | Pre-existente SP2 |

**Nuevo en SP3:** LCOM de `Torneo` (3/1) y LongMethod de `RankingOverall`. El resto son pre-existentes.

### commands (36 warnings)

Patrón uniforme: **FeatureEnvy + LongMethod** en todos los handlers.

- FeatureEnvy es **esperado** en la capa application: los handlers coordinan entre aggregate, ports y eventos. El analyzer no tiene contexto de que esto es el patrón Command Handler de DDD.
- LongMethod refleja la verbosidad de los handlers que hacen load/execute/save explícitamente.
- No requieren acción — son falsos positivos del patrón arquitectural.

Excepción: `RegistrarAPHandler` (LongMethod 71/20) y `AsignarTarjetaHandler` (46/20) son genuinamente largos y candidatos a refactor futuro.

### api (19 warnings)

- DataClumps en router.py (varios BCs): parámetros repetidos en endpoints — patrón FastAPI.
- FanOut en router.py: routers importan varios handlers y ports — esperado.
- LongMethod en endpoints: endpoints con lógica de orquestación — candidatos a refactor futuro.
- `FeatureEnvyAnalyzer` en `TorneoResponse`: response DTO que accede a campos del aggregate — falso positivo.

### application (1 warning)

- `_p08_finalizacion.py`: LongMethod 53/20 — contiene la política P-08 completa (callback de finalización). Lógicamente cohesivo aunque largo.

### event_store (5 warnings)

- `SQLiteEventStore`: 5 LongMethod — métodos SQL verbosos. Pre-existente, aceptado.

### queries (10 warnings)

- FeatureEnvy generalizado en handlers de query — mismo análisis que commands: falso positivo de patrón.
- LongMethod en `ObtenerRankingHandler` (31/20) y `ObtenerProximasPerformancesHandler` (29/20).

### repositories (13 warnings)

- FeatureEnvy en SQLite repos (Torneo, Usuario, Inscripción, Atleta) — patrón Repository es por definición FeatureEnvy del aggregate.
- LongMethod en adapters: `AndarivelesActivosAdapter` (52/20), `ResultadosCompetenciaAdapter` (46/20) — candidatos a refactor.

### src (3 warnings)

- `app.py` FanOut 10/7 — composition root importa todos los BCs. Esperado y correcto.
- `app.py` LongMethod `build_app` (51/20) y `_on_finalizacion` (34/20) — candidatos SP-ADJ-03.

---

## Observación sobre thresholds

Los umbrales de `pyproject.toml` no se actualizaron para SP3. Con 756 tests y 6 nuevos BCs CRUD, Competencia no creció significativamente (WMC estable). Sin embargo, **debería documentarse el estado actual** en los comentarios de pyproject.toml para SP4.
