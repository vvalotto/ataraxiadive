---
title: "Torneo — Query Handlers"
type: arquitectura-componente
bc: torneo
capa: application
tipo_componente: handler
responsabilidad: "3 handlers de consulta: torneo por ID, lista de torneos, disciplinas asignadas a un juez"
interfaces_out:
  - TorneoRepositoryPort
adr_refs: [ADR-005]
last_updated: "2026-05-23"
sources:
  - src/torneo/application/queries/obtener_torneo.py
  - src/torneo/application/queries/obtener_disciplinas_juez.py
us_origen:
  - US-5.1.10-normalizacion-del-campo-estado-en-fetch-torneo
  - US-5.1.2-detalle-torneo-page-tabs-y-panel-de-acciones-de-fase
  - US-5.1.5-jueces-panel-asignacion-de-juez-por-disciplina
  - US-5.1.7-politica-de-tabs-por-fase-en-detalle-torneo-page
  - US-5.1.8-torneo-competencias-page-composicion-disciplinas
tests:
  - tests/features/US-5.1.10-acciones-fase.feature
  - tests/features/US-5.1.2-gestion-fases-torneo.feature
  - tests/features/US-5.1.5-asignacion-jueces.feature
  - tests/features/US-5.1.7-politica-tabs.feature
  - tests/features/US-5.1.8-componer-competencias.feature
---

# Query Handlers — BC Torneo

---

## ObtenerTorneoHandler

```python
Query: ObtenerTorneoQuery(torneo_id: UUID)
Retorna: Torneo
```

`find_by_id()` o lanza `TorneoNoEncontrado`.

---

## ListarTorneosHandler

```python
Query: ListarTorneosQuery()
Retorna: list[Torneo]
```

`find_all()` — sin filtros en la capa de aplicación. El router filtra los `CANCELADO` antes de responder.

---

## ObtenerDisciplinasDeJuezHandler

```python
async def handle(self, torneo_id: UUID, juez_id: UUID) -> list[Disciplina]
```

Carga el torneo, llama `torneo.obtener_disciplinas_de_juez(juez_id)`. Usado por el portal del juez para saber qué disciplinas debe supervisar en un torneo dado.

---

## Relaciones

**Contenedor:** [[arquitectura/torneo]]

- Instanciados en [[router-torneo]]
- Usan [[sqlite-torneo-repository]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/torneo/application/queries/obtener_torneo.py` | Query: ObtenerTorneoHandler |
| `src/torneo/application/queries/obtener_disciplinas_juez.py` | Query: ObtenerDisciplinasJuezHandler |
