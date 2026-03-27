# Reporte Final — US-2.4.2: CalcularRanking (BC Resultados núcleo)

**Fecha:** 2026-03-27
**Branch:** feature/US-2.4.2-calcular-ranking
**Duración total:** ~26 min (incluyendo continuación de sesión)

---

## Resumen Ejecutivo

US-2.4.2 implementa el núcleo del BC Resultados: el cálculo automático de rankings
al finalizar una disciplina. El ranking aplica RF-PM-03 — empates comparten posición
y la siguiente se omite, podio para posiciones 1-2-3, DNS y tarjeta roja al final.

La US completa el Inc 2.4 (y con él el SP2) y cierra la cadena:
`performance_finalizada → P-08 → CompetenciaFinalizada → on_finalizada → CalcularRanking`.

---

## Artefactos Producidos

### Dominio (`src/resultados/domain/`)
| Archivo | Descripción |
|---------|-------------|
| `aggregates/ranking_competencia.py` | Aggregate raíz — `calcular()` + `reconstitute()` |
| `events/resultados_calculados.py` | Evento `ResultadosCalculados` |
| `ports/resultados_competencia_port.py` | Puerto ACL + `ResultadoFinal` DTO |
| `value_objects/entrada_ranking.py` | Value Object `EntradaRanking` |
| `exceptions.py` | `ResultadosIncompletos`, `RankingYaCalculado` |

### Aplicación (`src/resultados/application/`)
| Archivo | Descripción |
|---------|-------------|
| `commands/calcular_ranking.py` | `CalcularRankingCommand` + `CalcularRankingHandler` |
| `queries/obtener_ranking.py` | `ObtenerRankingQuery` + `ObtenerRankingHandler` + `RankingEntradaDTO` |

### Infraestructura (`src/resultados/infrastructure/`)
| Archivo | Descripción |
|---------|-------------|
| `repositories/resultados_competencia_adapter.py` | ACL → lee streams del BC Competencia |

### API (`src/resultados/api/`)
| Archivo | Descripción |
|---------|-------------|
| `router.py` | `GET /resultados/{competencia_id}/ranking?disciplina=...` |

### Integración (`src/`)
| Archivo | Modificación |
|---------|-------------|
| `app.py` | Incluye `resultados_router` |
| `competencia/api/router.py` | `get_on_finalizada_callback` inyecta `CalcularRankingHandler` tras `CompetenciaFinalizada` |
| `competencia/application/commands/asignar_tarjeta.py` | `on_finalizada` callback |
| `competencia/application/commands/registrar_dns.py` | `on_finalizada` callback |
| `competencia/application/_p08_finalizacion.py` | Helper P-08 con callback opcional |

### Tests
| Suite | Cantidad |
|-------|----------|
| Unit — `RankingCompetencia` | 14 tests |
| Unit — `CalcularRankingHandler` / `ObtenerRankingHandler` | 7 tests |
| Integration — flujo completo | 6 tests |
| BDD — 7 escenarios | 7 tests |
| **Total US-2.4.2** | **34 tests** |

---

## Bugs Encontrados y Corregidos

| Bug | Causa | Fix |
|-----|-------|-----|
| `posicion_actual = pos + 1` incorrecto en empates | Tras empate, siguiente posición no se saltaba | `posicion_actual = len(entries) + 1` |
| `self._descriptor.get()` no existe | `DisciplinaDescriptorAdapter` expone `.describe()`, no `.get()` | Corrección en `calcular_ranking.py:82` |
| Imports sin usar en `obtener_ranking.py` | `Decimal` y `EntradaRanking` importados pero no usados | Eliminados |

---

## Métricas de Calidad

| Métrica | Valor |
|---------|-------|
| Cobertura BC Resultados | 97% |
| CodeGuard CRITICAL | 0 |
| CodeGuard errores | 0 |
| CodeGuard advertencias post-fix | 0 |
| Total tests suite (481 → +34) | 481 pasando |

---

## Decisiones Técnicas

**Cross-BC sin acoplamiento:** BC Competencia nunca importa BC Resultados.
El `on_finalizada: Callable[[UUID, Disciplina], Awaitable[None]] | None` es inyectado
por el router FastAPI (capa de composición). En SP4+ se reemplaza por event bus.

**Empate con `posicion_actual = len(entries) + 1`:** más simple y correcto que
incrementar manualmente: siempre apunta a la siguiente posición secuencial
independientemente de cuántos empates ocurrieron antes.

**Unidad del RP tomada del AP:** `ResultadosCompetenciaAdapter` usa
`performance.ap.unidad.value` porque el RP no almacena su unidad por separado
(AP y RP siempre comparten unidad en la misma disciplina — invariante del dominio).

---

## Estado del Incremento 2.4

| US | Descripción | Estado |
|----|-------------|--------|
| US-2.4.1 | `CompetenciaFinalizada` automático (P-08) | ✅ Done — PR #33 |
| US-2.4.2 | `CalcularRanking` — BC Resultados núcleo | ✅ Done — este PR |

**Inc 2.4 completo → SP2 completo.**
