---
title: "Graphify — Knowledge Graph del código fuente (v0.8.18)"
type: impacto
last_updated: "2026-05-28"
sources:
  - src/graphify-out/GRAPH_REPORT.md
  - src/graphify-out/graph.json
graphify_commit: "bd4770b7"
graphify_version: "0.8.18"
extraction: "Semántica (Claude Haiku + AST Tree-sitter)"
---

# Graphify — Knowledge Graph del código fuente

> Generado: 2026-05-28 — Extracción semántica (Claude Haiku + AST Tree-sitter)
> Commit base: `bd4770b7` — ejecutar `graphify update src/` para mantener actualizado
> Comunidades nombradas manualmente desde `.graphify_labels.json`

---

## Estadísticas del grafo

| Métrica | Valor |
|---------|-------|
| Archivos procesados | 305 |
| Nodos | 2.706 |
| Edges | 15.865 |
| Comunidades | 777 (181 mostradas, 596 thin omitidas) |
| Edges extraídos (AST) | 19% |
| Edges inferidos (modelo) | 81% |
| Confianza promedio inferidos | 0.5 |

---

## God Nodes — Las abstracciones más conectadas

Estos son los nodos de mayor centralidad: cambiarlos tiene el mayor efecto en cascada.

| Rango | Nodo | Edges | Interpretación |
|-------|------|-------|----------------|
| 1 | `Disciplina` | 541 | Value object compartido — puente entre los 6 BCs vía `shared/domain` |
| 2 | `EventStorePort` | 319 | Puerto cross-BC — toda la infraestructura de ES pasa por aquí |
| 3 | `Performance` | 206 | Aggregate raíz del Core Domain — nodo de mayor densidad semántica |
| 4 | `PenalizacionTecnicaBody` | 186 | Body de la API — expuesto en múltiples endpoints de tarjeta |
| 5 | `UnidadMedida` | 151 | Value object de medición — metros/segundos, transversal |
| 6 | `CorregirResultadoTrasDNSBody` | 148 | Body de corrección post-DNS — command cross-BC |
| 7 | `FinalizarCompetenciaManualHandler` | 146 | Handler de cierre de competencia |
| 8 | `AsignarJuezPerformanceHandler` | 145 | Handler de asignación de juez a performance |
| 9 | `ObtenerPerformanceActualHandlerDep` | 145 | Dependency injection del handler de performance activa |
| 10 | `CompetenciasPorTorneoPort` | 133 | ACL entre BC Resultados y BC Torneo |

**Lectura:** los 3 primeros god nodes (`Disciplina`, `EventStorePort`, `Performance`) concentran el mayor riesgo de cambio en cascada del sistema.

---

## Comunidades principales (nombradas)

El grafo detectó 777 comunidades. Las 24 más grandes (≥ 10 nodos) tienen nombres significativos asignados:

| ID | Nodos | Nombre | BC / Área |
|----|-------|--------|-----------|
| 0 | 267 | Registro & Cross-BC Infrastructure | BC Registro + ACL + Adjuntos |
| 1 | 234 | Competencia Grilla & Handlers | BC Competencia — ejecución y grilla |
| 2 | 166 | Identidad & Roles | BC Identidad — usuarios, JWT, roles |
| 3 | 150 | Torneo & Disciplinas | BC Torneo — ciclo de vida, disciplinas |
| 4 | 145 | Resultados & Exportación | BC Resultados — rankings, CSV/JSON |
| 5 | 115 | Competencia Correcciones | BC Competencia — corrección de resultados |
| 6 | 92 | Competencia Estado & Eventos | BC Competencia — máquina de estados |
| 7 | 81 | Notificaciones Core | BC Notificaciones — aggregate |
| 8 | 74 | Resultados Ranking Engine | BC Resultados — motor de cálculo |
| 9 | 65 | Shared Domain Base | `shared/` — base classes, eventos de dominio |
| 10 | 61 | Competencia API Schemas | BC Competencia — schemas de la API |
| 11 | 56 | Application Wiring | `app.py` + cross-BC callbacks |
| 12 | 52 | Ranking Entries Calculation | BC Resultados — cálculo de entries |
| 13 | 43 | Competencia Llamado Atleta | BC Competencia — llamado al OT |
| 14 | 42 | Performance Value Objects | BC Competencia — VOs de Performance |
| 15 | 39 | Competencia Ejecución & DNS | BC Competencia — tarjeta, DNS, finalización |
| 16 | 36 | Competencia Aggregate Root | BC Competencia — aggregate Competencia |
| 17 | 34 | Performance Events Factory | BC Competencia — fábrica de eventos de Performance |
| 18 | 24 | Notificaciones Commands & Policies | BC Notificaciones — commands, políticas P10/P11 |
| 19 | 17 | Resultados Overall Ranking | BC Resultados — Overall multi-torneo |
| 20 | 15 | Registro Inscripción Repository | BC Registro — repository SQLite de inscripción |
| 21 | 13 | Performance State Machine | BC Competencia — apply events de Performance |
| 22 | 11 | Notificaciones Event Store | BC Notificaciones — SQLite event store |
| 23 | 11 | Shared Value Objects | `shared/domain/value_objects/` |

---

## Conexiones sorprendentes (Graphify)

Relaciones inferidas que el grafo detectó y que no son obvias desde los docs:

- `Disciplina` → `Disciplina` [INFERRED] — `_stream_ids.py` re-importa desde `shared/` pero también desde el módulo local (doble fuente)
- `Disciplina` → `Disciplina` [INFERRED] — `competencia/domain/ports/performances_estado_port.py` → `shared/domain/value_objects/disciplina.py`
- `PoliticaP10Handler` → `Competencia` [INFERRED] — `app.py` conecta BC Notificaciones con el aggregate de BC Competencia vía policy
- `PoliticaP10Handler` → `Inscripcion` [INFERRED] — la política P10 accede a datos de inscripción cross-BC vía `app.py`

---

## Queries útiles desde CLI

Con el grafo generado, estas queries están disponibles sin abrir el código:

```bash
# Camino más corto entre dos componentes
graphify path "Performance" "Notificacion" --graph src/graphify-out/graph.json

# Explorar un concepto y sus vecinos
graphify explain "EventStorePort" --graph src/graphify-out/graph.json

# Preguntar al grafo en lenguaje natural
graphify query "¿qué handlers dependen de InscripcionRepositoryPort?" --graph src/graphify-out/graph.json

# Qué se rompe si cambio X
graphify affected "SQLiteEventStore" --graph src/graphify-out/graph.json
```

---

## Integración con el LLM Wiki

Según el plan del POC (Fase 5 / Extensión Graphify), el workflow de actualización es:

```
# Después de cada cierre de SP o cambio significativo en src/:
graphify update src/          # AST re-extraction (no API cost)
# O extracción completa con semántica:
graphify extract src/ --backend claude   # requiere ANTHROPIC_API_KEY

# Luego el wiki ingest actualiza wiki/impacto/ con dependencias reales
```

**Trigger recomendado:** al crear un nuevo baseline `BL-*.md`, ejecutar `graphify update src/` y actualizar este archivo.

---

## Notas sobre extracción actual

- **19% EXTRACTED** = relaciones detectadas por Tree-sitter con certeza
- **81% INFERRED** = relaciones razonadas por el modelo semántico (confianza 0.5) — válidas como pistas, no como verdad absoluta
- La extracción semántica (`graphify-extract.sh`) ya fue ejecutada; el porcentaje INFERRED alto es esperable en un codebase Python con tipado implícito
- `graph.html` (~6.5 MB) es navegable en browser pero lento — preferir `graph_tree.html` (211 KB, árbol colapsable D3) para navegación cotidiana
- Comunidades nombradas: 24 de 777 (las que tienen ≥ 10 nodos y son visibles en el reporte)

---

*Graphify v0.8.18 — MIT License — [github.com/safishamsi/graphify](https://github.com/safishamsi/graphify)*
