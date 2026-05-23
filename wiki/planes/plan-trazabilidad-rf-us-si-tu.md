---
title: "Plan: Trazabilidad completa RF → US → Software Item → Test Unit"
type: plan
estado: pendiente
fecha: "2026-05-23"
fases: [A, B, C, D, E]
---

# Plan: Trazabilidad RF → US → Software Item → Test Unit

## Objetivo

Materializar en el wiki la cadena de trazabilidad de 4 niveles:

```
RF (requerimiento funcional)
  → US (historia de usuario)
    → Software Item (referencia al artefacto de código)
      → Test Unit (referencia al test que lo verifica)
```

**No se ingesta código.** Solo se agregan referencias (`path/al/archivo.py`,
`tests/features/US-X.Y.Z/...`) como campos de frontmatter. Dataview puede entonces
recorrer y filtrar la cadena completa desde cualquier nivel.

## Schema objetivo

### US (frontmatter extendido)

```yaml
# Campos nuevos a agregar a los 177 US existentes
rf: [RF-EJ-05, RF-EJ-06]
software_items:
  - src/competencia/application/handlers/registrar_resultado_handler.py
  - src/competencia/infrastructure/repositories/competencia_repository.py
test_units:
  - tests/features/US-1.2.3/registrar_resultado.feature
  - tests/integration/competencia/test_registrar_resultado.py
```

### RF pages (frontmatter extendido)

```yaml
# Campo nuevo a agregar a las 8 páginas RF
us_refs: [US-1.2.1, US-1.2.2, US-1.2.3]
```

### Queries Dataview que esto habilita

```dataview
// Cadena completa desde un RF
TABLE us_id, bc, software_items, test_units
FROM "wiki/trazabilidad"
WHERE contains(rf, "RF-EJ-05")
```

```dataview
// US sin Software Item asignado (gap de trazabilidad)
TABLE us_id, bc, sp
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us" AND software_items = null
SORT sp ASC
```

```dataview
// US sin Test Unit (riesgo de calidad)
TABLE us_id, bc, sp
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us" AND test_units = null AND estado = "cerrada"
```

---

## Fase A — Schema (1 sesión, ~15 min)

**Estado:** pendiente

Actualizar `WIKI.md` con los nuevos campos del tipo `trazabilidad-us` y del
tipo `trazabilidad-rf`.

Nada se pobla todavía — solo se declara el schema para que futuras sesiones
lo respeten.

---

## Fase B — Poblar `rf:` en las 177 US (1 sesión, ~20 min)

**Estado:** pendiente  
**Herramienta:** script Python (mismo patrón que el enriquecimiento de frontmatter anterior)

Los RF ya están en la narrativa de cada US en la sección `## RFs cubiertos`.
Un script extrae los patrones `RF-XX-NN` del cuerpo y los agrega al frontmatter.

**Lógica del script:**

```python
import re
rf_pattern = re.compile(r'\bRF-[A-Z]{2}-\d+\b')

# Para cada US-*.md:
# 1. Buscar en el body todos los RF-XX-NN
# 2. Deduplicar y ordenar
# 3. Agregar rf: [RF-XX-NN, ...] al frontmatter si no existe
```

**Casos especiales a revisar manualmente (~10–15 US):**
- US que dicen "Validado como parte de INC-X.X" sin sección RF explícita
- US-ADJ (ajustes técnicos): pueden no tener RF directo → `rf: []`
- US-2.0 y similares de setup: `rf: []`

---

## Fase C — Poblar `us_refs:` en las 8 páginas RF (1 sesión, ~15 min)

**Estado:** pendiente  
**Herramienta:** script Python (derivado de Fase B)

Una vez que todas las US tienen `rf:` en su frontmatter, se invierte la relación:
por cada RF, se agregan todas las US que lo referencian.

```python
# Para cada RF-*.md en wiki/trazabilidad/:
# 1. Buscar en todos los US-*.md donde rf contiene este RF
# 2. Agregar us_refs: [US-X.Y.Z, ...] al frontmatter de la página RF
```

Las 8 páginas RF están en `wiki/trazabilidad/RF-*.md`.

---

## Fase D — Poblar `software_items:` y `test_units:` (6 sesiones, ~30 min c/u)

**Estado:** pendiente  
**Herramienta:** Claude Code lee `src/<bc>/` y `tests/` → agrega campos a las US del BC

Una sesión por BC. Claude lee la estructura real del código y los tests, y para
cada US del BC determina:
- `software_items:` handler principal + repositorio/adapter si aplica
- `test_units:` feature file BDD + test de integración si existe

### Convenciones del proyecto que facilitan el mapeo

El proyecto sigue BC-first (ADR-006) con naming consistente:

| US título | Handler esperado |
|-----------|-----------------|
| RegistrarResultado | `registrar_resultado_handler.py` |
| CrearCompetencia | `crear_competencia_handler.py` |
| AnunciarMarca | `anunciar_marca_handler.py` |

Los BDD features siguen el patrón `tests/features/US-X.Y.Z/`.

### Sesiones

| Sesión | BC | US en ese BC | Estado |
|--------|----|-------------|--------|
| D1 | competencia | ~35 US | pendiente |
| D2 | registro | ~20 US | pendiente |
| D3 | bc-torneo | ~25 US | pendiente |
| D4 | resultados | ~20 US | pendiente |
| D5 | identidad | ~15 US | pendiente |
| D6 | notificaciones | ~15 US | pendiente |

### Instrucción estándar por sesión

```
Leé src/competencia/ y tests/ (structure + feature files).
Para cada US en wiki/trazabilidad/ donde bc = "competencia":
  - Determiná el/los software_items (paths relativos desde raíz del proyecto)
  - Determiná el/los test_units (paths relativos desde raíz del proyecto)
  - Agregá ambos campos al frontmatter de la US
  - Si no encontrás un software item claro, marcá software_items: null
  - Si no encontrás test, marcá test_units: null
No inventés paths. Solo referenciá archivos que existan en src/.
```

### US-ADJ

Los ajustes técnicos (US-ADJ-X.Y) no siguen el patrón handler/feature.
Para estas US:
- `software_items:` los archivos refactoreados (inferibles del título)
- `test_units:` null o el test de regresión más cercano

---

## Fase E — Vista de trazabilidad actualizada (1 sesión, ~20 min)

**Estado:** pendiente

Actualizar `wiki/vistas/trazabilidad.md` con las nuevas queries que aprovechan
la cadena completa RF→US→SI→TU.

### Queries nuevas a agregar

**Cadena completa RF → código → test**
```dataview
TABLE us_id, rf, software_items, test_units
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us" AND rf != null
SORT rf ASC, us_id ASC
```

**Gaps de trazabilidad (US cerradas sin Software Item)**
```dataview
TABLE us_id, bc, sp
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND software_items = null
SORT bc ASC
```

**Gaps de trazabilidad (US cerradas sin Test Unit)**
```dataview
TABLE us_id, bc, sp
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-us"
  AND estado = "cerrada"
  AND test_units = null
SORT bc ASC
```

**Cobertura de RFs**
```dataview
TABLE us_refs, length(us_refs) AS "US count"
FROM "wiki/trazabilidad"
WHERE type = "trazabilidad-rf"
SORT length(us_refs) DESC
```

---

## Resumen

| Fase | Herramienta | Entregable | Duración est. |
|------|-------------|------------|---------------|
| A — Schema | Edit WIKI.md | Tipos actualizados | 15 min |
| B — `rf:` en US | Script Python | 177 US con campo rf | 20 min |
| C — `us_refs:` en RF | Script Python | 8 RF pages actualizadas | 15 min |
| D — `software_items:` + `test_units:` | Claude lee src/ + tests/ | 177 US con referencias de código | 6×30 min |
| E — Vista actualizada | Edit vistas/trazabilidad.md | Queries de cadena completa | 20 min |

**Total estimado:** ~4 horas (dominado por Fase D).

## Valor al completar

Desde Obsidian se puede responder:
- *"¿Qué código implementa RF-EJ-05?"* → query directa
- *"¿Qué tests cubren US-3.3.1?"* → campo test_units
- *"¿Hay US cerradas sin test?"* → query de gap
- *"¿Cuántas US implementan cada RF?"* → query de cobertura RF
