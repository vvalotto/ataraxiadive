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
| HITO-14 | SP3 en curso | 2026-03-31 | Análisis crítico de la metodología y la estructura del proyecto | ¿Qué partes del sistema metodológico ya muestran valor claro y cuáles generan fricción o contradicción? | [HITO-14](./HITO-14-ANALISIS-METODOLOGIA-Y-ESTRUCTURA.md) |
| HITO-15 | SP3 Inc 3.3 | 2026-03-31 | Las proyecciones CQRS emergen naturalmente del Event Sourcing | ¿El Event Sourcing produce proyecciones CQRS como consecuencia estructural inevitable, no como elección? | [HITO-15](./HITO-15-CQRS-PROYECCIONES-EMERGEN-DE-ES.md) |
| HITO-16 | SP3 Inc 3.5 | 2026-04-02 | Secuencialidad prescriptiva del pipeline | ¿La linealidad de `/implement-us` es una preferencia operativa o parte del método? | [HITO-16](./HITO-16-SECUENCIALIDAD-PRESCRIPTIVA-PIPELINE.md) |
| HITO-17 | Post-SP3 | 2026-04-03 | Los datos reales actúan como oráculo empírico del dominio | ¿Los datos de una competencia real revelan inconsistencias del dominio que los tests formales no detectan? | [HITO-17](./HITO-17-DATOS-REALES-COMO-ORACULO-DEL-DOMINIO.md) |
| HITO-18 | SP4 Inc 4.0 | 2026-04-04 | El prototipo navegable como etapa de validación | ¿El prototipo navegable es una etapa necesaria entre especificación e implementación cuando hay frontend? | [HITO-18](./HITO-18-UX-PROTOTIPO-NAVEGABLE-COMO-ETAPA-VALIDACION.md) |
| HITO-19 | SP4 cierre INC-4.1 | 2026-04-08 | Cierre de incremento como captura formal de deuda de diseño | ¿El incremento es la unidad correcta para agrupar hallazgos estructurales y planificar ajustes? | [HITO-19](./HITO-19-INC-4-1-HALLAZGOS-DISENO-CIERRE.md) |
| HITO-20 | SP4 Inc 4.3 | 2026-04-12 | Invariantes de dominio que no aplican a todas las variantes | ¿El UAT end-to-end es el único oráculo que detecta invariantes correctos pero incompletos frente a variantes del dominio? | [HITO-20](./HITO-20-INVARIANTES-VARIANTES-DOMINIO-UAT.md) |
| HITO-21 | SP4 Inc 4.6 | 2026-04-16 | Tracker secuencial como política | ¿La secuencialidad del método incluye también al mecanismo que registra sus fases? | [HITO-21](./HITO-21-TRACKER-SECUENCIALIDAD-COMO-POLITICA.md) |
| HITO-22 | SP4 Inc 4.6 | 2026-04-16 | Event Sourcing como base de integridad criptográfica | ¿La misma traza de eventos puede sostener auditoría legible e integridad verificable sin persistencia adicional? | [HITO-22](./HITO-22-EVENT-SOURCING-INTEGRIDAD-CRIPTOGRAFICA.md) |
| HITO-23 | SP4 Inc 4.6 | 2026-04-16 | Auditoría UI como composición operable de read models | ¿La evidencia del Event Sourcing se vuelve útil recién cuando puede recorrerse desde la UI sin conocer el event store? | [HITO-23](./HITO-23-AUDITORIA-UI-COMPOSICION-QUERIES.md) |
| HITO-24 | SP4 Inc 4.6 | 2026-04-16 | Exportación como read model transversal portable | ¿La evidencia del dominio puede salir del sistema como artefacto portable sin persistencia paralela y sin romper bounded contexts? | [HITO-24](./HITO-24-EXPORTACION-COMO-READ-MODEL-TRANSVERSAL.md) |
| HITO-25 | SP4 cierre | 2026-04-16 | Restricción técnica como driver de abstracción | ¿La exigencia de offline-first produce mejor arquitectura que si hubiera sido opcional? | [HITO-25](./HITO-25-RESTRICCION-TECNICA-COMO-DRIVER-DE-ABSTRACCION.md) |
| HITO-26 | SP5 Inc 5.1 | 2026-04-22 | Cobertura asimétrica del Event Storming | ¿Qué áreas del dominio quedan subrepresentadas en el Event Storming si solo se hace para un BC? | [HITO-26](./HITO-26-COBERTURA-ASIMETRICA-EVENT-STORMING.md) |
| HITO-27 | SP5 Inc 5.2 | 2026-04-23 | Deriva Documental y Gates de Consistencia | ¿Cómo se detecta y controla la derivación documental cuando la especificación y la implementación compiten por autoridad? | [HITO-27](./HITO-27-DERIVA-DOCUMENTAL-GATES-CONSISTENCIA.md) |
| HITO-28 | SP5 Inc 5.2 | 2026-04-23 | UAT: Vibe Coding vs Pipeline Formal | ¿El testing exploratorio ad-hoc captura invariantes que el pipeline formal no ve? | [HITO-28](./HITO-28-UAT-VIBE-CODING-VS-PIPELINE-FORMAL.md) |
| HITO-29 | SP5 Inc 5.5 | 2026-04-26 | Spec-validatoria: anti-patrón de especificar desde código | ¿Escribir specs después de código listo genera sesgos invisibles en la cobertura de casos? | [HITO-29](./HITO-29-SPEC-VALIDATORIA-UX-ANTI-PATRON.md) |
| HITO-30 | SP6 apertura | 2026-05-08 | Deriva silenciosa de tests: invariantes, contratos y entorno | ¿Qué tipos de deriva silenciosa acumula un proyecto IEDD+LLM cuando los tests unitarios no se ejecutan en cada PR? | [HITO-30](./HITO-30-DERIVA-TESTS-UNITARIOS-INVARIANTES-DOMINIO.md) |
| HITO-31 | SP6 apertura | 2026-05-08 | Deriva de tests de integración: wiring, invariantes incorrectos y entorno | ¿Qué patrones de falla son exclusivos del nivel de integración frente a los unitarios en un proyecto IEDD+LLM? | [HITO-31](./HITO-31-DERIVA-TESTS-INTEGRACION-WIRING-ENTORNO.md) |

---

## Distribución por SP

| SP | HITOs | Foco principal |
|----|:-----:|----------------|
| Fase 0 / Pre-SP1 | 1, 2 | Validación metodológica inicial, consistencia del stack |
| SP1 (La Performance) | 3, 4, 5, 6, 7, 8, 9 | Primer ciclo IEDD completo, fricción del ecosistema, BDD + ES |
| SP2 (La Competencia) | 10, 11, 12, 13 | Patrones DDD avanzados, quality gates, deuda técnica formal |
| SP3 (El Torneo) | 14, 15, 16 | Proyecciones CQRS emergentes, secuencialidad del pipeline y gobierno del proceso |
| SP4 (La Plataforma) | 17, 18, 19, 20, 21, 22, 23, 24, 25 | Datos reales como oráculo, validación UX, captura formal de hallazgos estructurales, gobierno secuencial del tracker, integridad criptográfica, auditoría navegable por composición de read models, exportación portable, restricción técnica como driver de buen diseño |
| SP5 (La Puesta en Marcha) | 26, 27, 28, 29 | Cobertura asimétrica del event storming, deriva documental, validación con UAT exploratorio, anti-patrones de validación tardía |
| SP6 (Validación y Despliegue) | 30 | Deriva silenciosa de tests por evolución de invariantes de dominio |

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
| La secuencialidad del método incluye también al tracker y su evidencia | HITO-21 | ✅ Confirmada |
| El Event Sourcing puede sostener auditoría e integridad criptográfica con la misma traza | HITO-22 | ✅ Evidencia confirmada |
| La evidencia del Event Sourcing solo se vuelve operable cuando puede navegarse desde read models y UI | HITO-23 | ✅ Evidencia confirmada |
| La evidencia del dominio puede exportarse como read model portable sin persistencia paralela | HITO-24 | ✅ Evidencia confirmada |
| El incremento es la unidad correcta para leer deuda estructural acumulada | HITO-19 | ✅ Evidencia confirmada |
| La restricción técnica (offline-first) produce mejor arquitectura que decisión ad-hoc | HITO-25 | ✅ Evidencia confirmada |
| Las proyecciones CQRS emergen como consecuencia estructural del Event Sourcing | HITO-15 | ✅ Evidencia confirmada |
| Los datos reales de dominio detectan inconsistencias que los tests formales no ven | HITO-17 | ✅ Confirmada — dataset BA 2025 como oráculo |
| El prototipo navegable es una etapa necesaria cuando el proyecto incorpora frontend | HITO-18 | ✅ Evidencia confirmada en SP4 |
| Los invariantes correctos pueden ser incompletos frente a variantes no anticipadas del dominio | HITO-20 | ✅ Confirmada — UAT como único oráculo |
| Cobertura asimétrica del Event Storming genera especificaciones incompletas | HITO-26 | ✅ Evidencia identificada en SP5 |
| Especificar después de implementación introduce sesgos en cobertura | HITO-29 | ✅ Anti-patrón identificado |
| El testing exploratorio (vibe) complementa el pipeline formal | HITO-28 | ✅ Evidencia inicial |

---

*Creado: 2026-03-28 — SP-ADJ-02-doc*
*Mantenido por: Claude Cowork + Victor Valotto*
