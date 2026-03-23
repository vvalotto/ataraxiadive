# Reporte de Implementación: US-1.3.1

**Historia de Usuario:** US-1.3.1 — Interfaz del Juez: Read Models y Endpoints
**Fecha:** 2026-03-23
**Branch:** feature/US-1.3.1-interfaz-juez
**BC:** competencia (Query-side)

---

## Resumen

| Métrica | Valor |
|---|---|
| Tests totales | 174 (+28 nuevos) |
| Coverage | 97.53% |
| Pylint BC competencia | 9.58/10 |
| DesignReviewer CRITICAL | 0 |
| BDD escenarios | 4 (nuevos) — ahora ejecutando |

---

## Artefactos creados

| Artefacto | Path |
|---|---|
| US-IEDD | `docs/specs/sp1/US-1.3.1.md` |
| Plan | `docs/plans/sp1/US-1.3.1-plan.md` |
| BDD feature | `tests/features/US-1.3.1-interfaz-juez.feature` |
| BDD steps | `tests/features/steps/interfaz_juez_steps.py` |
| Puerto actualizado | `src/competencia/domain/ports/event_store_port.py` |
| Infra actualizada | `src/competencia/infrastructure/event_store/sqlite_event_store.py` |
| Query 1 | `src/competencia/application/queries/obtener_performance_actual.py` |
| Query 2 | `src/competencia/application/queries/obtener_proximas_performances.py` |
| Query 3 | `src/competencia/application/queries/obtener_progreso.py` |
| API router | `src/competencia/api/router.py` |
| App ensamble | `src/app.py` |
| Tests unitarios (queries) | `tests/unit/competencia/application/queries/` (3 archivos, 10 tests) |
| Tests unitarios (infra) | `tests/unit/competencia/infrastructure/test_sqlite_event_store_prefix.py` (4 tests) |
| Tests integración | `tests/integration/competencia/test_api_interfaz_juez.py` (4 tests) |

---

## Decisiones de diseño

1. **`load_all_streams_with_prefix` en EventStorePort**: pragmático para SP1 — evita materializar un read model separado. En SP3 se evaluará migrar a proyección materializada cuando la escala lo justifique.

2. **`Performance.participante_id` property añadida**: necesaria para que los query handlers accedan al participante sin violar encapsulamiento (`_participante_id` privado).

3. **Nombre del atleta hardcodeado**: `f"Atleta-{participante_id[:8]}"` — placeholder hasta SP3 cuando BC Registro esté disponible.

4. **Orden "proximas" por `occurred_at`**: proxy de grilla para SP1. En SP2 será por `posicion_grilla` de la grilla oficial.

---

## Hallazgo inesperado: BDD nunca corría

Al habilitar `python_files = ["test_*.py", "*_steps.py"]` en pyproject.toml, se descubrió que los 26 escenarios BDD de US-1.2.x nunca habían sido ejecutados (los `*_steps.py` no coincidían con el patrón de colección de pytest).

**Impacto:** Se activaron todos los BDD tests. Se encontró y corrigió un bug en `registrar_resultado_steps.py` — el step `AnunciadaAP` hacía `pass` en lugar de resetear el event store, causando que el Background dejara la Performance en estado `Llamada`.

**Estado final:** 174 tests pasan, incluyendo los 26 escenarios BDD de US-1.2.x y los 4 nuevos de US-1.3.1.

---

## Endpoints disponibles

```
GET /competencia/{competencia_id}/performance/actual
  → PerformanceActualDTO | null

GET /competencia/{competencia_id}/performance/proximas
  → list[ProximoAtletaDTO]  (limit=3)

GET /competencia/{competencia_id}/progreso
  → ProgresoCompetenciaDTO {total, ejecutadas, dns_count, completadas}
```

---

*Generado: 2026-03-23 — /implement-us US-1.3.1*
