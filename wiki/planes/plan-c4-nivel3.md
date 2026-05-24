---
title: "Plan: Vista C4 Nivel 3 — Componentes internos de cada BC"
type: plan
estado: completado
fecha: "2026-05-23"
fases: [A, B1, B2, B3, B4, B5, B6, C, D]
---

# Plan: Vista C4 Nivel 3

## Objetivo

Llevar el wiki de C4 L2 (Bounded Contexts) a C4 L3 (componentes internos de cada BC),
navegable en Obsidian con Dataview. Herramienta principal: Claude Code como motor de
ingest, leyendo `src/<bc>/` y generando páginas wiki con el patrón existente.

## Punto de partida

- C4 L2 ya completo: 6 páginas `wiki/arquitectura/<bc>.md` con `tipo_ddd`, `persistencia`, `db`, `test_coverage`
- Patrón de ingest establecido (Fases 1–4 del wiki)
- Dataview operativo con frontmatter enriquecido

## Fase A — Schema de componente

**Duración estimada:** 20 min  
**Estado:** pendiente

Definir el tipo de página `arquitectura-componente` antes de generar contenido.

### Nueva estructura de carpetas

```
wiki/arquitectura/
├── competencia.md          ← BC page (ya existe)
├── competencia/            ← nueva subcarpeta de componentes
│   ├── performance.md
│   ├── competencia-aggregate.md
│   ├── event-store-port.md
│   └── ...
├── registro.md
├── registro/
│   └── ...
└── ...
```

### Frontmatter del tipo `arquitectura-componente`

```yaml
---
title: "Competencia — Performance (Aggregate)"
type: arquitectura-componente
bc: competencia
capa: domain              # domain | application | infrastructure | api
tipo_componente: aggregate # aggregate | port | handler | repository | adapter | router
responsabilidad: "..."
interfaces_out: [EventStorePort, AtletaNombrePort]
adr_refs: [ADR-001, ADR-008]
last_updated: "2026-05-23"
---
```

**Granularidad:** componentes de peso (aggregates, ports, handlers, adapters, routers).
No entidades simples ni value objects aislados.

### Acción

Agregar el tipo `arquitectura-componente` al schema en `WIKI.md`.

---

## Fase B — Ingest por BC (6 sesiones)

**Duración estimada:** ~30 min por BC  
**Estado:** pendiente

Una sesión por BC. Claude lee `src/<bc>/` completo y genera las páginas de componentes.

| Sesión | BC | Complejidad | Componentes esperados | Estado |
|--------|----|-------------|----------------------|--------|
| B1 | competencia | Alta (Event Sourcing, 2 aggregates) | ~10–12 páginas | pendiente |
| B2 | registro | Media | ~6–8 páginas | pendiente |
| B3 | bc-torneo | Media | ~6–8 páginas | pendiente |
| B4 | resultados | Media | ~5–7 páginas | pendiente |
| B5 | identidad | Baja | ~4–5 páginas | pendiente |
| B6 | notificaciones | Media (Event Sourcing) | ~5–7 páginas | pendiente |

### Instrucción estándar por sesión

```
Leé src/<bc>/ completo. Para cada componente significativo
(aggregate, port, handler, repository, adapter, router) generá una
página wiki/arquitectura/<bc>/<nombre>.md con el schema
arquitectura-componente. Actualizá wiki/arquitectura/<bc>.md
con un campo componentes: [] que lista las páginas generadas.
Actualizá wiki/index.md y wiki/log.md.
```

---

## Fase C — Vista C4 L2+L3 con Dataview

**Duración estimada:** 20 min  
**Estado:** pendiente

Crear `wiki/vistas/arquitectura.md` con queries que rendericen C4 desde el frontmatter.

### Queries planeadas

**C4 L2 — Contenedores (BCs)**
```dataview
TABLE tipo_ddd, persistencia, test_coverage
FROM "wiki/arquitectura"
WHERE type = "arquitectura" AND tipo_ddd != null
SORT tipo_ddd ASC
```

**C4 L3 — Componentes por BC (ejemplo: competencia)**
```dataview
TABLE tipo_componente, capa, responsabilidad
FROM "wiki/arquitectura/competencia"
WHERE type = "arquitectura-componente"
SORT capa ASC, tipo_componente ASC
GROUP BY capa
```

**Ports (interfaces entre componentes)**
```dataview
TABLE bc, interfaces_out, adr_refs
FROM "wiki/arquitectura"
WHERE type = "arquitectura-componente" AND tipo_componente = "port"
```

**Componentes por tipo en todo el sistema**
```dataview
TABLE WITHOUT ID
  tipo_componente AS "Tipo",
  length(rows) AS "Total",
  map(rows, (r) => r.bc) AS "BCs"
FROM "wiki/arquitectura"
WHERE type = "arquitectura-componente"
GROUP BY tipo_componente
```

---

## Fase D — Cross-referencias

**Duración estimada:** dentro de Fase B  
**Estado:** pendiente

Al generar páginas de componentes, actualizar páginas `wiki/impacto/` existentes
para que apunten al componente concreto:
- `impacto/event-store-port.md` → `[[arquitectura/competencia/event-store-port]]`
- `impacto/atleta-nombre-port.md` → `[[arquitectura/competencia/atleta-nombre-port]]`

---

## Resumen

| Fase | Sesiones | Entregable |
|------|----------|------------|
| A — Schema | 1 | Tipo `arquitectura-componente` en WIKI.md |
| B — Ingest | 6 (1/BC) | ~36–47 páginas nuevas en `wiki/arquitectura/<bc>/` |
| C — Vista | 1 | `wiki/vistas/arquitectura.md` con Dataview C4 L2+L3 |
| D — Cross-refs | dentro de B | Links impacto → componente actualizados |

**Total estimado:** 8 sesiones, ~4 horas.
