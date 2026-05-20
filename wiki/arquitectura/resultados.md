---
title: "BC Resultados — Supporting Domain"
type: arquitectura
last_updated: "2026-05-20"
sources:
  - docs/architecture/13-bc-resultados.md
tipo_ddd: Supporting Domain
persistencia: CRUD + stream propio
db: resultados.db
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
