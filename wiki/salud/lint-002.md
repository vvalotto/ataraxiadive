---
title: "Lint-002 — Auditoría post-cierre (verificación de la ingesta BL-007)"
type: salud
last_updated: "2026-05-30"
sources:
  - wiki/ (todas las páginas)
  - wiki/index.md
  - wiki/log.md
---

# Lint-002 — Auditoría post-cierre (verificación de la ingesta BL-007)

> Ejecutado: 2026-05-30 — motivado por la ingesta de `.cm/baselines/BL-007.md` (ver entrada
> `[2026-05-30] ingest` en [[log]]). Objetivo declarado: verificar que la ingesta no rompió
> nada. Alcance real: la auditoría completa de `wiki/index.md` expuso un problema más grave
> y anterior, que ninguna ingesta previa había detectado.
> Páginas en disco al momento del lint: 362 archivos `.md` en `wiki/` (incluye `index.md` y `log.md`).

---

## Resumen ejecutivo

| Categoría | Severidad | Hallazgos |
|-----------|-----------|-----------|
| M1 — Consistencia de la ingesta BL-007 | 🟢 OK | 0 referencias residuales a BL-006/v1.0.0 como vigente o a SP7 como pendiente, fuera del log histórico |
| M2 — Wikilinks de Trazabilidad (US) en `index.md` | 🔴 GAP CRÍTICO | 177 / 177 enlaces rotos (100%) — bug sistémico, no introducido por la ingesta de hoy |
| M3 — Categoría de páginas no documentada (RNF) | 🟡 GAP | 8 páginas en `wiki/trazabilidad/rnf/` sin declarar en `WIKI.md` ni en `index.md` |
| M4 — Conteo de páginas desincronizado | 🟡 GAP MENOR | El encabezado de `index.md` no coincide con la suma de su propia tabla, ni con el conteo real en disco |
| M5 — Re-verificación de gaps de lint-001 | mixto | L5 y L8-A resueltos; L8-B resuelto por esta ingesta; L7 cambió de forma sin resolverse (ver detalle) |
| M6 — Trazabilidad fina de SP-ADJ-12/13 | 🟡 GAP (heredado) | Sin páginas de US individuales — declarado en el propio log del 30/05 |

---

## M1 — Consistencia de la ingesta BL-007

**Resultado: LIMPIO** ✅

Se buscó en todo `wiki/` cualquier mención de "BL-006" o "v1.0.0" presentados como vigentes,
y cualquier mención de "SP7" como activo/pendiente o "fly deploy" como pendiente. Las únicas
coincidencias están en `wiki/log.md`, correctamente contextualizadas como historia (la entrada
del 21/05 describe el estado *de ese momento*; la entrada del 30/05 describe la transición).
Ninguna página viva del wiki contradice hoy el cierre real del proyecto.

---

## M2 — Wikilinks de Trazabilidad (US) rotos en `index.md`

**Resultado: GAP CRÍTICO** 🔴 — el hallazgo más importante de este lint.

La sección "## Trazabilidad de Historias de Usuario" de `index.md` enumera wikilinks para las
185 US del proyecto, agrupados por SP. Se verificaron los 177 wikilinks `[[US-...]]` contra los
nombres de archivo reales en `wiki/trazabilidad/us/`: **ninguno resuelve.**

El patrón del bug es consistente en los 177 casos: el slug del título aparece **triplicado**
en el nombre del enlace. Ejemplo real (US-1.1.1, la primera US del proyecto — el bug está
presente desde el primer ingest, no es algo que haya aparecido con el tiempo):

```
Wikilink en index.md:
[[US-1.1.1-setup-esqueleto-bc-competencia-setup-esqueleto-bc-competencia-setup-esqueleto-bc-competencia]]

Archivo real:
wiki/trazabilidad/us/US-1.1.1-setup-esqueleto-bc-competencia.md
```

El mismo patrón se repite en los cinco enlaces que la ingesta de hoy tocó (US-7.1.1, US-7.1.2,
US-7.2.1, US-7.2.2, US-7.2.3) — confirmando que **no es un efecto de la ingesta BL-007**, sino
un defecto preexistente en el script o proceso que generó originalmente esta sección de
`index.md`, nunca detectado porque ningún lint anterior auditó `index.md` enlace por enlace.

**Consecuencia práctica:** cualquier consulta al wiki que dependa de navegar desde `index.md`
hacia una página de US específica falla en silencio — el LLM (o un humano en Obsidian) ve el
wikilink, pero no puede resolverlo. Las páginas de US en sí están bien; lo roto es exclusivamente
la tabla de navegación de `index.md`.

**Nota metodológica:** esto es, en sí mismo, un caso de honestidad del patrón — el problema no
se inventó ni se ocultó: apareció al correr la auditoría completa, y se reporta tal cual.

**Acción sugerida:** regenerar la sección de Trazabilidad (US) de `index.md`, usando el
nombre de archivo real (sin extensión) como target del wikilink, no un slug derivado del título.

---

## M3 — Categoría de páginas no documentada (RNF)

**Resultado: 8 páginas sin declarar** 🟡

`wiki/trazabilidad/rnf/` existe y contiene 8 páginas (ej. `RNF-01-confiabilidad-persistencia-event-sourcing.md`,
`RNF-02-disponibilidad-offline-first.md`, ...). Esta categoría de página:

- No aparece en la tabla "Tipos de páginas y ubicaciones" de `WIKI.md`.
- No tiene fila propia en la tabla "Estado del wiki" de `index.md`.
- Coincidentemente, la diferencia entre el conteo declarado de Trazabilidad (US) (185) y el
  conteo real en `wiki/trazabilidad/us/` (177) es exactamente 8 — compatible con la hipótesis
  de que estas 8 páginas fueron en algún momento reclasificadas de US a RNF sin actualizar el
  conteo de la tabla. No se confirmó esta hipótesis contra el historial de `log.md`; queda
  como pregunta abierta.

**Acción sugerida:** documentar `trazabilidad-rnf` como tipo de página en `WIKI.md` (mismo
tratamiento que `trazabilidad-rf`), y agregar la fila correspondiente en `index.md`.

---

## M4 — Conteo de páginas desincronizado

**Resultado: GAP MENOR** 🟡

Tres números que deberían coincidir, no coinciden:

| Fuente | Valor |
|--------|-------|
| Header `index.md` ("Total de páginas") | 305 |
| Suma de la tabla "Estado del wiki" (`index.md`) | ~354 |
| Archivos `.md` reales en `wiki/` (excluyendo `index.md`, `log.md`, `guia-uso.md`, `LLM-WIKI-DIAGNOSTICO-Y-PLAN.md`) | 358 |

El header no se ha reconciliado con su propia tabla desde hace varias ingestas — esta ingesta
heredó el mismo número (304→305) sin corregir la base. La tabla y el conteo real en disco son
razonablemente consistentes entre sí (diferencia ~4, probablemente páginas de contexto/context-map
no categorizadas); el header es el que quedó desalineado.

**Acción sugerida:** en la próxima ingesta que toque `index.md`, recalcular el header desde la
tabla real en lugar de incrementarlo a mano.

---

## M5 — Re-verificación de los gaps de lint-001

| Gap (lint-001) | Estado a 2026-05-30 |
|---|---|
| L3 — RFs sin US | No re-auditado en esta pasada — mantener como estaba |
| L4 — BCs sin cobertura numérica | No re-auditado en esta pasada — mantener como estaba |
| **L5 — `wiki/impacto/` vacío** | ✅ **Resuelto** — 4 páginas de análisis existen (EventStorePort, AtletaNombrePort, CategoriaShared, BC-Identidad), ingeridas el 23/05 |
| L6 — Conceptos sin página | No re-auditado en esta pasada — mantener como estaba |
| **L7 — Páginas huérfanas (sin enlace desde index)** | 🟡 **Cambió de forma, no se resolvió.** Las páginas que lint-001 marcó como huérfanas (SP6-INC-6.6, SP-ADJ-10, SP7) **ya aparecen** listadas en `index.md` — pero con los mismos wikilinks rotos que M2. Dejaron de estar ausentes; siguen sin ser navegables. |
| **L8-A — Ambigüedad de naming `torneo`** | ✅ **Resuelto** — `wiki/arquitectura/torneo.md` fue renombrado a `bc-torneo.md`; `wiki/conceptos/torneo.md` es ahora la única página con ese basename |
| **L8-B — Secciones desactualizadas del index** | ✅ **Resuelto por la ingesta BL-007** de hoy |

---

## M6 — Trazabilidad fina de SP-ADJ-12/13 (heredado del log de hoy)

Ya declarado en la entrada de ingesta del 30/05: las 6 US de SP-ADJ-12 y el addendum
SP-ADJ-13 no tienen páginas de trazabilidad-us propias — quedaron sintetizadas dentro de
`wiki/estado/proyecto.md` y `wiki/salud/calidad-BL-007.md`. No bloqueante; se deja como
gap conocido hasta que se decida si vale la pena esa granularidad.

---

## Acciones priorizadas

| Prioridad | Acción | Hallazgo origen |
|-----------|--------|-----------------|
| 1 | Regenerar los wikilinks de Trazabilidad (US) en `index.md` con el nombre de archivo real | M2 |
| 2 | Documentar `trazabilidad-rnf` en `WIKI.md` y agregarlo a la tabla de `index.md` | M3 |
| 3 | Reconciliar el header "Total de páginas" con el conteo real | M4 |
| 4 | Si se necesita, ingestar `docs/plans/sp-adj-12/` y `sp-adj-13/` para trazabilidad fina | M6 |
| 5 | Re-ejecutar L3, L4 y L6 de lint-001 en una próxima auditoría completa | M5 |

---

*Lint ejecutado por Claude (sesión Cowork) — 30 de mayo de 2026, a pedido de Victor Valotto,
como verificación posterior a la ingesta de BL-007.*
*Próximo lint sugerido: después de corregir M2, para confirmar que la regeneración de wikilinks
no introduce nuevos huecos.*
