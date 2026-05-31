---
title: "Resultados — Query Handlers"
type: arquitectura-componente
bc: resultados
capa: application
tipo_componente: handler
responsabilidad: "4 handlers de consulta: ranking definitivo, ranking provisional (tiempo real), overall, exportación CSV/JSON"
interfaces_out:
  - EventStorePort
adr_refs: [ADR-005, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/resultados/application/queries/obtener_ranking.py
  - src/resultados/application/queries/obtener_ranking_provisional.py
  - src/resultados/application/queries/obtener_overall.py
  - src/resultados/application/queries/exportar_resultados.py
us_origen:
  - US-3.5.3-api-get-resultados-{torneo-id}-overall
  - US-4.6.4-exportar-resultados-descarga-csv-json-del-torneo
  - US-5.6.5-ui-resultados-page-tabla-de-resultados-por-disciplina
  - US-5.6.6-ui-podios-por-division-6-divisiones-fijas
  - US-5.7.3-mis-resultados-result-hero-disciplina-pendiente-card
  - US-5.7.4-rankings-y-podios-para-el-atleta
---

# Query Handlers — BC Resultados

---

## ObtenerRankingHandler

Lee el stream `ranking-{competencia_id}-{disciplina}` de `resultados.db`. Si el stream existe (ranking calculado), reconstituye el aggregate y retorna las entradas agrupadas por categoría con `calculado=True`.

---

## ObtenerRankingProvisionalHandler

**Lectura en tiempo real** — no requiere que el ranking esté calculado.

Lee el stream `performance-{competencia_id}-*` directamente desde `competencia.db` y construye un ranking provisional usando el mismo algoritmo FAAS. Devuelve `calculado=False` en el response.

Usado por el router como fallback cuando el ranking definitivo no existe todavía:

```python
rankings = await handler.handle(...)     # busca en resultados.db
if not calculado:
    rankings = await provisional_handler.handle(...)  # lee competencia.db en tiempo real
```

Incluye información adicional en el provisional: `motivo_dq`, `penalizaciones`, `rp_medido`.

---

## ObtenerOverallHandler

Lee el stream `ranking-overall-{torneo_id}` de `resultados.db`. Reconstituye `RankingOverall` y retorna entradas agrupadas por categoría con `puntos_overall` y `detalle` por disciplina.

---

## ExportarResultadosHandler

El handler más complejo — agrega datos de múltiples fuentes:

1. **BC Torneo**: nombre del torneo, disciplinas habilitadas (via `TorneoRepositoryPort`)
2. **BC Competencia**: competencias del torneo (via `CompetenciasPorTorneoPort`)
3. **BC Resultados**: rankings de cada disciplina + overall (via `ranking_store`)
4. **BC Registro**: nombre, categoría, club del atleta (via `AtletaInfoAdapter` → `registro.db`)

Retorna un DTO `ExportResultadosDTO` con todos los datos consolidados. El router lo serializa a JSON o CSV.

---

## Relaciones

**Contenedor:** [[arquitectura/resultados]]

- Todos instanciados en [[router-resultados]] vía FastAPI `Depends()`
- `ObtenerRankingProvisionalHandler` y `ExportarResultadosHandler` acceden cross-BC directamente a `competencia.db` y `registro.db`
- `ExportarResultadosHandler` también usa `TorneoRepositoryPort` (BC Torneo) configurado vía `configure_resultados_cross_bc_dependencies()`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/resultados/application/queries/obtener_ranking.py` | Query: ObtenerRankingHandler (definitivo) |
| `src/resultados/application/queries/obtener_ranking_provisional.py` | Query: ObtenerRankingProvisionalHandler (tiempo real) |
| `src/resultados/application/queries/obtener_overall.py` | Query: ObtenerOverallHandler |
| `src/resultados/application/queries/exportar_resultados.py` | Query: ExportarResultadosHandler (CSV/JSON) |
