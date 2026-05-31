---
title: "BC Resultados — Supporting Domain"
type: arquitectura
last_updated: "2026-05-23"
sources:
  - docs/architecture/13-bc-resultados.md
l1_ref: "[[arquitectura/sistema]]"
tipo_ddd: supporting
persistencia: CRUD + stream propio
db: resultados.db
test_coverage: null
componentes:
  - arquitectura/resultados/ranking-competencia
  - arquitectura/resultados/ranking-overall
  - arquitectura/resultados/resultados-competencia-port
  - arquitectura/resultados/algoritmo-faas
  - arquitectura/resultados/command-handlers-resultados
  - arquitectura/resultados/query-handlers-resultados
  - arquitectura/resultados/router-resultados
---

# BC Resultados — Supporting Domain

## Rol

**Supporting Domain.** Transforma el cierre de una disciplina en una vista ordenada y publicable del ranking final, sin reimplementar la lógica deportiva de Competencia.

**Responsabilidades:** calcular posiciones, empates y podio; persistir el ranking calculado; exponer consultas por `competenciaId` y `disciplina`; publicar ranking overall; exportar resultados (CSV/JSON).

## Persistencia

Stream propio por ranking en `resultados.db`. Stream: `ranking-{competencia_id}-{disciplina}`. El aggregate `RankingCompetencia` se reconstituye desde ese stream. Aunque clasificado como CRUD en el diseño general, en implementación materializa el ranking mediante Event Sourcing.

## Aggregate principal: RankingCompetencia

**Responsabilidades:** ordenar performances válidas por mejor RP (distancia o tiempo), ubicar DNS y rojas al final, asignar posiciones con manejo de empates, marcar podio, emitir `ResultadosCalculados`.

### Evento: ResultadosCalculados

Persiste: competencia, disciplina, cantidad de entradas, snapshot serializado de filas del ranking, timestamp de cálculo.

### Value Object: EntradaRanking

Posición, atleta, marca efectiva (RP), unidad, tarjeta, indicador DNS, indicador de podio.

## Estructura de capas

| Capa | Responsabilidad |
|------|----------------|
| `api/` | `GET /resultados/{competencia_id}/ranking`, `GET /resultados/{torneo_id}/overall`, `GET /resultados/{torneo_id}/export` |
| `application/` | `CalcularRankingHandler`, `ObtenerRankingHandler`, `ObtenerRankingProvisionalHandler` (SP5), `CalcularOverallHandler`, `ExportarResultadosHandler` |
| `domain/` | `RankingCompetencia`, `EntradaRanking`, `ResultadosCalculados`, `ResultadosCompetenciaPort` |
| `infrastructure/` | `ResultadosCompetenciaAdapter` (ACL → Competencia), `DisciplinaDescriptorAdapter`, `SQLiteEventStore` |

## Componentes (C4 L3)

| Componente | Capa | Tipo | Responsabilidad |
|---|---|---|---|
| [[arquitectura/resultados/ranking-competencia\|RankingCompetencia]] | domain | aggregate | Calcula y persiste el ranking de una disciplina — Event Sourcing |
| [[arquitectura/resultados/ranking-overall\|RankingOverall]] | domain | aggregate | Ranking general del torneo sumando puntos FAAS de todas las disciplinas |
| [[arquitectura/resultados/algoritmo-faas\|AlgoritmoFAAS]] | domain | service | Reglamento FAAS: 3 fórmulas según tipo de disciplina |
| [[arquitectura/resultados/resultados-competencia-port\|ResultadosCompetenciaPort]] | domain | port | ACL hacia BC Competencia (performances) y BC Registro (categorías) |
| [[arquitectura/resultados/command-handlers-resultados\|Command Handlers]] | application | handler | 2 handlers: CalcularRanking y CalcularOverall |
| [[arquitectura/resultados/query-handlers-resultados\|Query Handlers]] | application | handler | 4 handlers: ranking definitivo, provisional, overall, exportación |
| [[arquitectura/resultados/router-resultados\|Router Resultados]] | api | router | API HTTP: 3 endpoints (ranking, overall, export) |

## Integración de entrada: Competencia

**Mecanismo principal:** Evento `CompetenciaFinalizada`. `ResultadosCompetenciaAdapter` carga streams `performance-*` desde `competencia.db`, reconstituye cada `Performance`, filtra estados `Ejecutada` y `DNS`, traduce a `ResultadoFinal`.

**Deuda técnica conocida:** `ObtenerRankingProvisionalHandler` (SP5) lee `competencia.db` directamente cuando no existe `ResultadosCalculados` — lectura cross-BC fuera del ACL formal.

## Integración de entrada: Torneo

Consulta read-only por `torneoId` para enriquecer publicación de resultados y overall. No depende de Torneo para validar lógica de ranking.

## Separación cálculo / lectura

La consulta HTTP no recalcula el ranking en runtime. Carga el stream, reconstituye `RankingCompetencia`, devuelve las entradas ya materializadas por el último `ResultadosCalculados`.

## ADRs relacionados

- [[ADR-001-event-sourcing-competencia]] — la fuente de datos de este BC
- [[ADR-005-bounded-contexts-ddd-estrategico]] — posición downstream de Competencia
- [[ADR-014-penalizaciones-acumulables]] — `BlancaConPenalizaciones` es tarjeta válida para ranking

## Salud (BL-006 · v1.0.0 · 2026-05-16)

### ArchitectAnalyst

| Métrica | Valor | Severidad | Tendencia |
|---------|-------|-----------|-----------|
| Distancia (D) | < umbral alerta | INFO | — |
| should_block | false | — | — |

BC Resultados no aparece en los reportes de alerta de DistanceAnalyzer en BL-005 ni BL-006 — su D está por debajo del umbral de aviso. El mejor indicador de salud arquitectónica de los BCs funcionales.

### DesignReviewer

| Total WARNING | Top smells |
|:---:|---|
| **40** | LongMethod (27) · FeatureEnvy (3) |

LongMethod concentrado en `RankingCompetencia` y `RankingOverall` — clases con lógica de cálculo compleja por diseño (FAAS, agrupación por categoría/género, empates). El patrón fue auditado en BL-006 (decisión DR-01: LCOM=2 en `RankingCompetencia` es falso positivo de Event Sourcing). Sin CRITICAL.

### Cobertura

Suite más densa del proyecto: 91 tests en `US-5.6.4` solos. Tests de integración y BDD desde SP2.
