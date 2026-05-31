---
title: "Vista de Trazabilidad — Cadena completa"
type: vista
last_updated: "2026-05-31"
sources:
  - wiki/trazabilidad/
  - wiki/arquitectura/
  - wiki/decisiones/
---

# Vista de Trazabilidad

> **Pregunta central:** este requerimiento inicial, ¿cómo se validó?

## Dos tracks de trazabilidad

```
Track de validación:
RF ──► US ──► Componente ──► Test
 ↑     ↑           ↑
 └─ rf: ─┘   componentes_wiki:   us_origen: / tests:

Track de diseño:
RNF ──► ADR ──► BC ──► Componente
  ↑       ↑
  └ adr_refs: ─┘  rnf_refs:
```

Los dos tracks convergen en el **Componente** — es el nodo donde un requisito funcional (RF→US) se encuentra con una decisión arquitectónica (RNF→ADR).

---

## Navegación de referencia

### "¿Cómo se validó RF-EJ-06 (corrección de resultados)?"

[[trazabilidad/rf/RF-EJ-06-correccion-resultado-registrado]]
→ `us_refs:` → [[trazabilidad/us/US-1.2.6-corregir-resultado]]
→ `componentes_wiki:` → [[arquitectura/competencia/command-handlers]]
→ `tests:` → `tests/features/US-1.2.6-corregir-resultado.feature`

### "¿Por qué se eligió Event Sourcing en Competencia?"

[[trazabilidad/rnf/RNF-01-confiabilidad-persistencia-event-sourcing]]
→ `adr_refs:` → [[decisiones/ADR-001-event-sourcing-competencia]]
→ `bcs_afectados:` → [[arquitectura/competencia]]
→ `us_origen:` → [[trazabilidad/us/US-1.1.1-setup-esqueleto-bc-competencia]]

### "¿Qué USs construyeron competencia-aggregate?"

[[arquitectura/competencia/competencia-aggregate]]
→ `us_origen:` → lista de USs
→ cada US → `rf:` → RF que motivó la US
→ cada US → `test_units:` → tests que la validan

---

## Cobertura de RFs

```dataview
TABLE rf_id, estado, length(us_refs) AS "USs", area
FROM "wiki/trazabilidad/rf"
WHERE type = "trazabilidad-rf-item"
SORT area ASC, rf_id ASC
```

---

## Cadena RF → US → Componente

```dataview
TABLE us_id, rf, componentes_wiki, test_units
FROM "wiki/trazabilidad/us"
WHERE type = "trazabilidad-us"
  AND rf != null AND length(rf) > 0
  AND componentes_wiki != null
SORT rf ASC, us_id ASC
```

---

## Track de diseño — RNF → ADR

```dataview
TABLE rnf_id, atributo, adr_refs, bcs_afectados
FROM "wiki/trazabilidad/rnf"
WHERE type = "trazabilidad-rnf"
SORT rnf_id ASC
```

---

## Componentes con trazabilidad completa

> Componentes que tienen: us_origen + tests (cadena cerrada)

```dataview
TABLE bc, tipo_componente, length(us_origen) AS "USs origen", length(tests) AS "Tests"
FROM "wiki/arquitectura"
WHERE type = "arquitectura-componente"
  AND us_origen != null
  AND tests != null
SORT bc ASC, tipo_componente ASC
```

---

## Gaps — preguntas sin respuesta

### RFs sin USs asignadas

```dataview
TABLE rf_id, area, estado
FROM "wiki/trazabilidad/rf"
WHERE type = "trazabilidad-rf-item"
  AND (us_refs = null OR length(us_refs) = 0)
SORT area ASC
```

### USs cerradas sin componente wiki

```dataview
TABLE us_id, bc, sp
FROM "wiki/trazabilidad/us"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND (componentes_wiki = null OR length(componentes_wiki) = 0)
SORT bc ASC
```

### USs cerradas sin tests

```dataview
TABLE us_id, bc, sp
FROM "wiki/trazabilidad/us"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND (test_units = null OR length(test_units) = 0)
SORT bc ASC
```

### ADRs sin RNF motivador

```dataview
TABLE file.name, bcs_afectados
FROM "wiki/decisiones"
WHERE type = "decision"
  AND rnf_refs = null
SORT file.name ASC
```

---

## Distribución de USs

### Por BC

```dataview
TABLE WITHOUT ID
  bc AS "BC",
  length(rows) AS "Total",
  length(filter(rows, (r) => r.estado = "cerrada")) AS "Cerradas",
  length(filter(rows, (r) => r.componentes_wiki != null AND length(r.componentes_wiki) > 0)) AS "Con componente"
FROM "wiki/trazabilidad/us"
WHERE type = "trazabilidad-us"
GROUP BY bc
SORT bc ASC
```

### Por estado

```dataview
TABLE WITHOUT ID
  estado AS "Estado",
  length(rows) AS "Total"
FROM "wiki/trazabilidad/us"
WHERE type = "trazabilidad-us"
GROUP BY estado
```

---

## Páginas hub de trazabilidad

| Página | Rol en la cadena |
|---|---|
| [[conceptos/atributos-calidad]] | Origen del track de diseño — 8 RNFs |
| [[trazabilidad/rf/RF-EJ-06-correccion-resultado-registrado]] | RF de referencia — cadena completa documentada |
| [[trazabilidad/rnf/RNF-01-confiabilidad-persistencia-event-sourcing]] | RNF fundacional — motiva ADR-001 |
| [[arquitectura/competencia/command-handlers]] | Componente con más trazabilidad (27 tests) |
| [[arquitectura/competencia/competencia-aggregate]] | Aggregate con más us_origen (17 USs) |
| [[RF-ejecucion]] | Hub de RFs del Core Domain |
| [[vistas/arquitectura]] | Vista complementaria — C4 L1→L4 |
