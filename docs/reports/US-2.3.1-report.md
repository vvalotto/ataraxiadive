# Reporte de Implementación: US-2.3.1 — Ejecución Multi-Andarivel

| Campo | Valor |
|-------|-------|
| **US** | US-2.3.1 |
| **Incremento** | Inc 2.3 |
| **Branch** | `feature/US-2.3.1-ejecucion-multi-andarivel` |
| **Fecha** | 2026-03-27 |
| **Tiempo real** | ~22 min |
| **Tests** | 424 passed (+15 nuevos) |
| **Cobertura** | 97% |
| **CodeGuard** | 0 errores, 0 advertencias |

---

## Resumen

Implementación del invariante **INV-C-05** (no hay dos performances en estado Llamada en el mismo andarivel) y del Read Model `AndarivelesActivos` (`GET /competencia/{id}/andariveles`).

---

## Componentes creados

| Archivo | Descripción |
|---------|-------------|
| `domain/ports/andariveles_activos_port.py` | Port + DTO `AndarivelesActivosData` |
| `application/commands/llamar_atleta.py` | `AndarivelesConflicto` + verificación INV-C-05 |
| `application/queries/obtener_andariveles_activos.py` | Query handler |
| `infrastructure/repositories/andariveles_activos_adapter.py` | Adapter sobre Event Store |
| `api/router.py` | `GET /competencia/{id}/andariveles` |

## Componentes modificados

| Archivo | Cambio |
|---------|--------|
| `domain/events/atleta_llamado.py` | Campo `andarivel: int = 1` (backward compat) |
| `domain/aggregates/performance.py` | Propiedad `andarivel`, `llamar(andarivel=1)` |

## Tests nuevos

| Archivo | Tests |
|---------|-------|
| `tests/unit/competencia/application/test_llamar_atleta_andariveles.py` | 5 unit tests INV-C-05 |
| `tests/unit/competencia/application/queries/test_obtener_andariveles_activos.py` | 2 unit tests handler |
| `tests/integration/competencia/test_andariveles_activos_integration.py` | 3 integration tests con SQLiteEventStore real |
| `tests/features/steps/ejecucion_multi_andarivel_steps.py` | 5 BDD scenarios |

---

## Decisiones de diseño

1. **`andariveles_activos: AndarivelesActivosPort | None = None`** en `LlamarAtletaHandler` — backward compat con ~15 archivos de tests existentes sin necesidad de modificarlos. El router siempre inyecta el adapter real.
2. **`andarivel: int = 1`** en `AtletaLlamado`, `Performance.llamar()` y `LlamarAtletaCommand` — preserva todos los eventos existentes en el Event Store; `from_payload` usa `.get("andarivel", 1)`.
3. **`AndarivelesActivosAdapter`** proyecta estado leyendo streams `performance-{cid}-*` filtrando por disciplina y `EstadoPerformance.Llamada` — reutiliza el mismo SQLite sin Event Store separado.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| CodeGuard | ✅ 0 errores |
| Cobertura | ✅ 97% (umbral 85%) |
| DesignReviewer | ✅ 0 CRITICAL (verificado en DoD Inc 2.2) |
| Suite completa | ✅ 424 passed |
