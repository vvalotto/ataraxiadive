---
title: "Vista de Decisiones"
type: vista
last_updated: "2026-05-21"
sources:
  - wiki/decisiones/
  - wiki/arquitectura/
---

# Vista de Decisiones

> El sistema visto desde su historia de razonamiento técnico.

## Propósito

Exponer por qué el sistema fue construido de una manera particular: alternativas consideradas, trade-offs evaluados y estado vigente de cada decisión. Evita que el razonamiento arquitectónico se pierda y que futuras sesiones rehagan análisis ya realizados.

## Stakeholder principal

Arquitecto, desarrollador senior, quien va a tomar la próxima decisión técnica.

---

## Preguntas características y recorridos

### 1. ¿Por qué SQLite y no PostgreSQL?

El sistema opera con ~4 torneos/año, ~100 atletas, ~500 performances/torneo y pico de 50 usuarios concurrentes. La contención es mínima porque cada juez opera en su andarivel propio. SQLite en modo WAL cubre el caso con cero infraestructura de servidor.

**Recorrido:**
`[[ADR-007-sqlite-persistencia-bc]]` → `[[ADR-009-migraciones-por-bc]]` → `[[ADR-021-fly-io]]`

> La condición de escape está documentada en ADR-007: migrar a PostgreSQL si supera 200 escrituras simultáneas sostenidas, requiere full-text search avanzado, o necesita replicación multi-servidor.

---

### 2. ¿Por qué Event Sourcing solo en dos BCs y no en todos?

Event Sourcing se aplicó únicamente donde hay auditoría regulatoria o idempotencia crítica: Competencia (correcciones del juez ante la FAAS) y Notificaciones (exactly-once delivery). Los BCs de soporte usan CRUD porque no requieren historia de cambios.

**Recorrido:**
`[[ADR-001-event-sourcing-competencia]]` → `[[ADR-017-notificaciones-event-sourcing]]` → `[[ADR-008-event-store-sqlite]]` → `[[ADR-018-hash-sha256-auditoria]]`

> El hash SHA-256 al cerrar una disciplina es posible precisamente porque los eventos son inmutables y ordenados.

---

### 3. ¿Qué alternativas se descartaron para el frontend y por qué?

La interfaz del juez debe funcionar sin conexión (AC-DS-03): la competencia no se detiene por el sistema. Se descartó app nativa (requiere stores y dos codebases) en favor de PWA + IndexedDB. Solo la pantalla del juez opera offline; el resto requiere conexión.

**Recorrido:**
`[[ADR-003-offline-first-pwa]]` → `[[ADR-015-dexie-indexeddb-frontend]]` → `[[arquitectura/competencia]]`

---

### 4. ¿Qué ADRs gobiernan el BC Competencia?

Competencia es el Core Domain y el más regulado. Cinco ADRs lo gobiernan directamente:

| ADR | Qué define |
|-----|-----------|
| [[ADR-001-event-sourcing-competencia]] | Event Sourcing para Performance y Competencia |
| [[ADR-008-event-store-sqlite]] | Esquema de la tabla events; concurrencia optimista |
| [[ADR-014-penalizaciones-acumulables]] | `rp_penalizado = rp_medido - Σpenalizaciones` |
| [[ADR-018-hash-sha256-auditoria]] | Hash SHA-256 de la secuencia canónica al cerrar disciplina |
| [[ADR-006-estructura-bc-first]] | Organización hexagonal por capas (api/application/domain/infrastructure) |

**Recorrido:**
`[[arquitectura/competencia]]` → `[[ADR-001-event-sourcing-competencia]]` → `[[ADR-008-event-store-sqlite]]` → `[[ADR-014-penalizaciones-acumulables]]`

---

### 5. ¿Hay decisiones que se contradicen o fueron superadas?

**ADR supersedido confirmado:**
- [[ADR-010-docker-cloud-run]] — Docker + Cloud Run fue reemplazado por [[ADR-021-fly-io]] (Fly.io). Las páginas del wiki reflejan el estado vigente (ADR-021), pero los documentos de dominio históricos pueden mencionar Cloud Run.

**Desalineación conocida (D-03):**
- Documentos en `docs/dominio/` anteriores a ADR-007 mencionan PostgreSQL como base vigente. La jerarquía de fuentes de verdad establece que ADR-007 prevalece.

**Recorrido:**
`[[ADR-010-docker-cloud-run]]` → `[[ADR-021-fly-io]]` (para ver la transición de despliegue)

---

### 6. ¿Qué decisión justifica la estructura BC-first del código?

ADR-005 define los 6 BCs como unidades de negocio. ADR-006 los materializa en la estructura del repositorio: cada BC tiene su propia carpeta con capas `api/`, `application/`, `domain/`, `infrastructure/`. No hay imports directos entre BCs.

**Recorrido:**
`[[ADR-005-bounded-contexts-ddd-estrategico]]` → `[[ADR-006-estructura-bc-first]]` → `[[arquitectura/context-map]]`

> Dato experimental documentado en ADR-005: el Event Storming produjo un modelo más simple que el análisis estático de RFs. El BC Configuración fue eliminado porque ningún evento le pertenecía exclusivamente.

---

### 7. ¿Qué decisiones afectan a todos los BCs?

Hay ADRs transversales que aplican sin excepción a los seis BCs:

| ADR | Alcance |
|-----|---------|
| [[ADR-002-fastapi-backend]] | Framework HTTP para todos los BCs |
| [[ADR-005-bounded-contexts-ddd-estrategico]] | Diseño estratégico; 6 BCs definitivos |
| [[ADR-006-estructura-bc-first]] | Estructura de código BC-first |
| [[ADR-007-sqlite-persistencia-bc]] | Un archivo .db por BC |
| [[ADR-009-migraciones-por-bc]] | Alembic por BC |
| [[ADR-011-structlog-logging]] | Logging estructurado |
| [[ADR-012-rfc7807-errores-http]] | Formato de errores HTTP |
| [[ADR-013-exception-management]] | Política de excepciones |
| [[ADR-021-fly-io]] | Plataforma de despliegue |

---

## ADRs por área de impacto

| Área | ADRs |
|------|------|
| Persistencia | [[ADR-007-sqlite-persistencia-bc]], [[ADR-008-event-store-sqlite]], [[ADR-009-migraciones-por-bc]] |
| Event Sourcing | [[ADR-001-event-sourcing-competencia]], [[ADR-017-notificaciones-event-sourcing]], [[ADR-008-event-store-sqlite]] |
| Arquitectura interna | [[ADR-005-bounded-contexts-ddd-estrategico]], [[ADR-006-estructura-bc-first]] |
| Frontend / offline | [[ADR-003-offline-first-pwa]], [[ADR-015-dexie-indexeddb-frontend]] |
| Backend / framework | [[ADR-002-fastapi-backend]] |
| Dominio / reglas | [[ADR-004-reglas-como-datos]], [[ADR-014-penalizaciones-acumulables]], [[ADR-022-categoria-shared]] |
| API / errores | [[ADR-012-rfc7807-errores-http]], [[ADR-013-exception-management]] |
| Seguridad | [[ADR-018-hash-sha256-auditoria]], [[ADR-019-politica-contrasenas]], [[ADR-020-modelo-usuarios-roles]] |
| Notificaciones | [[ADR-016-resend-email-provider]], [[ADR-017-notificaciones-event-sourcing]] |
| Observabilidad | [[ADR-011-structlog-logging]] |
| Despliegue | [[ADR-021-fly-io]] *(supersede ADR-010)* |

---

## Páginas hub de esta vista

| Página | Por qué es hub |
|--------|----------------|
| `[[ADR-001-event-sourcing-competencia]]` | Decisión fundacional del Core Domain |
| `[[ADR-005-bounded-contexts-ddd-estrategico]]` | Diseño estratégico; define los 6 BCs |
| `[[ADR-006-estructura-bc-first]]` | Materialización del diseño en código |
| `[[ADR-007-sqlite-persistencia-bc]]` | Decisión de persistencia con mayor impacto cruzado; reemplaza PostgreSQL |
| `[[ADR-021-fly-io]]` | Estado vigente del despliegue (supersede ADR-010) |
