# Wiki Index — AtaraxiaDive

> Catálogo de todas las páginas del wiki.
> El LLM actualiza este archivo en cada operación de ingest.
> Leer este archivo primero al responder cualquier consulta.

**Última actualización:** 2026-05-22
**Total de páginas:** 236

---

## Estado del wiki

| Sección | Páginas | Estado |
|---------|---------|--------|
| Bounded Contexts | 7 / 7 | ✅ Ingest completo + métricas de salud BL-006 (ArchitectAnalyst + DesignReviewer) |
| Decisiones (ADRs) | 22 / 22 | ✅ Ingest completo |
| Trazabilidad (US) | 185 | ✅ SP1–SP7 + SP-ADJ-01 a SP-ADJ-11 completos; SP7 INC-7.1 + INC-7.2 documentados |
| Trazabilidad (RF semilla) | 8 | 🔄 Ingest parcial (fuente 3/7) |
| Investigación | 5 | ✅ Ingest completo (HITOs + experimento) |
| Conceptos de dominio | 16 | ✅ 9 originales + 7 nuevos (L6 lint-001 resuelto) |
| Impacto | 4 | ✅ 4 páginas de análisis (L5 lint-001 resuelto) |
| Estado del proyecto | 1 | ✅ Fase 3 completa — síntesis BL-000..BL-006 + SP7 en curso |
| Salud / lint | 2 | ✅ calidad-BL-006 + lint-001 ejecutado (Fase 4 completa) |
| Vistas | 6 / 6 | ✅ Fase 2 completa — 6 vistas operativas |

---

## Bounded Contexts

| Página | Tipo DDD | Persistencia | Responsabilidad |
|--------|----------|-------------|-----------------|
| [[competencia]] | Core Domain | Event Sourcing | Grilla, performances, tarjetas, trazabilidad deportiva |
| [[bc-torneo]] | Supporting | CRUD | Ciclo de vida del torneo, sede, entidad organizadora |
| [[registro]] | Supporting | CRUD | Atletas, inscripciones, validación de participación |
| [[resultados]] | Supporting | CRUD + stream | Rankings derivados, overall, exportación |
| [[identidad]] | Generic | CRUD | Usuarios, roles, JWT — cross-cutting |
| [[notificaciones]] | Generic | Event Sourcing | Ciclo de vida de notificaciones, exactly-once delivery |
| [[context-map]] | — | — | Integraciones y patrones entre los 6 BCs |

## Decisiones

| Página | Fecha | Estado | BCs afectados |
|--------|-------|--------|---------------|
| [[ADR-001-event-sourcing-competencia]] | 2026-02-10 | Aceptada | competencia |
| [[ADR-002-fastapi-backend]] | 2026-02-12 | Aceptada | todos |
| [[ADR-003-offline-first-pwa]] | 2026-02-15 | Aceptada | — |
| [[ADR-004-reglas-como-datos]] | 2026-02-20 | Aceptada | torneo, competencia |
| [[ADR-005-bounded-contexts-ddd-estrategico]] | 2026-02-24 | Aceptada | todos |
| [[ADR-006-estructura-bc-first]] | 2026-02-27 | Aceptada | todos |
| [[ADR-007-sqlite-persistencia-bc]] | 2026-03-01 | Aceptada | todos |
| [[ADR-008-event-store-sqlite]] | 2026-03-05 | Aceptada | competencia, notificaciones |
| [[ADR-009-migraciones-por-bc]] | 2026-03-10 | Aceptada | todos |
| [[ADR-010-docker-cloud-run]] | 2026-03-12 | **Supersedida** por ADR-021 | — |
| [[ADR-011-structlog-logging]] | 2026-03-15 | Aceptada | todos |
| [[ADR-012-rfc7807-errores-http]] | 2026-03-20 | Aceptada | todos |
| [[ADR-013-exception-management]] | 2026-03-26 | Aceptada | todos |
| [[ADR-014-penalizaciones-acumulables]] | 2026-04-08 | Aceptada | competencia, resultados |
| [[ADR-015-dexie-indexeddb-frontend]] | 2026-04-13 | Aceptada | — |
| [[ADR-016-resend-email-provider]] | 2026-04-16 | Aceptada | notificaciones |
| [[ADR-017-notificaciones-event-sourcing]] | 2026-04-16 | Aceptada | notificaciones |
| [[ADR-018-hash-sha256-auditoria]] | 2026-04-16 | Aceptada | competencia |
| [[ADR-019-politica-contrasenas]] | 2026-04-24 | Aceptada | identidad |
| [[ADR-020-modelo-usuarios-roles]] | 2026-05-16 | Aceptada | identidad, registro |
| [[ADR-021-fly-io]] | 2026-05-17 | Aceptada | todos |
| [[ADR-022-categoria-shared]] | 2026-05-02 | Aceptada | registro, competencia, resultados |

## Trazabilidad

### Semilla de requerimientos funcionales (por área)

| Página | Área | Pendientes |
|--------|------|-----------|
| [[RF-gestion-torneo]] | Gestión del torneo | 0 |
| [[RF-inscripcion-atletas]] | Inscripción de atletas | 1 (RF-IN-07) |
| [[RF-preparacion]] | Preparación de competencias | 0 |
| [[RF-ejecucion]] | Ejecución de competencias | 1 (RF-EJ-04 códigos de penalización) |
| [[RF-resultados]] | Premiación y resultados | 1 (RF-PM-01 sistema de puntos) |
| [[RF-usuarios-roles]] | Usuarios, roles y permisos | 0 |
| [[RF-notificaciones]] | Notificaciones | 1 (RF-NT-03) |
| [[RF-integracion]] | Integración con sistemas externos | 4 (toda el área pendiente) |

### Trazabilidad por US

#### SP1 (INC-1.1 a INC-1.4)

[[US-1.1.1]] · [[US-1.2.1]] [[US-1.2.2]] [[US-1.2.3]] [[US-1.2.4]] [[US-1.2.5]] [[US-1.2.6]] · [[US-1.3.1]] · [[US-1.4.1]] [[US-1.4.2]]

#### SP-ADJ-01

[[US-ADJ-1.1]] [[US-ADJ-1.2]] [[US-ADJ-1.3]] [[US-ADJ-1.4]] [[US-ADJ-1.5]]

#### SP-ADJ-02

[[US-ADJ-2.6]] [[US-ADJ-2.7]] [[US-ADJ-2.8]]

#### SP2 (INC-2.0 a INC-2.4)

[[US-2.0]] · [[US-2.1.1]] [[US-2.1.2]] [[US-2.1.3]] [[US-2.1.4]] · [[US-2.2.1]] [[US-2.2.2]] · [[US-2.3.1]] · [[US-2.4.1]] [[US-2.4.2]]

#### SP-ADJ-03

[[US-ADJ-3.1]] [[US-ADJ-3.2]] [[US-ADJ-3.3]] [[US-ADJ-3.4]] [[US-ADJ-3.5]] [[US-ADJ-3.6]] [[US-ADJ-3.7]] [[US-ADJ-3.8]]

#### SP-ADJ-04

[[US-ADJ-4.1]] [[US-ADJ-4.2]] [[US-ADJ-4.3]] [[US-ADJ-4.4]] [[US-ADJ-4.5]] [[US-ADJ-4.6]]

#### SP3 (INC-3.1 a INC-3.5)

[[US-3.1.1]] [[US-3.1.2]] · [[US-3.2.1]] [[US-3.2.2]] [[US-3.2.3]] · [[US-3.3.1]] [[US-3.3.2]] · [[US-3.4.1]] [[US-3.4.2]] · [[US-3.5.1]] [[US-3.5.2]] [[US-3.5.3]]

#### SP4 (INC-4.1 a INC-4.6)

[[US-4.1.1]] [[US-4.1.2]] [[US-4.1.3]] [[US-4.1.4]] [[US-4.1.5]] [[US-4.1.6]] [[US-4.1.7]] [[US-4.1.8]] · [[US-4.2.1]] [[US-4.2.2]] · [[US-4.3.1]] [[US-4.3.2]] [[US-4.3.3]] [[US-4.3.4]] [[US-4.3.5]] · [[US-4.4.1]] [[US-4.4.2]] [[US-4.4.3]] · [[US-4.5.1]] [[US-4.5.2]] [[US-4.5.3]] [[US-4.5.4]] [[US-4.5.5]] · [[US-4.6.1]] [[US-4.6.2]] [[US-4.6.3]] [[US-4.6.4]]

#### SP-ADJ-05

[[US-ADJ-5.1]] [[US-ADJ-5.2]] [[US-ADJ-5.3]] [[US-ADJ-5.4]] [[US-ADJ-5.5]]

#### SP-ADJ-06

[[US-ADJ-6.1]] [[US-ADJ-6.2]] [[US-ADJ-6.3]] [[US-ADJ-6.4]] [[US-ADJ-6.5]] [[US-ADJ-6.6]] [[US-ADJ-6.7]]

#### SP-ADJ-07

[[US-ADJ-7.1]] [[US-ADJ-7.2]] [[US-ADJ-7.3]]

#### SP5 — Panel Organizador (INC-5.1)

[[US-5.1.1]] [[US-5.1.2]] [[US-5.1.3]] [[US-5.1.4]] [[US-5.1.5]] [[US-5.1.6]]

#### SP5 — INC-5.1-ADJ (ajuste post-UAT)

[[US-5.1.7]] [[US-5.1.8]] [[US-5.1.9]] [[US-5.1.10]]

#### SP5 — Ejecución por Disciplina (INC-5.2)

[[US-5.2.1]] [[US-5.2.2]]

#### SP-ADJ-08

[[US-ADJ-8.1]] [[US-ADJ-8.2]] [[US-ADJ-8.3]]

#### SP5 — Gestión de Usuarios (INC-5.3)

[[US-5.3.1]] [[US-5.3.2]]

#### SP5 — Identidad Extendida (INC-5.4)

[[US-5.4.1]] [[US-5.4.2]] [[US-5.4.3]]

#### SP5 — Portal Atleta e Inscripción con AP (INC-5.5)

[[US-5.5.1]] [[US-5.5.2]]

#### SP5 — Algoritmo de Puntaje y Rankings (INC-5.6)

[[US-5.6.1]] [[US-5.6.2]] [[US-5.6.3]] [[US-5.6.4]] [[US-5.6.5]] [[US-5.6.6]]

#### SP-ADJ-09

[[US-ADJ-9.1]] [[US-ADJ-9.2]] [[US-ADJ-9.3]] [[US-ADJ-9.4]] [[US-ADJ-9.5]] [[US-ADJ-9.6]] [[US-ADJ-9.7]]

#### SP5 — Portal del Atleta (INC-5.7)

[[US-5.7.1]] [[US-5.7.2]] [[US-5.7.3]] [[US-5.7.4]]

#### SP6 — Ajustes Juez (INC-6.1)

[[US-6.1.1]] [[US-6.1.2]] [[US-6.1.3]] [[US-6.1.4]] [[US-6.1.5]]

#### SP6 — Ajustes Organizador (INC-6.2)

[[US-6.2.1]] [[US-6.2.2]] [[US-6.2.3]] [[US-6.2.4]] [[US-6.2.5]] [[US-6.2.6]]

#### SP6 — Ajustes Atleta (INC-6.3)

[[US-6.3.1]] [[US-6.3.2]]

#### SP6 — Deuda Técnica Sistema (INC-6.4)

[[US-6.4.1]] [[US-6.4.2]] [[US-6.4.3]] [[US-6.4.4]] [[US-6.4.5]] [[US-6.4.6]]

#### SP6 — API Pública (INC-6.6)

[[US-6.6.1]] [[US-6.6.2]] [[US-6.6.3]] [[US-6.6.4]]

#### SP-ADJ-10 — Edición de torneo post-cierre

[[US-ADJ-10.1]] [[US-ADJ-10.2]] [[US-ADJ-10.3]] [[US-ADJ-10.4]]

#### SP-ADJ-11 — Modelo de usuarios con múltiples roles

[[US-ADJ-11.1]] [[US-ADJ-11.2]] [[US-ADJ-11.3]] [[US-ADJ-11.4]] [[US-ADJ-11.5]] [[US-ADJ-11.6]] [[US-ADJ-11.7]] [[US-ADJ-11.8]] [[US-ADJ-11.9]] [[US-ADJ-11.10]]

#### SP7 — Despliegue (INC-7.1 + INC-7.2)

[[US-7.1.1]] [[US-7.1.2]] · [[US-7.2.1]] [[US-7.2.2]] [[US-7.2.3]]

## Conceptos de dominio

| Página | Descripción |
|--------|-------------|
| [[torneo]] | Evento competitivo central; ciclo de vida y etapas |
| [[disciplina]] | Modalidad de prueba (tiempo o distancia) |
| [[grilla]] | Planilla de salida por disciplina |
| [[performance]] | Actuación de un atleta en una disciplina |
| [[tarjeta]] | Resultado de validez de una performance (blanca/roja) |
| [[anuncio]] | Marca previa declarada por el atleta en Preparación |
| [[atleta]] | Participante del torneo; datos de identidad deportiva |
| [[roles]] | Organizador, Juez, Atleta, Administrador |
| [[atributos-calidad]] | Drivers no funcionales: rendimiento, disponibilidad, usabilidad, confiabilidad, etc. |
| [[inscripcion]] | Aggregate de participación de un atleta en un torneo; estados ACTIVA/CANCELADA |
| [[categoria]] | StrEnum compartido (shared/); clasifica atletas; importado por Registro, Competencia y Resultados |
| [[penalizacion]] | Infracción técnica que reduce RP sin descalificar; introduce BlancaConPenalizaciones |
| [[ranking]] | Ordenamiento de performances; dos tipos: por competencia y overall; separación cálculo/lectura |
| [[dns]] | Did Not Start; evento de atleta no presentado; aparece al final del ranking sin posición |
| [[sede]] | Value object de Torneo; ubicación física del evento (nombre, ciudad, país) |
| [[entidad-organizadora]] | Value object de Torneo; organismo institucional responsable; distinto del rol Organizador |

## Impacto

| Página | Componente | Riesgo |
|--------|-----------|--------|
| [[event-store-port]] | EventStorePort — contrato append-only; 2 BCs Event Sourcing | Muy alto |
| [[atleta-nombre-port]] | AtletaNombrePort / registro.db cross-BC — lectura directa desde Competencia y Resultados | Medio |
| [[categoria-shared]] | Categoria StrEnum — ADR-022 pendiente; imports cross-BC desde Resultados | Medio |
| [[bc-identidad]] | BC Identidad JWT — 3 BCs Conformist; cambio de claims impacta todos | Muy alto |

## Guía de uso

| Página | Descripción |
|--------|-------------|
| [[guia-uso]] | Cómo interactuar con el wiki: consultas, vistas, ingest, lint, triggers y componentes de alto riesgo |

## Estado del proyecto

| Página | Descripción |
|--------|-------------|
| [[proyecto]] | Estado unificado del proyecto — síntesis BL-000..BL-006, SP activo, US cerradas |

## Investigación

| Página | Descripción |
|--------|-------------|
| [[iedd-marco-conceptual]] | Modelo de 5 capas IEDD; tesis central; rol de DDD y la IA |
| [[iedd-hipotesis-experimento]] | Hipótesis del ensayo; tabla completa de 22 hipótesis confirmadas; tesis provisional |
| [[uat-metodologia]] | Política de UAT controlado; proceso por fase; vibe coding; datos reales como oráculo |
| [[hitos-catalog]] | Catálogo de 32 HITOs; evidencia empírica del experimento; agrupados por SP y tema |
| [[experimento-plan]] | Plan del experimento; 3 horizontes; jerarquía SP→Incremento→US; capitalización de conocimiento |

## Salud

| Página | Descripción |
|--------|-------------|
| [[calidad-BL-006]] | Snapshot de calidad al cierre de SP6 — 3 gates: DesignReviewer, ArchitectAnalyst, UAT |

## Vistas

| Página | Propósito |
|--------|-----------|
| [[dominio]] | El sistema visto desde el negocio y el lenguaje ubicuo |
| [[decisiones]] | El sistema visto desde su historia de razonamiento técnico |
| [[trazabilidad]] | El sistema visto desde los requerimientos hacia la implementación |
| [[impacto]] | El sistema visto desde las dependencias y el riesgo de cambio |
| [[salud]] | El sistema visto desde la deuda técnica y la calidad |
| [[investigacion]] | El sistema visto como fuente de conocimiento intelectual |
