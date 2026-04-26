# Reporte de Implementación — US-5.6.2

**Historia:** TipoReglamento en Torneo + DI de AlgoritmoPuntaje en CalcularRanking  
**Incremento:** INC-5.6  
**Subproyecto:** SP5 — La Puesta en Marcha  
**Producto:** torneo + resultados  
**Fecha:** 2026-04-26  

---

## Resumen Ejecutivo

Introduce el VO `TipoReglamento` (FAAS/CMAS/AIDA) en el BC Torneo y extiende `CalcularRankingHandler` para recibir `AlgoritmoPuntaje` por inyección de dependencias. El dominio de resultados queda desacoplado del reglamento concreto.

**Estado final:** ✅ Completo — 0 errores, 0 advertencias CodeGuard

---

## Artefactos Producidos

| Artefacto | Ruta | Tipo |
|-----------|------|------|
| `TipoReglamento` VO | `torneo/domain/value_objects/tipo_reglamento.py` | Nuevo |
| `Torneo` + campo | `torneo/domain/aggregates/torneo.py` | Modificado |
| Repo SQLite + migración | `torneo/infrastructure/repositories/sqlite_torneo_repository.py` | Modificado |
| `CalcularRankingHandler` DI | `resultados/application/commands/calcular_ranking.py` | Modificado |
| `__init__.py` exports | `torneo/domain/value_objects/__init__.py` | Modificado |
| Tests unitarios | `tests/unit/torneo/domain/test_tipo_reglamento.py` | Nuevo |
| Tests integración | `tests/integration/torneo/test_tipo_reglamento_repository.py` | Nuevo |
| Feature BDD | `tests/features/US-5.6.2-tipo-reglamento-di-ranking.feature` | Nuevo |
| Steps BDD | `tests/features/steps/test_US_5_6_2_steps.py` | Nuevo |
| CodeGuard report | `quality/reports/codeguard/US-5.6.2-codeguard-raw.json` | Nuevo |

---

## Resultados de Tests

| Suite | Tests | Estado |
|-------|-------|--------|
| Unitarios — `TestTipoReglamento` | 3 | ✅ |
| Unitarios — `TestTorneoTipoReglamento` | 3 | ✅ |
| Unitarios — `TestCalcularRankingDI` | 2 | ✅ |
| Integración — persistencia SQLite | 4 | ✅ |
| BDD — 3 escenarios | 3 | ✅ |
| **Total US-5.6.2** | **15** | **✅** |

Regresión torneo + resultados: 157 tests pasando.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| CodeGuard — errores | 0 |
| CodeGuard — advertencias | 0 |
| PEP8 | ✅ Compliant |
| Seguridad | ✅ Sin issues (B110 preexistente en patrón migración — intencional) |

---

## Decisiones Técnicas

- **`TipoReglamento` como `StrEnum`:** mismo patrón que `EstadoTorneo` en el BC; default `FAAS` garantiza retro-compatibilidad con torneos existentes (INV-5.6.2-01).
- **Migración `ALTER TABLE`:** `_ADD_TIPO_REGLAMENTO_COLUMN` con `DEFAULT 'FAAS'` — bases de datos existentes se migran sin pérdida de datos.
- **DI opcional:** `algoritmo: AlgoritmoPuntaje | None = None` — el handler puede construirse sin algoritmo para no romper tests legacy; el wiring real ocurre en US-5.6.3.
