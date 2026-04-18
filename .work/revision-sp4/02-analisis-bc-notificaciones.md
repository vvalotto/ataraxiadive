# Revisión de Calidad — Cierre SP4
## Análisis BC Notificaciones — INC-4.5

**Fecha:** 2026-04-16
**Archivos revisados:**
- `src/notificaciones/domain/aggregates/notificacion.py`
- `src/notificaciones/application/commands/solicitar_envio.py`
- `src/notificaciones/application/commands/enviar_notificacion.py`
- `src/notificaciones/application/policies/politica_p10.py`
- `src/notificaciones/application/policies/politica_p11.py`
- `src/notificaciones/domain/ports/notificacion_repository.py`
- `src/notificaciones/domain/ports/email_port.py`
- `src/notificaciones/infrastructure/repositories/sqlite_notificacion_repository.py`
- `src/notificaciones/infrastructure/event_store/sqlite_notificacion_event_store.py`
- `src/notificaciones/infrastructure/email/resend_email_adapter.py`
- `src/notificaciones/infrastructure/email/logging_email_adapter.py`

---

## Lo que está bien

### Aggregate `Notificacion`

La invariante de idempotencia está correctamente implementada. `solicitar_envio()` recibe
`existe_envio_exitoso_previo: bool` como parámetro explícito y devuelve `None` si es `True` —
el aggregate no emite ningún evento y el handler termina limpiamente. La lógica de
idempotencia no está en la infraestructura sino en el domain, que es el lugar correcto.

Las tres transiciones de estado (`Nueva → Solicitada`, `Solicitada → Enviada`,
`Solicitada → Fallida`) están bien separadas. `_assert_solicitada()` encapsula la
precondición de `registrar_envio_exitoso` y `registrar_fallo`.

### Separación hexagonal

El dominio no importa nada de infraestructura — la regla de oro del proyecto se cumple.
Los puertos (`EmailPort`, `NotificacionRepository`) están correctamente en `domain/ports/`.
`EnviarNotificacionHandler` depende de `EmailPort` (abstracto), no del adaptador concreto.

### `SQLiteNotificacionEventStore` — query de idempotencia eficiente

`exists_success_by_evento_fuente_id` usa `json_extract` de SQLite sobre un índice
funcional creado en `_CREATE_FUENTE_INDEX`. La query no hace un full table scan —
la idempotencia se verifica eficientemente incluso con miles de notificaciones.

```sql
CREATE INDEX IF NOT EXISTS idx_notificaciones_fuente
ON notificaciones_events(json_extract(payload, '$.evento_fuente_id'))
```

Esta es una decisión de diseño correcta y no obvia.

### `EnviarNotificacionHandler` — gestión del fallo

El handler reconoce el fallo de `email_port.enviar()` y lo registra como
`NotificacionFallida` en el event store. Esto mantiene trazabilidad completa:
el fallo queda en el audit trail del aggregate, no se pierde silenciosamente.
El `# noqa: BLE001` está justificado: cualquier excepción del proveedor debe
convertirse en un fallo registrado, no en una excepción no manejada.

---

## Issues encontrados

### ARCH-01 — DIP leve: `SQLiteNotificacionRepository` instancia su dependencia

```python
# sqlite_notificacion_repository.py
class SQLiteNotificacionRepository(NotificacionRepository):
    def __init__(self, event_store: SQLiteNotificacionEventStore | None = None) -> None:
        self._event_store = event_store or SQLiteNotificacionEventStore()  # ← problema
```

El repositorio instancia `SQLiteNotificacionEventStore()` por defecto. Esto viola DIP
levemente: la clase de infraestructura no debería auto-instanciar sus propias dependencias
— eso es responsabilidad del composition root (`app.py`). Con el patrón actual, si se
quiere cambiar el path de la DB o inyectar un mock en tests, hay que pasar el store
explícitamente, lo que no es evidente para quien use la clase.

**Comparación:** `SQLiteEventStore` de Competencia se inyecta desde `app.py` sin default.
Notificaciones es inconsistente con ese patrón.

**Severidad:** Baja — funciona correctamente. La inyección desde `app.py` sí ocurre en
producción; el default solo se activa si alguien instancia el repo directamente.

---

### ARCH-02 — `_ensure_schema` llamado en cada operación

```python
async def append(self, ...) -> None:
    async with aiosqlite.connect(self._db_path) as db:
        await self._ensure_schema(db)   # ← DDL en cada llamada
        ...

async def load(self, ...) -> list[...]:
    async with aiosqlite.connect(self._db_path) as db:
        await self._ensure_schema(db)   # ← DDL en cada llamada
        ...
```

Cada operación ejecuta 3 sentencias DDL (`CREATE TABLE IF NOT EXISTS` + 2 `CREATE INDEX
IF NOT EXISTS`) antes de la query real. SQLite evalúa el `IF NOT EXISTS` en cada llamada.
En un servidor con múltiples requests concurrentes, esto añade overhead innecesario.

**Nota:** El mismo patrón existe en `SQLiteEventStore` de Competencia (pre-existente desde
SP1, aceptado). La diferencia es que Competencia procesa eventos de alta frecuencia durante
una competencia activa; Notificaciones tiene volumen mucho menor. El impacto es mínimo.

**Severidad:** Baja — no bloquea, no es incorrecto. Deuda conocida compartida con Competencia.
Opción de mejora SP5: inicializar schema en startup (lifespan event de FastAPI).

---

### DES-01 — Lógica duplicada entre `PoliticaP10Handler` y `PoliticaP11Handler`

`_registrar_fallo_sin_email` es idéntico en ambas políticas:

```python
# politica_p10.py
async def _registrar_fallo_sin_email(self, evento: InscripcionConfirmada) -> None:
    if await self._repository.exists_success_by_evento_fuente_id(evento.id):
        return
    aggregate = Notificacion.registrar_fallo_de_solicitud(
        evento_fuente_id=EventoFuenteId(evento.id),
        motivo="destinatario_sin_email",
    )
    await persistir_eventos_pendientes(self._repository, aggregate)

# politica_p11.py — firma diferente pero lógica idéntica
async def _registrar_fallo_sin_email(self, evento_fuente_id: str) -> None:
    if await self._repository.exists_success_by_evento_fuente_id(evento_fuente_id):
        return
    aggregate = Notificacion.registrar_fallo_de_solicitud(
        evento_fuente_id=EventoFuenteId(evento_fuente_id),
        motivo="destinatario_sin_email",
    )
    await persistir_eventos_pendientes(self._repository, aggregate)
```

La versión de P-11 ya es la más limpia (recibe `str` en vez del objeto evento). P-10
debería alinearse. Ambas podrían delegar en una función utilitaria compartida en
`application/commands/solicitar_envio.py` (ya importado por ambas) o en un helper
de aplicación.

**Severidad:** Media — no es incorrecto, pero si se agregan políticas P-12, P-13, la
duplicación crece linealmente.

---

### DES-02 — `PoliticaP11Handler._evento_fuente_id` no usa `self` (causa del LCOM=2)

```python
# politica_p11.py
def _evento_fuente_id(
    self,
    evento: ResultadosPublicados,
    resultado: ResultadoPublicadoAtleta,
) -> str:
    return f"{evento.id}:{resultado.atleta_id}"
```

El método no accede a ningún atributo de instancia. Debería ser `@staticmethod`.
El DesignReviewer reportó `PoliticaP11Handler` con LCOM=2 — este método sin estado
es exactamente la causa: forma un grupo de cohesión separado del resto de la clase.

**Fix trivial:**
```python
@staticmethod
def _evento_fuente_id(evento: ResultadosPublicados, resultado: ResultadoPublicadoAtleta) -> str:
    return f"{evento.id}:{resultado.atleta_id}"
```

**Severidad:** Baja — una línea de cambio, elimina el LCOM=2.

---

### DOC-01 — Discrepancia entre documentación y código en P-11

`CLAUDE.md §8` (Lenguaje Ubicuo) y la documentación generada en `docs/design/notificaciones.md`
(US-4.6.7) describen P-11 como:

> `TarjetaAsignada(roja)` → email al atleta (motivo DQ)

Pero el código implementa `PoliticaP11Handler` con el evento **`ResultadosPublicados`**
(resultados finales de disciplina → email a todos los atletas participantes, excluyendo
retirados). Son dos comportamientos completamente distintos.

**Impacto:** La documentación de `docs/design/notificaciones.md` que se acaba de crear
en US-4.6.7 describe P-11 incorrectamente. Hay que corregirla.

**Acción requerida:**
1. Verificar la US-4.5.4 para confirmar cuál es el comportamiento diseñado
2. Actualizar `CLAUDE.md §8` (si P-11 fue redefinida durante la implementación)
3. Corregir `docs/design/notificaciones.md` — tabla de políticas y referencias

**Severidad:** Alta (documental) — el código funciona, la documentación miente.

---

## Resumen de issues

| ID | Área | Issue | Severidad | Candidato SP-ADJ-06 |
|----|------|-------|-----------|:-------------------:|
| ARCH-01 | `sqlite_notificacion_repository.py` | DIP leve — default instancia concreta | Baja | No (funcional) |
| ARCH-02 | `sqlite_notificacion_event_store.py` | `_ensure_schema` en cada operación | Baja | No (deuda compartida con Competencia) |
| DES-01 | `politica_p10.py` + `politica_p11.py` | `_registrar_fallo_sin_email` duplicado | Media | Sí |
| DES-02 | `politica_p11.py` | `_evento_fuente_id` sin `@staticmethod` | Baja | Sí (fix trivial) |
| DOC-01 | `CLAUDE.md`, `notificaciones.md` | P-11 documentada como tarjeta roja, implementada como resultados publicados | Alta | Sí (corrección documental urgente) |

---

## Acción inmediata recomendada

**DOC-01 debe resolverse antes de continuar la revisión.** La documentación recién
generada (US-4.6.7) es parte de la baseline BL-004 y describe P-11 incorrectamente.

Verificar `docs/specs/sp4/US-4.5.4.md` para determinar si:
- (a) P-11 fue rediseñada durante la implementación (resultados publicados reemplazó a tarjeta roja)
- (b) Hay una P-11 pendiente de implementar (tarjeta roja) y lo implementado es una política adicional no documentada

*Creado: 2026-04-16 — Revisión pre-BL-004*
