---
title: "Resultados — Command Handlers"
type: arquitectura-componente
bc: resultados
capa: application
tipo_componente: handler
responsabilidad: "2 handlers: CalcularRankingHandler (disciplina) y CalcularOverallHandler (torneo) — orquesta ES y ACL cross-BC"
interfaces_out:
  - EventStorePort
  - ResultadosCompetenciaPort
  - AtletaCategoriaPort
adr_refs: [ADR-001, ADR-005, ADR-008]
last_updated: "2026-05-23"
sources:
  - src/resultados/application/commands/calcular_ranking.py
  - src/resultados/application/commands/calcular_overall.py
us_origen:
  - US-2.4.2-calcular-ranking-—-bc-resultados-nucleo
  - US-3.5.1-aggregate-ranking-overall-calcular-overall-handler
  - US-3.5.2-politica-p-09-overall-automatico-al-cerrar-torneo
  - US-5.6.3-ranking-competencia-con-puntos-por-categoria
  - US-5.6.4-ranking-overall-puntos-acumulados-por-categoria-y
  - US-6.4.2-materializar-proyeccion-competencias-por-torneo-en
tests:
  - tests/features/US-2.4.2-calcular-ranking.feature
  - tests/integration/resultados/test_calcular_ranking_integration.py
  - tests/features/US-3.5.1-ranking-overall.feature
  - tests/integration/resultados/test_calcular_overall_integration.py
  - tests/features/US-3.5.2-politica-p09.feature
  - tests/features/US-5.6.3-ranking-puntos-faas.feature
  - tests/features/US-5.6.4-ranking-overall-puntos.feature
  - tests/features/US-6.4.2-proyeccion-overall.feature
---

# Command Handlers — BC Resultados

---

## CalcularRankingHandler

El handler central del BC. Orquesta la lectura cross-BC, el enriquecimiento con categoría y la persistencia ES.

```python
class CalcularRankingHandler:
    def __init__(
        self,
        ranking_store: EventStorePort,         # resultados.db
        resultados_port: ResultadosCompetenciaPort,  # ACL → competencia.db
        atleta_categoria_port: AtletaCategoriaPort | None = None,  # ACL → registro.db
        descriptor: DisciplinaDescriptor | None = None,
        algoritmo: AlgoritmoPuntaje | None = None,  # AlgoritmoPuntajeFAAS
    ): ...
```

### Flujo

```
1. resultados_crudos = resultados_port.get_resultados_finales(competencia_id, disciplina)
   → Lee streams performance-{id}-* de competencia.db
2. resultados = _enriquecer_con_categoria(resultados_crudos)
   → Por cada resultado: atleta_categoria_port.get_categoria(atleta_id) → registro.db
3. stream_id = f"ranking-{competencia_id}-{disciplina.value}"
4. existing = ranking_store.load(stream_id)
   → Reconstitución desde resultados.db
5. ranking = RankingCompetencia.reconstitute(competencia_id, disciplina, existing)
6. ranking.calcular(resultados, algoritmo)
   → Emite ResultadosCalculados, pobla _entries
7. for event in ranking.pull_events():
       ranking_store.append(stream_id, event)
```

### Stream ID canónico

```
ranking-{competencia_id}-{disciplina.value}
```

---

## CalcularOverallHandler

```python
class CalcularOverallHandler:
    def __init__(
        self,
        ranking_store: EventStorePort,  # resultados.db
        # También necesita cargar rankings por disciplina del mismo store
    ): ...
```

### Flujo

```
1. Carga los rankings de cada disciplina del torneo desde resultados.db
   (stream_id = "ranking-{competencia_id}-{disciplina}" por disciplina)
2. RankingOverall.reconstitute(torneo_id, events)
3. overall.calcular(torneo_id, rankings_por_disciplina)
   → INV-5.6.4-04: falla si alguna disciplina no tiene ranking
4. overall.pull_events() → append a stream "ranking-overall-{torneo_id}"
```

---

## Relaciones

**Contenedor:** [[arquitectura/resultados]]

- Orquesta [[ranking-competencia]] y [[ranking-overall]]
- Usa [[resultados-competencia-port]] (ACL cross-BC)
- Usa [[algoritmo-faas]] como estrategia de puntuación
- Instanciados en [[router-resultados]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/resultados/application/commands/calcular_ranking.py` | Handler: CalcularRankingHandler |
| `src/resultados/application/commands/calcular_overall.py` | Handler: CalcularOverallHandler |
