---
title: "Lint-001 — Primera auditoría del wiki"
type: salud
last_updated: "2026-05-22"
sources:
  - wiki/ (todas las páginas)
  - src/ (estructura de archivos compilados)
  - docs/traceability/matrix.md
---

# Lint-001 — Primera auditoría del wiki

> Ejecutado: 2026-05-22 — Fase 4 del POC LLM Wiki
> Páginas auditadas: 232 (sin contar index.md y log.md)

---

## Resumen ejecutivo

| Categoría | Severidad | Hallazgos |
|-----------|-----------|-----------|
| L1 — PostgreSQL como tecnología vigente | 🟢 OK | 0 instancias problemáticas |
| L2 — ADRs con estado contradictorio | 🟢 OK | ADR-010 correctamente supersedida |
| L3 — RFs sin páginas US | 🟡 GAP | 8 RFs sin US asociada |
| L4 — BCs sin cobertura de tests registrada | 🟡 GAP MENOR | 4 BCs con cobertura en prosa, sin métricas numéricas |
| L5 — Páginas de impacto con dependencias sin validar | 🔴 GAP CRÍTICO | wiki/impacto/ vacío — 0 páginas |
| L6 — Conceptos del dominio en código sin página wiki | 🟡 GAP | 7 conceptos sin página propia |
| L7 — Páginas huérfanas (sin enlace entrante desde index) | 🟡 GAP | 14 páginas no enlazadas desde index.md |
| L8 — Inconsistencias estructurales del wiki | 🔴 GAP CRÍTICO | 2 inconsistencias de naming / estado de index |

---

## L1 — PostgreSQL como tecnología vigente

**Resultado: LIMPIO** ✅

Todas las menciones de PostgreSQL en el wiki están en contexto correcto:
- `wiki/decisiones/ADR-007-sqlite-persistencia-bc.md` — pregunta histórica respondida (fue el origen de ADR-007)
- `wiki/decisiones/ADR-021-fly-io.md` — contraste con alternativa descartada
- `wiki/vistas/decisiones.md` — pregunta característica "¿Por qué SQLite y no PostgreSQL?"
- `wiki/vistas/salud.md` — nota meta sobre qué detectar en futuros lints
- `wiki/trazabilidad/us/US-ADJ-5.2.md` — referencia histórica contextualizada
- `wiki/LLM-WIKI-DIAGNOSTICO-Y-PLAN.md` — documento del plan (meta)

**Ninguna página presenta PostgreSQL como tecnología activa del proyecto.**

---

## L2 — ADRs con estado contradictorio

**Resultado: LIMPIO** ✅

- **ADR-010 (Docker + Cloud Run)**: correctamente marcada como "⚠️ SUPERSEDIDA" con enlace a [[ADR-021-fly-io]].
- **ADR-021 (Fly.io)**: referencia a ADR-010 en contexto histórico correcto.
- No se detectaron ADRs que se contradigan mutuamente sin documentación.

**Nota:** `wiki/trazabilidad/us/US-7.1.1.md` referencia ADR-010 — verificar que lo haga en contexto histórico.

---

## L3 — RFs sin páginas US

**Resultado: 8 RFs pendientes** 🟡

Los siguientes requerimientos funcionales no tienen US implementada documentada en el wiki:

| RF | Área | Estado |
|----|------|--------|
| RF-IN-07 | Inscripción de atletas | Pendiente de implementación |
| RF-EJ-04 | Ejecución — códigos de penalización | Pendiente de implementación |
| RF-PM-01 | Premiación — sistema de puntos | Pendiente de implementación |
| RF-NT-03 | Notificaciones | Pendiente de implementación |
| RF-IG-01 | Integración — BD externa FAAS (¿formato?) | Indefinido desde elicitación |
| RF-IG-02 | Integración — modo consulta (lectura/escritura) | Indefinido |
| RF-IG-03 | Integración — comportamiento offline | Indefinido |
| RF-IG-04 | Integración — exportación AIDA/CMAS | Indefinido |

Los RF-IG-* son un caso especial: están indefinidos desde la elicitación inicial y no son backlog formal. Ver [[RF-integracion]] para el contexto completo.

**Acción sugerida:** Crear backlog item para RF-IN-07, RF-EJ-04, RF-PM-01, RF-NT-03 si se planea SP8.

---

## L4 — BCs sin cobertura de tests registrada

**Resultado: GAP MENOR** 🟡

Todos los BCs tienen una sección `### Cobertura` en sus páginas. Sin embargo, la calidad varía:

| BC | Cobertura documentada |
|----|-----------------------|
| [[competencia]] | ✅ Numérica: "≥ 90% (BL-001..BL-006)" + BDD features referenciadas |
| [[registro]] | ✅ Numérica: "≥ 90% domain/ + application/" |
| [[resultados]] | ✅ Cualitativa con dato concreto: "91 tests en US-5.6.4" |
| [[bc-torneo]] | 🟡 Solo prosa: "estable sin cambios desde BL-003" |
| [[identidad]] | 🟡 Solo prosa: "BC genérico con pocos cambios" |
| [[notificaciones]] | 🟡 Solo prosa: "política exactly-once verificada" |

**Acción sugerida:** En el próximo ingest de `quality/reports/`, actualizar torneo, identidad y notificaciones con porcentajes reales.

---

## L5 — Páginas de impacto con dependencias sin validar

**Resultado: GAP CRÍTICO** 🔴

`wiki/impacto/` contiene **0 páginas**. El index.md lo registra como "Vacío — pendiente Fase 2 (construcción de vistas)".

Esta es la vista de mayor valor para el objetivo central del POC: análisis de impacto para mantenimiento. Sin páginas de impacto, preguntas como "¿qué se rompe si cambio EventStorePort?" no tienen respuesta en el wiki.

**Candidatos prioritarios para wiki/impacto/:**

| Componente | Por qué es prioritario |
|------------|----------------------|
| `EventStorePort` | Implementado en competencia + notificaciones; contrato crítico |
| `AtletaRepositoryPort` | Cruzado por registro, competencia (ACL) y resultados |
| `CategoriaShared` | ADR-022 creó un shared kernel; cualquier cambio impacta 3 BCs |
| `BC Identidad` | Provee JWT/auth al resto de los BCs — dependencia transversal |

**Acción sugerida:** Crear al menos 4 páginas de impacto para los componentes de mayor acoplamiento. Ver [[vistas/impacto]] para guía de construcción.

---

## L6 — Conceptos del dominio en código sin página wiki

**Resultado: 7 conceptos identificados** 🟡

Páginas existentes en `wiki/conceptos/`: anuncio, atleta, atributos-calidad, disciplina, grilla, performance, roles, tarjeta, torneo (9 páginas).

Conceptos presentes en el código fuente (`src/`) sin página propia:

| Concepto | Dónde aparece | Por qué merece página |
|----------|---------------|-----------------------|
| `inscripcion` | `registro/domain/aggregates/inscripcion` | Aggregate central del BC Registro; gestiona ciclo de vida de inscripción, estados, cancelación |
| `categoria` | `shared/`, ADR-022 | Kernel compartido por 3 BCs (ADR-022); la única entidad cross-BC del sistema |
| `penalizacion` | `competencia/domain/` | Concepto con tipos (técnica, DQ), invariantes de acumulación (ADR-014) |
| `ranking` | `resultados/domain/` | Dos tipos: por competencia y overall; algoritmos FAAS/CMAS/AIDA diferenciados |
| `dns` (Did-Not-Start) | `competencia/domain/events/` | Evento crítico: atleta que no completa la performance; afecta ranking |
| `sede` | `torneo/domain/` | Entidad de dominio: localización del torneo; no cubierta en [[bc-torneo]] |
| `entidad_organizadora` | `torneo/domain/` | Organismo responsable del torneo; relacionado con tipo de reglamento |

**Nota:** El concepto `ap` (anuncio previo / announced performance) está parcialmente cubierto en [[anuncio]], pero el término técnico `ap_declarado` vs `ap_registrado` no está diferenciado.

**Acción sugerida (prioridad):** `inscripcion` y `categoria` son los más críticos para trazabilidad y análisis de impacto.

---

## L7 — Páginas huérfanas (sin enlace desde index.md)

**Resultado: 14 páginas sin registro en index** 🟡

Las siguientes páginas existen como archivos pero no tienen `[[wikilink]]` en `wiki/index.md`:

### Trazabilidad — INC-6.6 (SP6 API pública)
- `wiki/trazabilidad/us/US-6.6.1.md`
- `wiki/trazabilidad/us/US-6.6.2.md`
- `wiki/trazabilidad/us/US-6.6.3.md`
- `wiki/trazabilidad/us/US-6.6.4.md`

### Trazabilidad — SP-ADJ-10
- `wiki/trazabilidad/us/US-ADJ-10.1.md`
- `wiki/trazabilidad/us/US-ADJ-10.2.md`
- `wiki/trazabilidad/us/US-ADJ-10.3.md`
- `wiki/trazabilidad/us/US-ADJ-10.4.md`

### Trazabilidad — SP7 (parcialmente registrado)
El index menciona SP7 en su tabla de estado pero no tiene secciones con wikilinks:
- `wiki/trazabilidad/us/US-7.1.1.md`
- `wiki/trazabilidad/us/US-7.1.2.md`
- `wiki/trazabilidad/us/US-7.2.1.md`
- `wiki/trazabilidad/us/US-7.2.2.md`
- `wiki/trazabilidad/us/US-7.2.3.md`

### Estado del proyecto
- `wiki/estado/proyecto.md` — existe pero el index.md solo lo menciona en la tabla de estado (sin wikilink navegable)

**Acción sugerida:** Actualizar `wiki/index.md` para incluir todas las páginas huérfanas con sus wikilinks.

---

## L8 — Inconsistencias estructurales del wiki

**Resultado: 2 inconsistencias críticas** 🔴

### L8-A: Directorio de BCs difiere del plan y del index

El plan (`WIKI.md` y `LLM-WIKI-DIAGNOSTICO-Y-PLAN.md`) define las páginas de BC en:
```
wiki/bounded-contexts/<nombre-bc>.md
```

La estructura real es:
```
wiki/arquitectura/<nombre-bc>.md
```

El `index.md` referencia `[[competencia]]`, `[[torneo]]` etc. con wikilinks sin path, lo que genera **ambigüedad**: tanto `wiki/arquitectura/torneo.md` como `wiki/conceptos/torneo.md` tienen el mismo basename `torneo`. Un sistema de resolución de wikilinks que use basename tendría un conflicto de nombres.

**Acción sugerida:** Renombrar una de las dos páginas para eliminar la ambigüedad:
- Opción A: Renombrar `wiki/arquitectura/torneo.md` → `wiki/arquitectura/bc-torneo.md`
- Opción B: Ajustar el naming del index para diferenciar `[[bc-torneo]]` vs `[[concepto-torneo]]`

### L8-B: index.md tiene secciones desactualizadas

Las secciones "Impacto" y "Estado del proyecto" del index siguen mostrando mensajes de "pendiente" que ya no son correctos:

| Sección | Texto actual (incorrecto) | Estado real |
|---------|--------------------------|-------------|
| Impacto (línea ~205) | `*Vacío — pendiente Fase 2 (construcción de vistas)*` | La *vista* existe (`wiki/vistas/impacto.md`) pero las páginas de análisis siguen vacías |
| Estado del proyecto (línea ~209) | `*Vacío — pendiente Fase 3 (ingest de estado)*` | `wiki/estado/proyecto.md` existe y está completo |

**Acción sugerida:** Actualizar estas dos secciones del index para reflejar el estado real.

---

## Sugerencias de fuentes a ingestar (próximas)

| Fuente | Contenido potencial | Prioridad |
|--------|---------------------|-----------|
| `docs/contexto/APRENDIZAJES-IEDD.md` | Aprendizajes metodológicos del experimento; enriquece `wiki/investigacion/` | Alta |
| `quality/reports/` BL-001..BL-005 | Tendencia histórica de calidad; enriquece [[calidad-BL-006]] con contexto temporal | Media |
| `frontend/` (si existe) | Conceptos UX, flujos de pantallas; sin representación en wiki | Media |
| Graphify output sobre `src/` | Dependencias reales entre BCs; completaría `wiki/impacto/` con datos estructurales | Alta (post-POC) |
| Reports de SP7 al cierre | Completar páginas US-7.* y actualizar [[estado/proyecto]] | Alta (cuando disponible) |

---

## Acciones priorizadas

| Prioridad | Acción | Hallazgo origen |
|-----------|--------|-----------------|
| 1 | Crear `wiki/impacto/` con 4 páginas mínimas (EventStorePort, AtletaPort, CategoriaShared, BC-Identidad) | L5 |
| 2 | Actualizar `wiki/index.md`: agregar SP6-INC-6.6, SP-ADJ-10, SP7 y enlace a estado/proyecto | L7 |
| 3 | Resolver ambigüedad de naming `torneo` (arquitectura vs concepto) | L8-A |
| 4 | Crear páginas `wiki/conceptos/inscripcion.md` y `wiki/conceptos/categoria.md` | L6 |
| 5 | Ingestar `docs/contexto/APRENDIZAJES-IEDD.md` → `wiki/investigacion/` | L8 sugerencia |
| 6 | Actualizar secciones desactualizadas del index (Estado + Impacto) | L8-B |
| 7 | Enriquecer cobertura numérica de torneo, identidad, notificaciones | L4 |

---

*Lint ejecutado por Claude Sonnet 4.6 — Mayo 2026*
*Próximo lint sugerido: al cierre de SP7 o después de ingest de APRENDIZAJES-IEDD.md*
