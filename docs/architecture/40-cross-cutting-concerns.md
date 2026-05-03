# 40 Cross-Cutting Concerns

## Propósito

Describir las preocupaciones transversales de arquitectura que atraviesan a
varios bounded contexts de AtaraxiaDive.

Esta vista documenta restricciones y mecanismos compartidos que no pertenecen a
un único BC, pero que condicionan el diseño e implementación del sistema
completo.

## Alcance

Incluye:

- persistencia y aislación por BC;
- Event Sourcing y event store compartido;
- seguridad y autenticación;
- manejo de errores;
- observabilidad y logging;
- migraciones y composición de aplicación.

No cubre en detalle la estrategia offline-first del juez, que se desarrolla en
`50-offline-sync.md`.

## Fuentes

- `docs/adr/ADR-001-event-sourcing-competencia.md`
- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
- `docs/adr/ADR-007-sqlite-persistencia-bc.md`
- `docs/adr/ADR-008-event-store-sqlite.md`
- `docs/adr/ADR-009-migraciones-por-bc.md`
- `docs/adr/ADR-011-structlog-logging.md`
- `docs/adr/ADR-012-rfc7807-errores-http.md`
- `docs/adr/ADR-013-exception-management.md`
- `src/app.py`
- `src/shared/`

## Aislación de persistencia por bounded context

La regla transversal principal es: **cada BC es dueño exclusivo de su
persistencia**.

Esto se materializa con un archivo SQLite por bounded context:

- `competencia.db`
- `torneo.db`
- `registro.db`
- `resultados.db`
- `identidad.db`
- `notificaciones.db`

Consecuencias arquitectónicas:

- no hay joins entre BCs;
- el schema evoluciona por contexto;
- un error o cambio en un BC no debe obligar a modificar la persistencia de
  otro;
- cualquier lectura cross-BC debe pasar por ACL, evento o lookup explícito.

## Event Sourcing como preocupación transversal selectiva

AtaraxiaDive no aplica Event Sourcing de forma uniforme. La decisión es
selectiva:

- `Competencia`: por auditabilidad regulatoria y reconstrucción de historia;
- `Notificaciones`: por idempotencia de envío;
- resto de BCs: CRUD convencional.

Esto introduce una preocupación transversal mixta:

- los BCs CRUD comparten principios de repositorio y tablas convencionales;
- los BCs ES comparten un puerto común `EventStorePort`;
- la infraestructura `SQLiteEventStore` vive en `shared/` para evitar
  duplicación de mecanismo.

## Event Store compartido

Los BCs con ES usan una tabla append-only en SQLite y un contrato común
implementado en [sqlite_event_store.py](/Users/victor/PycharmProjects/ataraxiadive/src/shared/infrastructure/event_store/sqlite_event_store.py).

Aspectos relevantes:

- streams identificados por `stream_id`;
- append en orden por versión;
- control de concurrencia optimista;
- carga por stream individual o por prefijo;
- serialización JSON del payload.

Esto es transversal porque fija:

- cómo se reconstituyen aggregates;
- cómo se leen proyecciones o snapshots lógicos;
- qué capacidades pueden reutilizar otros BCs ES futuros.

## Seguridad y autenticación

La autenticación es una preocupación transversal, pero su implementación está
encapsulada en `Identidad`.

Las reglas que aplican a todo el sistema son:

- un único contrato de claims JWT;
- verificación local del token en BCs consumidores;
- ausencia de consultas síncronas recurrentes a `Identidad`;
- uso de roles como dato de autorización de alto nivel.

El JWT emitido por `Identidad` incluye, como mínimo:

- `sub`;
- `email`;
- `rol`;
- `exp`.

Esto mantiene a `Identidad` como proveedor de identidad y a los demás BCs como
consumidores conformist del contrato.

## Manejo de errores

La arquitectura define dos niveles complementarios:

### Dominio

Cada BC debería concentrar sus excepciones en `domain/exceptions.py`, con
`DomainError` como base cuando el BC ya adoptó la convención completa.

### API

El mapeo HTTP debe vivir en `api/exception_handlers.py` y seguir RFC 7807.

Estado actual del repo:

- `Competencia` aplica la convención con mayor fidelidad;
- `Torneo` tiene handlers específicos con body estilo problem details;
- `Registro`, `Identidad` y `Resultados` todavía devuelven respuestas de error
  más simples en varias rutas.

La preocupación transversal, entonces, no es solo la forma del error, sino la
**consistencia pendiente** entre BCs.

## Composición y wiring cross-BC

El composition root del sistema está en [app.py](/Users/victor/PycharmProjects/ataraxiadive/src/app.py).

Ese archivo concentra preocupaciones transversales que no pertenecen al dominio:

- registro de routers;
- registro de exception handlers;
- callbacks o políticas que cruzan BCs;
- creación de adaptadores concretos para integraciones.

Un ejemplo actual es la política `CompetenciaFinalizada -> CalcularRanking`,
armada en el composition root y no dentro del dominio de `Competencia` o
`Resultados`.

## Migraciones por BC

La estrategia acordada es tener migraciones independientes por bounded context.

Esto es transversal porque preserva:

- independencia evolutiva del schema;
- coherencia con un archivo SQLite por BC;
- despliegues más controlables por contexto.

Estado actual del repo:

- existe estructura de migraciones en `Competencia`;
- el patrón todavía no está desplegado homogéneamente en todos los BCs.

## Observabilidad y logging

La decisión aceptada es usar `structlog` con:

- salida legible en desarrollo;
- JSON en producción;
- context variables por request.

Sin embargo, en el código actual todavía no aparece la configuración homogénea
de `shared/logging.py` ni un middleware de request tracing ya integrado al entry
point.

Esto deja una distinción importante:

- **decisión arquitectónica aceptada**: logging estructurado;
- **estado de implementación**: parcial o pendiente de adopción transversal.

## Arquitectura frontend (SP4/SP5)

La incorporación del frontend en SP4 introdujo preocupaciones transversales que
no son exclusivas de un BC pero condicionan el sistema completo.

**React PWA con Vite:**

- SPA instalable como PWA (`vite-plugin-pwa`);
- build estático servido independientemente del backend;
- proxy Vite en desarrollo para `/api` y `/resultados` hacia FastAPI.

**Portales por rol:**

El frontend tiene tres portales diferenciados por `rol` del JWT:

- `ORGANIZADOR`: gestión de torneos, competencias y grilla;
- `JUEZ`: operación durante la competencia (tarjetas, OTs);
- `ATLETA`: mis torneos, mi grilla, mis resultados, rankings (INC-5.7).

La discriminación de portal ocurre en el frontend a partir del claim `rol` del
JWT, sin consulta adicional al backend.

**Preocupaciones transversales del frontend:**

- el contrato JWT (especialmente `sub`, `rol`, `nombre`, `apellido`) es consumido
  directamente por el frontend para rutas y vistas — cualquier cambio en claims
  impacta la presentación;
- el proxy Vite en desarrollo debe estar alineado con los prefijos de los routers
  FastAPI — divergencia causa 404 silenciosos;
- el build de producción es estático y no incluye variables de entorno de runtime
  — la URL base del backend se fija en tiempo de build.

## Configuración por entorno

Algunas decisiones transversales dependen de variables de entorno:

- `IDENTIDAD_JWT_SECRET`;
- expiración JWT;
- paths de bases SQLite por BC.

La arquitectura favorece inyección por configuración externa y evita hardcodear
secretos o ubicaciones absolutas dentro del dominio.

## Tabla resumen

| Preocupación | Decisión vigente | Estado |
|--------------|------------------|--------|
| Persistencia por BC | Un archivo SQLite por BC | Implementado |
| Event Sourcing selectivo | Solo `Competencia` y `Notificaciones` | Parcialmente implementado |
| Event store compartido | `shared.EventStorePort` + `SQLiteEventStore` | Implementado |
| JWT cross-cutting | Claims locales consumidos por downstreams y frontend | Implementado |
| RFC 7807 | Convención estándar de errores HTTP | Parcialmente implementado |
| Jerarquía de excepciones | `domain/exceptions.py` por BC | Parcialmente implementado |
| Migraciones por BC | Un entorno de migración por contexto | Parcialmente implementado |
| Logging estructurado | `structlog` | Mayormente pendiente |
| Frontend PWA | React + Vite · portales por rol · proxy de desarrollo | Implementado (SP4/SP5) |

## Restricciones a preservar

- ningún BC debe acceder arbitrariamente a la base de otro fuera de ACLs
  explícitos y contenidos;
- la lógica de autenticación no debe filtrarse al dominio de BCs funcionales;
- los BCs con Event Sourcing deben conservar append-only y control de
  concurrencia;
- el mapeo HTTP de errores no debe llevar lógica de dominio al API layer;
- las decisiones transversales aceptadas en ADRs deben reflejarse
  progresivamente en todos los BCs, no solo en los primeros implementados.

