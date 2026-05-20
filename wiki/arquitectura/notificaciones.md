---
title: "BC Notificaciones — Generic Domain"
type: arquitectura
last_updated: "2026-05-20"
sources:
  - docs/architecture/15-bc-notificaciones.md
tipo_ddd: Generic Domain
persistencia: Event Sourcing
db: notificaciones.db
---

# BC Notificaciones — Generic Domain

## Rol

**Generic Domain** downstream de todos los BCs funcionales. No decide negocio — administra de manera confiable la comunicación resultante.

**Responsabilidades:** suscribirse a eventos de dominio de otros BCs, decidir plantilla y canal, registrar cada intento de envío, garantizar idempotencia (exactly-once delivery), registrar éxito/fallo/reintento, delegar entrega a servicios externos.

## Persistencia

Event Sourcing sobre `notificaciones.db`. La razón principal es **idempotencia operativa**, no auditoría regulatoria.

Stream: `notificacion-{notificacion_id}`

## Aggregate principal: Notificacion

**Estados del ciclo de vida:**

```
NotificacionSolicitada → NotificacionEnviada
                      → NotificacionFallida → (NotificacionReintentada)
```

**Invariante clave:** unicidad lógica por `EventoFuenteId` — antes de ordenar un envío, el BC verifica si ya existe `NotificacionEnviada` para ese `eventoFuenteId`. Si existe → no envía.

## Value Objects

| VO | Descripción |
|----|-------------|
| `EventoFuenteId` | Clave de idempotencia — ID del evento fuente |
| `Destinatario` | `userId` + canal preferido |
| `ContenidoEmail` | Asunto (no vacío) + texto + HTML opcional |

## Políticas implementadas

| Política | Trigger | Destinatario | Implementada en |
|----------|---------|-------------|----------------|
| P-10 | `InscripcionConfirmada` | Atleta | US-4.5.3 / US-4.5.5 |
| P-11 | `ResultadosPublicados` | Todos los atletas de la disciplina | US-4.5.4 |

**Clave de idempotencia P-10:** `str(inscripcion.inscripcion_id)`
**Clave de idempotencia P-11:** `"{evento.id}:{atleta_id}"` (compuesta por atleta)

**Comportamiento de fallo sin bloquear:** si el atleta no tiene email o no existe durante el enriquecimiento, se registra `NotificacionFallida` con motivo, sin interrumpir el flujo principal del BC productor.

## Templates implementados

- `InscripcionConfirmadaTemplate`
- `ResultadosPublicadosTemplate`

## Adaptadores de canal

| Puerto | Adaptador actual | Estado |
|--------|-----------------|--------|
| `EmailPort` | `ResendEmailAdapter` (HTTP POST /emails) | ✅ Implementado |
| `PushPort` | — | ⏳ Solo diseño |

**Fallback de desarrollo:** si `RESEND_API_KEY` no está configurada, se inyecta `LoggingEmailAdapter` — registra el email en el log sin enviarlo.

## Mecanismo de integración (SP4)

Callbacks in-process registrados en el composition root (`src/app.py`). El router de Registro recibe un callback async opcional sin importar tipos de Notificaciones. Ningún BC funcional espera respuesta síncrona de Notificaciones.

## Estructura de capas

| Capa | Responsabilidad |
|------|----------------|
| `api/` | Endpoints de observabilidad / reintentos manuales |
| `application/` | `SolicitarEnvioHandler`, `EnviarNotificacionHandler`, `PoliticaP10Handler`, `PoliticaP11Handler`, `ReintentarNotificacionHandler` |
| `domain/` | `Notificacion`, `EventoFuenteId`, `Destinatario`, `ContenidoEmail`, `EmailPort`, `NotificacionRepository` |
| `infrastructure/` | `NotificacionEventStoreRepository`, `ResendEmailAdapter`, `LoggingEmailAdapter` |

## ADRs relacionados

- [[ADR-017-notificaciones-event-sourcing]] — justificación del ES en un BC genérico; flujo de idempotencia
- [[ADR-016-resend-email-provider]] — proveedor de email; sandbox `onboarding@resend.dev`; `LoggingEmailAdapter`
- [[ADR-008-event-store-sqlite]] — infraestructura compartida con Competencia
