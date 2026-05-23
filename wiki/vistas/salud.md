---
title: "Vista de Salud"
type: vista
last_updated: "2026-05-21"
sources:
  - wiki/salud/
  - docs/contexto/HITO-14-ANALISIS-METODOLOGIA-Y-ESTRUCTURA.md
  - wiki/conceptos/atributos-calidad.md
---

# Vista de Salud

> El sistema visto desde la deuda técnica, la calidad y la consistencia entre lo que el proyecto dice ser y lo que realmente es.

## Propósito

Responder preguntas sobre el estado de salud del proyecto: cobertura de tests, deuda técnica, inconsistencias documentales y gaps de trazabilidad. Convierte el diagnóstico disperso en múltiples documentos en una narrativa coherente y actualizada.

Resuelve directamente los problemas identificados en HITO-14:
- **D-02:** múltiples fuentes de verdad para el estado del proyecto
- **D-03:** documentación fundacional desalineada con la arquitectura vigente

## Stakeholder principal

Tech lead, responsable de calidad, Victor evaluando el experimento.

---

## Estado actual del wiki

> ⚠️ **Fase 4 pendiente.** No hay resultados de lint todavía. Las páginas en `wiki/salud/` están vacías.
>
> Lo que existe: los problemas conocidos (catalogados en HITO-14) y los atributos de calidad
> elicitados ([[atributos-calidad]]), que proveen los umbrales de referencia para el diagnóstico.

---

## Problemas conocidos pre-lint (desde HITO-14)

Estos problemas serán los primeros hallazgos del lint cuando se ejecute la Fase 4:

| ID | Problema | Severidad |
|----|----------|-----------|
| D-02 | Múltiples fuentes de verdad para el estado del proyecto (README, CLAUDE.md, docs/plans, docs/reports, .cm/baselines, matrix.md) | Muy alto |
| D-03 | Documentos de `docs/dominio/` mencionan PostgreSQL como tecnología vigente (reemplazado por SQLite en [[ADR-007-sqlite-persistencia-bc]]) | Muy alto |
| D-05 | Regla hexagonal no cumplida estrictamente en todo el código | Alto |
| D-06 | Imports directos entre BCs en algunos módulos | Alto |
| D-09 | Documentos históricos redactados como si siguieran vigentes | Medio |

---

## Preguntas características y recorridos

### 1. ¿Qué documentos están desalineados con la arquitectura vigente?

La desalineación más conocida (D-03): documentos de `docs/dominio/` anteriores a ADR-007 mencionan PostgreSQL. La jerarquía de fuentes de verdad establece que `docs/adr/` prevalece sobre `docs/dominio/`.

**Recorrido:**
[[ADR-007-sqlite-persistencia-bc]] → buscar "PostgreSQL" en `docs/dominio/` → verificar encabezado de documento histórico

**Acción esperada del lint:** detectar páginas del wiki que mencionen PostgreSQL como tecnología vigente y marcarlas para revisión.

---

### 2. ¿Hay ADRs con estado contradictorio entre sí?

El caso confirmado: [[ADR-010-docker-cloud-run]] fue supersedido por [[ADR-021-fly-io]]. Las páginas del wiki reflejan el estado vigente, pero otras partes del repositorio pueden seguir referenciando Cloud Run.

**Recorrido:**
[[ADR-010-docker-cloud-run]] → verificar que su estado diga "Supersedida" → [[ADR-021-fly-io]]

---

### 3. ¿Qué BCs no tienen cobertura de tests registrada?

Esta información vive en los quality gate reports (CodeGuard, DesignReviewer, ArchitectAnalyst) que se ingestarán en Fase 3. Hasta entonces, la referencia es `docs/traceability/matrix.md`.

**Recorrido (disponible en Fase 3):**
[[arquitectura/competencia]] → campo `test_coverage` → quality reports de `quality/reports/`

**Recorrido actual:**
[[arquitectura/competencia]] → sección "ADRs" → verificar si hay US registradas en matrix.md

---

### 4. ¿Hay conceptos del lenguaje ubicuo usados en el código sin página en el wiki?

Las 9 páginas de conceptos existentes cubren los términos principales. Los términos potencialmente no documentados se detectarán en el lint revisando nombres de clases y funciones en `src/`.

**Conceptos documentados:** [[performance]], [[grilla]], [[tarjeta]], [[anuncio]], [[disciplina]], [[atleta]], [[torneo]], [[roles]], [[atributos-calidad]]

**Recorrido del lint:** leer nombres de aggregates y value objects en `src/competencia/domain/` → contrastar con `wiki/conceptos/` → listar ausentes

---

### 5. ¿Cuál es la tendencia de calidad entre baselines?

Los baselines del proyecto (.cm/baselines/BL-*.md) registran el estado de calidad al cierre de cada Sprint. Se ingestarán en Fase 3 para poblar la página de estado del proyecto.

**Indicadores que el lint verificará:**
- Cobertura de tests por BC (¿sube o baja entre BLs?)
- Métricas de CodeGuard: CBO, WMC por clase
- Deuda técnica documentada vs. resuelta
- US cerradas por SP

**Recorrido (disponible en Fase 3):**
[[estado/proyecto]] → historial de baselines → métricas por BC → tendencia

---

### 6. ¿Hay páginas del wiki huérfanas (sin enlaces entrantes)?

El grafo de wikilinks puede tener páginas que nadie referencia. Estas son candidatas a páginas de baja utilidad o a gaps en el grafo de conocimiento.

**Recorrido del lint:** leer todos los [[wikilinks]] del wiki → construir grafo de enlaces → detectar nodos sin aristas entrantes

---

### 7. ¿Los atributos de calidad elicitados se están cumpliendo?

Los atributos de calidad son los umbrales de referencia del sistema. Ver [[atributos-calidad]] para la tabla completa.

**Umbrales clave a verificar:**
| Atributo | Umbral | ADR derivado |
|----------|--------|-------------|
| Latencia juez | ≤ 500 ms | — |
| Interfaz offline del juez | Funcional sin conexión | [[ADR-003-offline-first-pwa]] |
| Pérdida de performance | Inaceptable (cero) | [[ADR-001-event-sourcing-competencia]] |
| Auditoría inalterable | Requerida | [[ADR-018-hash-sha256-auditoria]] |
| Reglas sin cambio de código | Requerido | [[ADR-004-reglas-como-datos]] |

---

## Instrucción para el primer lint (Fase 4)

Cuando se ejecute `/wiki-lint`, el resultado debe ir a `wiki/salud/lint-001.md` con:

1. Páginas que mencionan PostgreSQL como tecnología vigente
2. ADRs con estado contradictorio entre sí o con la arquitectura actual
3. Requerimientos sin página US en el wiki (pendiente Fase 3)
4. BCs sin cobertura de tests registrada
5. Páginas con dependencias inferidas que requieren validación humana
6. Conceptos del dominio usados en el código sin página en `wiki/conceptos/`
7. Páginas huérfanas (sin ningún wikilink entrante)
8. Sugerencias de nuevas fuentes a ingestar para llenar gaps detectados

---

## Páginas hub de esta vista

| Página | Por qué es hub |
|--------|----------------|
| `wiki/salud/lint-001.md` | Primera radiografía del wiki (disponible en Fase 4) |
| [[atributos-calidad]] | Umbrales de referencia para evaluar el cumplimiento |
| [[arquitectura/context-map]] | Mapa de integraciones — útil para detectar imports ilegales |
| [[ADR-007-sqlite-persistencia-bc]] | Referencia para detectar D-03 (documentos con PostgreSQL) |
