---
title: "Vista de Trazabilidad"
type: vista
last_updated: "2026-05-24"
sources:
  - wiki/trazabilidad/
  - docs/traceability/matrix.md
---

# Vista de Trazabilidad

> El sistema visto desde los requerimientos hacia la implementación.

## Propósito

Responder preguntas sobre qué requerimiento funcional implementa cada parte del sistema, qué tests lo verifican y cuál es el estado de cobertura. Es la vista del QA, el auditor y el desarrollador que necesita entender el alcance antes de modificar algo.

## Stakeholder principal

QA, auditor de calidad, desarrollador implementando o modificando un requerimiento.

---

## Estado actual del wiki

```dataview
TABLE WITHOUT ID
  length(rows) AS "Total US",
  estado AS "Estado"
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
GROUP BY estado
SORT length(rows) DESC
```

---

## Preguntas características y recorridos

### 1. ¿Qué requerimientos cubre el área de ejecución?

El área de ejecución concentra las reglas más complejas del dominio: tarjetas, DNS, black-out, correcciones del juez, cronometraje manual.

**Recorrido (estado actual):**
[[RF-ejecucion]] → [[performance]] → [[tarjeta]] → [[arquitectura/competencia]] → [[ADR-014-penalizaciones-acumulables]]

**Recorrido completo:**
[[RF-ejecucion]] → `US-X.Y.Z` → código en `src/competencia/` → tests en `tests/features/` → reporte de cierre

**Requerimiento pendiente de elicitación:** RF-EJ-04 (códigos de penalización AIDA/CMAS).

---

### 2. ¿Qué requerimientos cubre el ciclo de vida del torneo?

Gestión del torneo incluye: creación, configuración de disciplinas, inscripciones, etapas reversibles, y cierre sin eliminación de datos.

**Recorrido (estado actual):**
[[RF-gestion-torneo]] → [[torneo]] (concepto) → [[arquitectura/bc-torneo]]

**Regla clave documentada:** las disciplinas son configurables; el set inicial es STA, DNF, DBF, DYN, SPE. Las transiciones entre fases son reversibles.

---

### 3. ¿Qué requerimientos cubre la inscripción de atletas?

Inscripción define: categorías, brevet, límites de participantes, apto médico, constancia de pago, datos del club.

**Recorrido (estado actual):**
[[RF-inscripcion-atletas]] → [[atleta]] → [[arquitectura/registro]]

**Requerimiento pendiente:** RF-IN-07 (resolución de conflictos con BD externa) — sin implementar.

---

### 4. ¿Qué requerimientos de preparación generan la grilla?

La preparación comprende: generación de grilla, anuncios de marcas, configuración de disciplinas.

**Recorrido (estado actual):**
[[RF-preparacion]] → [[grilla]] → [[anuncio]] → [[arquitectura/competencia]]

---

### 5. ¿Qué áreas de requerimientos tienen pendientes sin implementar?

| Área RF | Página | Pendientes |
|---------|--------|-----------|
| Inscripción | [[RF-inscripcion-atletas]] | RF-IN-07 (conflicto BD externa) |
| Ejecución | [[RF-ejecucion]] | RF-EJ-04 (códigos penalización) |
| Resultados | [[RF-resultados]] | RF-PM-01 (sistema de puntos) |
| Notificaciones | [[RF-notificaciones]] | RF-NT-03 |
| Integración | [[RF-integracion]] | Toda el área (4 RFs pendientes) |
| Gestión torneo | [[RF-gestion-torneo]] | Ninguno |
| Preparación | [[RF-preparacion]] | Ninguno |
| Usuarios/roles | [[RF-usuarios-roles]] | Ninguno |

---

### 6. ¿Cómo se traza un requerimiento hasta su implementación?

La cadena canónica en AtaraxiaDive es:

```
RF (área) → US (historia de usuario) → código en src/<bc>/ → tests en tests/ → reporte en docs/reports/
```

Esta cadena vive en `docs/traceability/matrix.md` y es navegable directamente en el wiki — cada US tiene su propia página con el ciclo completo.

**Recorrido de referencia:**
[[RF-ejecucion]] → [[US-X.Y.Z]] → código en `src/<bc>/` → tests en `tests/features/`

---

### 7. ¿Qué BC implementa cada área de requerimientos?

| Área RF | BC principal | BC secundario |
|---------|-------------|--------------|
| Gestión del torneo | [[arquitectura/bc-torneo]] | [[arquitectura/competencia]] |
| Inscripción de atletas | [[arquitectura/registro]] | — |
| Preparación | [[arquitectura/competencia]] | [[arquitectura/registro]] |
| Ejecución | [[arquitectura/competencia]] | — |
| Resultados | [[arquitectura/resultados]] | [[arquitectura/competencia]] |
| Usuarios y roles | [[arquitectura/identidad]] | — |
| Notificaciones | [[arquitectura/notificaciones]] | — |
| Integración externa | [[RF-integracion]] | (sin BC asignado aún) |

---

## Trazabilidad RF → Software Item → Test Unit

> Cadena completa disponible desde 2026-05-24. Todos los BCs poblados: Competencia · Registro · Torneo · Resultados · Identidad · Notificaciones.

### Cadena completa RF → código → test

```dataview
TABLE us_id, rf, software_items, test_units
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us" AND rf != null AND length(rf) > 0
SORT rf ASC, us_id ASC
```

### Distribución por origen — radiografía de trazabilidad

```dataview
TABLE WITHOUT ID
  origen_tipo AS "Origen",
  length(rows) AS "US",
  map(rows, (r) => r.us_id) AS "Ejemplos"
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
GROUP BY origen_tipo
```

### Cobertura de RFs

```dataview
TABLE us_refs, length(us_refs) AS "US count"
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-rf"
SORT length(us_refs) DESC
```

### Gaps de origen (US cerradas sin origen_tipo)

```dataview
TABLE us_id, bc, sp
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND origen_tipo = null
SORT bc ASC
```

### Gaps de trazabilidad — US cerradas sin Software Item

```dataview
TABLE us_id, bc, sp, origen_tipo
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND software_items = null
SORT bc ASC
```

### Gaps de trazabilidad — US cerradas sin Test Unit

```dataview
TABLE us_id, bc, sp, origen_tipo
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND test_units = null
SORT bc ASC
```

---

## Vistas dinámicas

### US por estado

```dataview
TABLE us_id, bc, sp, tests_count
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
SORT sp ASC, us_id ASC
GROUP BY estado
```

### US pendientes

```dataview
TABLE us_id, bc, sp, inc
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us" AND estado = "pendiente"
SORT sp ASC
```

### US por BC

```dataview
TABLE WITHOUT ID
  bc AS "BC",
  length(rows) AS "Total US",
  length(filter(rows, (r) => r.estado = "cerrada")) AS "Cerradas"
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
GROUP BY bc
SORT bc ASC
```

### US con cobertura de tests registrada

```dataview
TABLE us_id, bc, sp, tests_count
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us" AND tests_count != null
SORT tests_count DESC
```

### Cobertura por BC (arquitectura)

```dataview
TABLE tipo_ddd, test_coverage
FROM "wiki/arquitectura"
WHERE tipo_ddd != null
SORT test_coverage ASC
```

---

## Páginas de RF semilla disponibles

| Página | Área |
|--------|------|
| [[RF-gestion-torneo]] | Gestión del torneo — sin pendientes |
| [[RF-inscripcion-atletas]] | Inscripción de atletas — 1 pendiente |
| [[RF-preparacion]] | Preparación de competencias — sin pendientes |
| [[RF-ejecucion]] | Ejecución de competencias — 1 pendiente |
| [[RF-resultados]] | Premiación y resultados — 1 pendiente |
| [[RF-usuarios-roles]] | Usuarios, roles y permisos — sin pendientes |
| [[RF-notificaciones]] | Notificaciones — 1 pendiente |
| [[RF-integracion]] | Integración externa — toda el área pendiente |

---

## Páginas hub de esta vista

| Página | Por qué es hub |
|--------|----------------|
| [[RF-ejecucion]] | Área más compleja; concentra reglas de negocio del Core Domain |
| [[arquitectura/competencia]] | Implementa la mayoría de los RFs de ejecución y preparación |
| [[arquitectura/context-map]] | Muestra qué BC implementa qué área |
| `docs/traceability/matrix.md` | Fuente primaria original — cadena RF→US→SI→TU ahora en el wiki (177 US) |
