---
title: "Catálogo de HITOs — Aprendizajes del experimento IEDD"
type: investigacion
last_updated: "2026-05-20"
sources:
  - docs/contexto/INDICE-HITOS.md
  - docs/contexto/HITO-*.md
---

# Catálogo de HITOs — Aprendizajes del experimento IEDD

Los HITOs documentan aprendizajes experimentales significativos producidos durante el desarrollo de AtaraxiaDive. Son el material primario del paper IEDD. 32 HITOs registrados a mayo 2026.

## Por SP — Distribución y foco

| SP | HITOs | Foco principal |
|----|:-----:|----------------|
| Fase 0 / Pre-SP1 | 1, 2 | Validación metodológica inicial, consistencia del stack |
| SP1 — La Performance | 3–9 | Primer ciclo IEDD completo, fricción del ecosistema, BDD + ES |
| SP2 — La Competencia | 10–13 | Patrones DDD avanzados, quality gates, deuda técnica formal |
| SP3 — El Torneo | 14–16 | Proyecciones CQRS emergentes, secuencialidad del pipeline |
| SP4 — La Plataforma | 17–25 | Datos reales como oráculo, validación UX, integridad criptográfica, exportación portable |
| SP5 — La Puesta en Marcha | 26–29 | Cobertura asimétrica Event Storming, deriva documental, anti-patrones de validación |
| SP6 — Validación y Despliegue | 30–32 | Deriva silenciosa de tests en proyectos IEDD+LLM |

---

## Tabla completa

| HITO | SP | Título | Pregunta central | Estado |
|------|----|--------|-----------------|--------|
| HITO-1 | Fase 0 | Adherencia IEDD — Fase 0 | ¿Los invariantes del Process Modeling producen US-IEDD con menos edge cases? | 🔄 En evaluación |
| HITO-2 | Pre-SP1 | Stack técnico y consistencia documental | ¿ADR-007..012 son coherentes entre sí y con la arquitectura? | ✅ Confirmada |
| HITO-3 | SP1 | Walking Skeleton | ¿El scaffold BC-first + Event Store SQLite funciona como base real? | ✅ Confirmada |
| HITO-4 | SP1 | Primer ciclo completo de /implement-us | ¿El ecosistema IEDD + Dev Kit es operativo desde la primera US? | ✅ H-4.1 confirmada: overhead ~18 min estable |
| HITO-5 | SP1 | Convergencia del overhead | ¿El overhead se estabiliza tras el primer ciclo? | ✅ Confirmada — US-1.2.1: 2h → US-1.2.2: 9min → US-1.2.3: 18min |
| HITO-6 | SP1 | Fricción BDD × Event Sourcing | ¿BDD y ES se integran naturalmente o generan fricción de expresividad? | 🔄 En evaluación |
| HITO-7 | SP1 | Fiabilidad AI en protocolos + métricas DDD | ¿El LLM ejecuta protocolos estructurados de forma fiable? ¿CBO/WMC capturan calidad DDD? | 🔄 En evaluación |
| HITO-8 | SP1 | Artefactos faltantes por compresión de contexto | ¿La compresión de contexto del LLM degrada silenciosamente la completitud? | ✅ Confirmada — patrón documentado |
| HITO-9 | SP1 | UAT híbrido sin endpoints de escritura | ¿Es posible evidenciar el DoD cuando no hay HTTP POST? | ✅ Confirmada — patrón UAT híbrido (pytest + HTTP) |
| HITO-10 | SP2 | PerformancesAPPort — dominio puro con datos de otro aggregate | ¿Un puerto de dominio resuelve la dependencia inter-aggregate sin romper pureza? | ✅ Confirmada |
| HITO-11 | SP2 | Quality gate como catalizador de decisión arquitectónica | ¿Una métrica automatizada puede derivar en una decisión de diseño no anticipada? | ✅ Confirmada |
| HITO-12 | SP2 | Gates de texto vs constraints de herramienta | ¿Las instrucciones en lenguaje natural son barreras reales para LLMs? | ✅ Confirmada — no son barreras efectivas |
| HITO-13 | SP2 | SP-ADJ como etapa formal del ciclo IEDD | ¿La deuda técnica post-SP merece un sub-sprint formal en lugar de backlog? | ✅ Confirmada |
| HITO-14 | SP3 | Análisis crítico de la metodología | ¿Qué partes del sistema metodológico muestran valor claro y cuáles generan fricción? | ✅ D-02 y D-03 identificadas (fuentes de verdad múltiples, docs desalineados) |
| HITO-15 | SP3 | Proyecciones CQRS emergen del Event Sourcing | ¿El ES produce proyecciones CQRS como consecuencia estructural inevitable? | ✅ Confirmada |
| HITO-16 | SP3 | Secuencialidad prescriptiva del pipeline | ¿La linealidad de /implement-us es preferencia operativa o parte del método? | ✅ Confirmada — es parte del método |
| HITO-17 | Post-SP3 | Datos reales como oráculo del dominio | ¿Los datos de competencia real revelan inconsistencias que los tests formales no detectan? | ✅ Confirmada — dataset BA 2025 como oráculo |
| HITO-18 | SP4 | Prototipo navegable como etapa de validación | ¿El prototipo navegable es necesario entre especificación e implementación con frontend? | ✅ Confirmada en SP4 |
| HITO-19 | SP4 | Incremento como unidad de captura de deuda de diseño | ¿El incremento es la unidad correcta para agrupar hallazgos estructurales? | ✅ Confirmada |
| HITO-20 | SP4 | Invariantes correctos pero incompletos frente a variantes del dominio | ¿El UAT end-to-end es el único oráculo que detecta invariantes correctos pero incompletos? | ✅ Confirmada |
| HITO-21 | SP4 | Tracker secuencial como política | ¿La secuencialidad del método incluye también al tracker que registra sus fases? | ✅ Confirmada |
| HITO-22 | SP4 | Event Sourcing como base de integridad criptográfica | ¿La misma traza puede sostener auditoría e integridad verificable sin persistencia adicional? | ✅ Confirmada (ver [[ADR-018-hash-sha256-auditoria]]) |
| HITO-23 | SP4 | Auditoría UI como composición de read models | ¿La evidencia del ES se vuelve útil cuando puede recorrerse desde la UI? | ✅ Confirmada |
| HITO-24 | SP4 | Exportación como read model transversal portable | ¿La evidencia puede salir como artefacto portable sin persistencia paralela? | ✅ Confirmada |
| HITO-25 | SP4 | Restricción técnica como driver de abstracción | ¿El offline-first produce mejor arquitectura que si hubiera sido opcional? | ✅ Confirmada (ver [[ADR-003-offline-first-pwa]]) |
| HITO-26 | SP5 | Cobertura asimétrica del Event Storming | ¿Qué áreas quedan subrepresentadas si el Event Storming se hace solo para un BC? | ✅ Evidencia identificada |
| HITO-27 | SP5 | Deriva Documental y Gates de Consistencia | ¿Cómo se detecta la derivación cuando especificación e implementación compiten? | ✅ Patrón documentado |
| HITO-28 | SP5 | UAT: Vibe Coding vs Pipeline Formal | ¿El testing exploratorio ad-hoc captura invariantes que el pipeline formal no ve? | ✅ Evidencia inicial (complementariedad) |
| HITO-29 | SP5 | Spec-validatoria: anti-patrón de especificar desde código | ¿Escribir specs después del código genera sesgos invisibles en la cobertura? | ✅ Anti-patrón identificado |
| HITO-30 | SP6 | Deriva silenciosa de tests unitarios | ¿Qué tipos de deriva acumula un proyecto IEDD+LLM cuando los tests no se ejecutan en cada PR? | ✅ Evidencia documentada |
| HITO-31 | SP6 | Deriva de tests de integración | ¿Qué patrones de falla son exclusivos del nivel de integración en proyectos IEDD+LLM? | ✅ Evidencia documentada |
| HITO-32 | SP6 | Deriva de tests BDD | ¿Los tests BDD son el nivel con mayor deriva semántica en proyectos IEDD+LLM? | ✅ Evidencia documentada |

---

## Agrupación por tema

### Ecosistema y tooling

HITO-4, HITO-5 — overhead convergente (~18 min estable).
HITO-7, HITO-12 — fiabilidad del LLM en protocolos; gates de texto no son barreras efectivas.
HITO-8 — compresión de contexto degrada silenciosamente la completitud de artefactos.
HITO-16, HITO-21 — la secuencialidad del método incluye al pipeline y al tracker.

### DDD y Event Sourcing

HITO-3 — Walking Skeleton BC-first + Event Store funciona como base real.
HITO-6 — fricción BDD × ES documentada.
HITO-10 — puerto de dominio resuelve dependencia inter-aggregate.
HITO-15 — proyecciones CQRS emergen inevitablemente del ES.
HITO-22, HITO-23, HITO-24 — ES como base de integridad criptográfica, auditoría navegable y exportación portable.

### Calidad y deuda técnica

HITO-11 — quality gate como catalizador de decisión arquitectónica.
HITO-13 — SP-ADJ como etapa formal del ciclo IEDD.
HITO-14 — diagnóstico metodológico: D-02 (fuentes de verdad múltiples), D-03 (docs desalineados).
HITO-19 — el incremento como unidad de captura de deuda estructural.
HITO-27 — deriva documental y gates de consistencia.
HITO-30, HITO-31, HITO-32 — deriva silenciosa de tests en proyectos IEDD+LLM.

### Validación y datos de dominio

HITO-9 — UAT híbrido sin endpoints de escritura.
HITO-17 — datos reales como oráculo del dominio (dataset BA 2025).
HITO-18 — prototipo navegable como etapa de validación con frontend.
HITO-20 — invariantes correctos pero incompletos frente a variantes del dominio.
HITO-28 — vibe coding complementa al pipeline formal.
HITO-29 — anti-patrón: spec-validatoria escrita después del código.

### Arquitectura emergente

HITO-25 — restricción técnica (offline-first) como driver de mejor diseño.
HITO-26 — cobertura asimétrica del Event Storming.

---

## Páginas relacionadas

- [[iedd-marco-conceptual]] — el modelo de 5 capas que estos HITOs validan
- [[iedd-hipotesis-experimento]] — hipótesis centrales del experimento y su estado
- [[uat-metodologia]] — metodología UAT (HITO-9, HITO-17, HITO-20, HITO-28 son evidencia)
