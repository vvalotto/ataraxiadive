---
title: "Notificaciones — SQLiteNotificacionEventStore + EmailPort adapters"
type: arquitectura-componente
bc: notificaciones
capa: infrastructure
tipo_componente: event-store + adapters
responsabilidad: "Event store ES en notificaciones.db + adapters EmailPort (Resend / Logging)"
interfaces_out:
  - EmailPort (implementado por ResendEmailAdapter y LoggingEmailAdapter)
  - NotificacionRepository (implementado por SQLiteNotificacionRepository)
adr_refs: [ADR-008, ADR-016, ADR-017]
last_updated: "2026-05-23"
sources:
  - src/notificaciones/infrastructure/event_store/sqlite_notificacion_event_store.py
  - src/notificaciones/infrastructure/repositories/sqlite_notificacion_repository.py
  - src/notificaciones/infrastructure/email/resend_email_adapter.py
  - src/notificaciones/infrastructure/email/logging_email_adapter.py
---

# SQLiteNotificacionEventStore + EmailPort Adapters — BC Notificaciones

---

## SQLiteNotificacionEventStore

Implementación del event store en `notificaciones.db`. Es la pieza de infraestructura central del BC.

### Tabla: `notificaciones_events`

```sql
CREATE TABLE IF NOT EXISTS notificaciones_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_id   TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    payload     TEXT NOT NULL,    -- JSON serializado
    version     INTEGER NOT NULL,
    occurred_at TEXT NOT NULL
)
```

**Índices:**
- `idx_notificaciones_stream` — sobre `stream_id` (carga por aggregate)
- `idx_notificaciones_fuente` — sobre `json_extract(payload, '$.evento_fuente_id')` (búsqueda de idempotencia)

### Métodos clave

| Método | Descripción |
|--------|-------------|
| `append(stream_id, event_type, payload, expected_version?)` | Inserta evento. Si `expected_version` está presente, verifica concurrencia optimista. Versión autoincrementada por stream. |
| `load(stream_id)` | Retorna lista de dicts `{event_type, payload, version, occurred_at}` ordenada por versión ASC. |
| `exists_success_by_evento_fuente_id(evento_fuente_id)` | Consulta `json_extract` para detectar si ya existe `NotificacionEnviada` con ese `evento_fuente_id`. Núcleo de la idempotencia. |
| `_ensure_schema(db)` | Crea tabla e índices si no existen — patrón auto-migration. |

**Variable de entorno:** `NOTIFICACIONES_DB_PATH` (default `data/notificaciones.db`).

### SQLiteNotificacionRepository

Thin wrapper sobre `SQLiteNotificacionEventStore` — implementa `NotificacionRepository` delegando todas las operaciones. Permite inyección de `SQLiteNotificacionEventStore` alternativo en tests.

```python
class SQLiteNotificacionRepository(NotificacionRepository):
    def __init__(self, event_store: SQLiteNotificacionEventStore | None = None) -> None:
        self._event_store = event_store or SQLiteNotificacionEventStore()
```

---

## EmailPort

```python
class EmailPort(ABC):
    @abstractmethod
    async def enviar(self, destinatario: Destinatario, contenido: ContenidoEmail) -> str | None: ...
```

Retorna `proveedor_id` (string del proveedor externo) o `None`. Las implementaciones concretan este contrato.

---

## ResendEmailAdapter

Implementación de producción — HTTP POST a la API de Resend.

**Variables de entorno requeridas:**
- `RESEND_API_KEY` — API key de autenticación (obligatoria)
- `NOTIFICACIONES_EMAIL_FROM` — dirección remitente (obligatoria)
- `RESEND_BASE_URL` — base URL (default `https://api.resend.com`)

**Flujo de `enviar()`:**
1. `_assert_configured()` — falla rápido si faltan vars de entorno
2. Construye payload `{from, to, subject, text, html?}`
3. POST `/emails` con `Authorization: Bearer {api_key}`
4. `response.raise_for_status()` — `RuntimeError` si HTTP error
5. Extrae `data["id"]` como `proveedor_id` — `RuntimeError` si falta
6. Retorna `proveedor_id`

**Inyección de cliente:** acepta `client_factory` opcional para tests (permite usar `httpx.MockTransport` sin depender de la red real).

---

## LoggingEmailAdapter

Implementación de desarrollo — escribe en el log en lugar de enviar.

```python
class LoggingEmailAdapter(EmailPort):
    async def enviar(self, destinatario, contenido) -> str:
        provider_id = f"log-{uuid.uuid4()}"
        logger.warning(...)  # tabla ASCII con destinatario + asunto + primeras 15 líneas del cuerpo
        return provider_id
```

- Siempre retorna un `provider_id` ficticio `log-{uuid}` — permite que el flujo del aggregate complete normalmente
- Activo cuando `RESEND_API_KEY` no está configurado (inyectado desde composition root)
- No lanza excepciones — nunca genera `NotificacionFallida` por razones técnicas del adaptador

---

## Templates de email

| Template | Renderiza | Para |
|----------|-----------|------|
| `InscripcionConfirmadaTemplate` | Asunto + cuerpo texto con nombre, torneo, fecha, sede, disciplinas | P-10 |
| `ResultadosPublicadosTemplate` | Asunto + cuerpo texto por atleta con posición, RP, tarjeta, podio | P-11 |

Ambas implementan el protocolo `render(evento) → ContenidoEmail`. Las políticas las inyectan en construcción.

---

## Relaciones

**Contenedor:** [[arquitectura/notificaciones]]

- Persiste eventos del [[notificacion-aggregate]]
- Usado por [[command-handlers-notificaciones]] vía `NotificacionRepository`
- `ResendEmailAdapter` y `LoggingEmailAdapter` son inyectados por `configure_identity_dependencies()` desde `app.py`

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/notificaciones/infrastructure/event_store/sqlite_notificacion_event_store.py` | Event store ES en notificaciones.db |
| `src/notificaciones/infrastructure/repositories/sqlite_notificacion_repository.py` | Repositorio de consulta de notificaciones |
| `src/notificaciones/infrastructure/email/resend_email_adapter.py` | Adapter Resend — envío real vía API REST |
| `src/notificaciones/infrastructure/email/logging_email_adapter.py` | Adapter Logging — fallback sin API key (desarrollo) |
