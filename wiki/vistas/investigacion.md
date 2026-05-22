---
title: "Vista de Investigación"
type: vista
last_updated: "2026-05-21"
sources:
  - wiki/investigacion/
  - docs/contexto/PLAN-EXPERIMENTO.md
  - docs/contexto/HITO-*.md
---

# Vista de Investigación

> El sistema visto como fuente de conocimiento para productos intelectuales de largo plazo.

## Propósito

Mapear los aprendizajes del experimento a los productos intelectuales que los capitalizan: libro DDD, curso de Ingeniería de Software, paper IEDD, material de gestión. Es la vista que transforma el wiki de herramienta de desarrollo en herramienta de producción intelectual.

Esta vista no tiene equivalente en la literatura de arquitectura. Es la dimensión diferenciadora del proyecto AtaraxiaDive.

## Stakeholder principal

Victor como investigador y autor.

---

## Estado del experimento (mayo 2026)

| Horizonte | SPs | Estado |
|-----------|-----|--------|
| H1 — Validar | SP1 + SP2 | ✅ Completado — BL-002 generada |
| H2 — Construir | SP3 + SP4 | ✅ Completado — BL-004 generada |
| H3 — Producir | SP5 + SP6 + capitalización | 🔄 En progreso — SP6 activo |

**32 HITOs** documentados. Fuente: `[[hitos-catalog]]`.

---

## Preguntas características y recorridos

### 1. ¿Qué evidencia empírica tiene la metodología IEDD para el paper?

IEDD es el marco metodológico experimental del proyecto. Su tesis central: la IA no sustituye al ingeniero — desplaza el cuello de botella hacia la especificación y el juicio de diseño.

**Hipótesis confirmadas con más peso para el paper:**
- HITO-4: overhead del ecosistema IEDD convergió a ~18 min estable (US-1.2.1: 2h → US-1.2.3: 18min)
- HITO-8: compresión de contexto del LLM produce artefactos faltantes silenciosos
- HITO-12: instrucciones en lenguaje natural no son barreras efectivas para LLMs
- HITO-13: SP-ADJ como etapa formal del ciclo es necesario (deuda técnica post-SP)
- HITO-15: proyecciones CQRS emergen del Event Sourcing como consecuencia estructural inevitable
- HITO-16: secuencialidad prescriptiva de `/implement-us` es parte del método, no preferencia operativa

**Recorrido:**
`[[iedd-hipotesis-experimento]]` → `[[hitos-catalog]]` → `[[iedd-marco-conceptual]]` → `[[experimento-plan]]`

---

### 2. ¿Qué aprendimos sobre Event Sourcing que pueda ir al libro DDD?

El aggregate `Performance` bajo Event Sourcing en el Core Domain produjo evidencia práctica de alta calidad para el libro.

**Aprendizajes con evidencia empírica:**
- Las correcciones del juez como eventos adicionales (no mutaciones) — caso concreto de invariante de aggregate
- Las proyecciones CQRS emergen inevitablemente del ES (HITO-15)
- Event Sourcing para auditoría regulatoria: hash SHA-256 sobre secuencia inmutable ([[ADR-018-hash-sha256-auditoria]])
- Solo dos BCs usan ES — la decisión de cuándo NO usar ES tiene tanto valor como cuándo sí

**Recorrido:**
`[[iedd-hipotesis-experimento]]` → `[[arquitectura/competencia]]` → `[[ADR-001-event-sourcing-competencia]]` → `[[ADR-008-event-store-sqlite]]`

**Destino:** Libro DDD — caps. "Aggregates con invariantes reales" + "Domain Events como memoria del dominio"

---

### 3. ¿Qué casos del proyecto sirven para el curso de Ingeniería de Software?

AtaraxiaDive es un caso de estudio excepcionalmente bueno: dominio de primera mano, lógica no trivial, atributos de calidad medibles y modelo de desarrollo alineado.

| Caso práctico | Tema del curso | Páginas wiki |
|--------------|---------------|-------------|
| Performance aggregate + invariantes | Semana 4 — Aggregates y DDD | `[[arquitectura/competencia]]` + `[[performance]]` |
| Event Sourcing para auditoría | Semana 8 — Eventos de dominio | `[[ADR-001-event-sourcing-competencia]]` |
| Máquina de estados del Torneo | Semana 6 — State machines como UL | `[[arquitectura/bc-torneo]]` + `[[torneo]]` |
| Reglas como datos (disciplinas) | Semana 10 — Configurabilidad | `[[ADR-004-reglas-como-datos]]` |
| Pattern UAT híbrido sin POST | Semana 12 — Testing de dominio | `[[uat-metodologia]]` |

**Recorrido:**
`[[experimento-plan]]` sección "Capitalización" → caso específico → páginas correspondientes

---

### 4. ¿Qué aprendimos sobre la fricción de consistencia documental?

HITO-14 es el hallazgo metodológico más relevante sobre el costo de las fuentes de verdad múltiples.

**Hallazgos:**
- D-02: el estado del proyecto aparece en README, CLAUDE.md, docs/plans, docs/reports, .cm/baselines, matrix.md y specs individuales → onboarding confuso, análisis incorrecto de agentes
- D-03: documentos de `docs/dominio/` siguen mencionando PostgreSQL (reemplazado en [[ADR-007-sqlite-persistencia-bc]]) → contaminación de contexto LLM
- El LLM Wiki es la respuesta directa: una fuente sintetizada y mantenida reemplaza la dispersión

**Recorrido:**
`[[hitos-catalog]]` fila HITO-14 → `[[vistas/salud]]` (D-02/D-03) → `[[ADR-007-sqlite-persistencia-bc]]`

**Destino:** Paper IEDD — sección sobre fricción documental y memoria explícita como prerrequisito del desarrollo con IA

---

### 5. ¿Qué aprendizajes del experimento son generalizables a otros proyectos DDD?

Los HITOs más generalizables (confirmados, no específicos del dominio de apnea):

| HITO | Aprendizaje generalizable |
|------|--------------------------|
| HITO-4/5 | Overhead de ecosistema IEDD converge a ~18 min tras el primer ciclo completo |
| HITO-8 | Compresión de contexto LLM produce artefactos faltantes sin advertencia — se necesita verificación sistemática |
| HITO-9 | Patrón UAT híbrido (pytest + HTTP con seed) resuelve DoD cuando no hay endpoints POST |
| HITO-10 | Puerto de dominio resuelve dependencias inter-aggregate sin romper pureza hexagonal |
| HITO-11 | Quality gate automatizado puede derivar en decisión de diseño no anticipada — las métricas como catalizador arquitectónico |
| HITO-13 | Deuda técnica post-SP merece sub-sprint formal (SP-ADJ) en lugar de backlog indefinido |
| HITO-15 | Proyecciones CQRS emergen del ES como consecuencia estructural, no como diseño adicional |

**Recorrido:**
`[[hitos-catalog]]` → HITOs marcados ✅ → `[[iedd-marco-conceptual]]` → `[[iedd-hipotesis-experimento]]`

---

### 6. ¿Cuál es el estado de validación de las hipótesis del experimento?

Ver `[[iedd-hipotesis-experimento]]` para la tabla completa de 22 hipótesis con estado de confirmación.

**Tesis provisional (mayo 2026):** la IA no sustituye al ingeniero — desplaza el cuello de botella hacia la especificación y el juicio de diseño. Cuanto mayor la automatización de la implementación, mayor la necesidad de intervención humana en dominio, especificación, evaluación de trade-offs y formalización del conocimiento.

**Recorrido:**
`[[iedd-hipotesis-experimento]]` → tabla de 22 hipótesis → `[[hitos-catalog]]` para evidencia empírica de cada una

---

### 7. ¿Cómo fluye el conocimiento del proyecto hacia productos intelectuales?

El flujo de capitalización evita reescritura. Los ADRs, retrospectivas y reportes de `/implement-us` son materia prima directa.

```
Hallazgo en desarrollo (US, HITO, ADR)
  ↓
Formalización en wiki (investigacion/ + decisiones/)
  ↓
Selección por producto intelectual
  ↓
Libro DDD / Curso IS / Paper IEDD / Material de gestión
```

**Estado actual de subproyectos:**

| SP | Baseline | Foco | HITOs |
|----|---------|------|-------|
| SP1 — La Performance | BL-001 | Primer aggregate, ES, walking skeleton | HITO 3–9 |
| SP2 — La Competencia | BL-002 | Core domain, quality gates, SP-ADJ | HITO 10–13 |
| SP3 — El Torneo | BL-003 | Supporting domains, CQRS emergente | HITO 14–16 |
| SP4 — La Plataforma | BL-004 | Offline, auditoría, notificaciones, datos reales | HITO 17–25 |
| SP5 — La Puesta en Marcha | BL-005 | Multi-rol, seguridad, despliegue | HITO 26–29 |
| SP6 — Validación y Despliegue | BL-006 (en curso) | Deriva de tests, wiki, producción | HITO 30–32 |

**Recorrido:**
`[[experimento-plan]]` → sección "Subproyectos y Baselines" → `[[hitos-catalog]]` por SP

---

## Páginas hub de esta vista

| Página | Por qué es hub |
|--------|----------------|
| `[[iedd-hipotesis-experimento]]` | 22 hipótesis con estado de confirmación — material central del paper |
| `[[hitos-catalog]]` | 32 HITOs: evidencia empírica agrupada por SP y tema |
| `[[experimento-plan]]` | Estructura del experimento, 3 horizontes, tabla de capitalización |
| `[[iedd-marco-conceptual]]` | Marco teórico de 5 capas — referencia para el paper |
| `[[uat-metodologia]]` | Patrón UAT híbrido — caso generalizable documentado |
