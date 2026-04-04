# Índice de HITOs — AtaraxiaDive

Los HITOs documentan aprendizajes experimentales significativos del proyecto.
Son el material primario del paper IEDD y las retrospectivas de baseline.
Todos viven en `docs/contexto/HITO-N-*.md`.

---

## Tabla de HITOs

| ID | SP | Fecha | Título corto | Hipótesis / Pregunta central | Archivo |
|----|:--:|-------|--------------|------------------------------|---------|
| HITO-1 | Fase 0 | 2026-03-19 | Adherencia IEDD — Fase 0 | ¿Los invariantes del Process Modeling producen US-IEDD con menos edge cases? | [HITO-1](./HITO-1-ADHERENCIA-IEDD-FASE0.md) |
| HITO-2 | Pre-SP1 | 2026-03-20 | Stack técnico y consistencia documental | ¿ADR-007..012 son coherentes entre sí y con la arquitectura? | [HITO-2](./HITO-2-STACK-TECNICO-CONSISTENCIA.md) |
| HITO-3 | SP1 Inc 1.1 | 2026-03-21 | Walking Skeleton — primer contacto con el código | ¿El scaffold BC-first + Event Store SQLite funciona como base real? | [HITO-3](./HITO-3-INC-1-1-WALKING-SKELETON.md) |
| HITO-4 | SP1 Inc 1.2 | 2026-03-21 | Primer ciclo completo de /implement-us | ¿El ecosistema IEDD + Dev Kit es operativo desde la primera US? | [HITO-4](./HITO-4-US-1-2-1-PRIMER-CICLO-IMPLEMENT-US.md) |
| HITO-5 | SP1 Inc 1.2 | 2026-03-22 | Segundo ciclo — convergencia del overhead | ¿El overhead del ecosistema se estabiliza tras el primer ciclo? | [HITO-5](./HITO-5-US-1-2-2-SEGUNDO-CICLO-IMPLEMENT-US.md) |
| HITO-6 | SP1 Inc 1.2 | 2026-03-22 | Fricción BDD × Event Sourcing × invariantes DDD | ¿BDD y ES se integran naturalmente o generan fricción de expresividad? | [HITO-6](./HITO-6-US-1-2-4-BDD-EVENT-SOURCING.md) |
| HITO-7 | SP1 Inc 1.2 | 2026-03-23 | Fiabilidad AI en protocolos + métricas DDD | ¿El LLM ejecuta protocolos estructurados de forma fiable? ¿CBO/WMC capturan calidad DDD? | [HITO-7](./HITO-7-US-1-2-5-FIABILIDAD-AI-METRICAS-DDD.md) |
| HITO-8 | SP1 Inc 1.3 | 2026-03-23 | Artefactos faltantes por compresión de contexto | ¿La compresión de contexto del LLM degrada silenciosamente la completitud de los artefactos? | [HITO-8](./HITO-8-ARTEFACTOS-FALTANTES-COMPRESION-CONTEXTO.md) |
| HITO-9 | SP1 cierre | 2026-03-24 | UAT híbrido sin endpoints de escritura | ¿Es posible evidenciar el DoD de forma observable cuando no hay HTTP POST? | [HITO-9](./HITO-9-UAT-HIBRIDO-SIN-HTTP-COMMANDS.md) |
| HITO-10 | SP2 Inc 2.1 | 2026-03-25 | PerformancesAPPort — dominio puro con datos de otro aggregate | ¿Un puerto de dominio resuelve la dependencia de datos inter-aggregate sin romper pureza? | [HITO-10](./HITO-10-PERFORMANCES-AP-PORT-DOMINIO-PURO.md) |
| HITO-11 | SP2 pre-Inc 2.1 | 2026-03-26 | Quality gate como catalizador de decisión arquitectónica | ¿Una métrica automatizada puede derivar en una decisión de diseño no anticipada? | [HITO-11](./HITO-11-QUALITY-GATE-COMO-CATALIZADOR-COLABORATIVO.md) |
| HITO-12 | SP2 Inc 2.2 | 2026-03-26 | Gates de texto vs constraints de herramienta | ¿Las instrucciones procedurales en lenguaje natural son barreras reales para LLMs? | [HITO-12](./HITO-12-GATES-TEXTO-VS-HERRAMIENTA.md) |
| HITO-13 | SP2 cierre | 2026-03-28 | SP-ADJ como etapa formal del ciclo IEDD | ¿La deuda técnica post-SP merece un sub-sprint formal propio en lugar de backlog? | [HITO-13](./HITO-13-SP-ADJ-DEUDA-TECNICA-COMO-ETAPA-FORMAL.md) |
| HITO-16 | SP3 Inc 3.5 | 2026-04-02 | Secuencialidad prescriptiva del pipeline | ¿La linealidad de `/implement-us` es una preferencia operativa o parte del método? | [HITO-16](./HITO-16-SECUENCIALIDAD-PRESCRIPTIVA-PIPELINE.md) |

---

## Distribución por SP

| SP | HITOs | Foco principal |
|----|:-----:|----------------|
| Fase 0 / Pre-SP1 | 1, 2 | Validación metodológica inicial, consistencia del stack |
| SP1 (La Performance) | 3, 4, 5, 6, 7, 8, 9 | Primer ciclo IEDD completo, fricción del ecosistema, BDD + ES |
| SP2 (La Competencia) | 10, 11, 12, 13 | Patrones DDD avanzados, quality gates, deuda técnica formal |
| SP3 (El Torneo) | 15, 16 | Proyecciones CQRS emergentes, secuencialidad del pipeline y gobierno del proceso |

---

## Hipótesis del experimento respondidas

| Hipótesis | HITOs relevantes | Estado |
|-----------|-----------------|--------|
| H-4.1: overhead del ecosistema converge | HITO-4, HITO-5 | ✅ Confirmada — ~18 min estable |
| RQ1: fricción de coordinación entre herramientas | HITO-4..8, HITO-11 | 🔄 En evaluación |
| RQ2: IEDD mejora especificaciones | HITO-1, HITO-4, HITO-6 | 🔄 En evaluación |
| SP-ADJ como etapa necesaria | HITO-13 | ✅ Confirmada |
| Gates de texto no son barreras para LLMs | HITO-12 | ✅ Confirmada |
| La secuencialidad del pipeline es parte del método | HITO-16 | ✅ Confirmada |

---

*Creado: 2026-03-28 — SP-ADJ-02-doc*
*Mantenido por: Claude Cowork + Victor Valotto*
