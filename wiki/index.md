# Wiki Index — AtaraxiaDive

> Catálogo de todas las páginas del wiki.
> El LLM actualiza este archivo en cada operación de ingest.
> Leer este archivo primero al responder cualquier consulta.

**Última actualización:** 2026-05-20
**Total de páginas:** 51

---

## Estado del wiki

| Sección | Páginas | Estado |
|---------|---------|--------|
| Bounded Contexts | 7 / 7 | ✅ Ingest completo (6 BCs + context map) |
| Decisiones (ADRs) | 22 / 22 | ✅ Ingest completo |
| Trazabilidad (US) | 0 | ⏳ Pendiente ingest de estado (Fase 3) |
| Trazabilidad (RF semilla) | 8 | 🔄 Ingest parcial (fuente 3/7) |
| Investigación | 3 | 🔄 Ingest parcial (fuente 4/7) |
| Conceptos de dominio | 9 | 🔄 Ingest parcial (fuente 1/6 + enriquecimiento) |
| Impacto | 0 | ⏳ Pendiente construcción de vistas |
| Estado del proyecto | 0 | ⏳ Pendiente ingest de estado |
| Salud / lint | 0 | ⏳ Pendiente primer lint |
| Vistas | 6 / 6 | ✅ Inicializadas |

---

## Bounded Contexts

| Página | Tipo DDD | Persistencia | Responsabilidad |
|--------|----------|-------------|-----------------|
| [[competencia]] | Core Domain | Event Sourcing | Grilla, performances, tarjetas, trazabilidad deportiva |
| [[torneo]] | Supporting | CRUD | Ciclo de vida del torneo, sede, entidad organizadora |
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

*Vacío — pendiente Fase 3 (ingest de estado)*

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

## Impacto

*Vacío — pendiente Fase 2 (construcción de vistas)*

## Estado del proyecto

*Vacío — pendiente Fase 3 (ingest de estado)*

## Investigación

| Página | Descripción |
|--------|-------------|
| [[iedd-marco-conceptual]] | Modelo de 5 capas IEDD; tesis central; rol de DDD y la IA |
| [[iedd-hipotesis-experimento]] | Hipótesis del ensayo; tabla completa de 22 hipótesis confirmadas; tesis provisional |
| [[uat-metodologia]] | Política de UAT controlado; proceso por fase; vibe coding; datos reales como oráculo |
| [[hitos-catalog]] | Catálogo de 32 HITOs; evidencia empírica del experimento; agrupados por SP y tema |
| [[experimento-plan]] | Plan del experimento; 3 horizontes; jerarquía SP→Incremento→US; capitalización de conocimiento |

## Salud

*Vacío — pendiente Fase 4 (primer lint)*

## Vistas

| Página | Propósito |
|--------|-----------|
| [[dominio]] | El sistema visto desde el negocio y el lenguaje ubicuo |
| [[decisiones]] | El sistema visto desde su historia de razonamiento técnico |
| [[trazabilidad]] | El sistema visto desde los requerimientos hacia la implementación |
| [[impacto]] | El sistema visto desde las dependencias y el riesgo de cambio |
| [[salud]] | El sistema visto desde la deuda técnica y la calidad |
| [[investigacion]] | El sistema visto como fuente de conocimiento intelectual |
