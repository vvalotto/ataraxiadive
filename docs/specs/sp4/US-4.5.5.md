# US-4.5.5: Cablear P-10 al endpoint de inscripción

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.5
**Bounded Context**: `registro` (productor) · `notificaciones` (consumidor)
**Capas afectadas**: `registro/api/router.py` · `src/app.py`

---

## Descripción

Como **sistema**,
quiero **que al confirmar una inscripción vía HTTP se dispare automáticamente la Política P-10**
para **enviar el email de confirmación al atleta sin intervención manual**.

---

## Contexto del dominio

### Problema identificado

`build_p10_handler()` está definido en `app.py` (composition root) pero no está cableado
al `InscribirAtletaHandler`. El router instancia el handler sin el callback:

```python
# registro/api/router.py:166 — GAP: sin callback P-10
handler = InscribirAtletaHandler(_inscripcion_repo(), _torneo_consulta())
```

Además, el callback recibe un `Inscripcion` que solo contiene `atleta_id`, `torneo_id`
y `disciplinas` — pero `PoliticaP10Handler` necesita `atleta_email`, `atleta_nombre`,
`torneo_nombre`, `torneo_fecha`, `torneo_sede`. Estos datos deben buscarse en los
repositorios de Registro y Torneo dentro del composition root.

### Datos disponibles

| Dato necesario | Fuente |
|---|---|
| `atleta_email`, `atleta_nombre` | `AtletaRepository.find_by_id(inscripcion.atleta_id)` |
| `torneo_nombre`, `torneo_fecha_inicio`, `torneo_sede` | `TorneoRepository.find_by_id(inscripcion.torneo_id)` |
| `disciplinas` | `inscripcion.disciplinas` (ya disponible) |
| `evento_fuente_id` | `str(inscripcion.inscripcion_id)` |

---

## Especificación del comportamiento

### Invariantes

- **INV-4.5.5-01:** Si `atleta` o `torneo` no existen al construir `InscripcionConfirmada`,
  el callback falla silenciosamente (no interrumpe la inscripción — mismo contrato que INV-4.5.3-04).
- **INV-4.5.5-02:** El `evento_fuente_id` del `InscripcionConfirmada` es `str(inscripcion.inscripcion_id)`.
  Garantiza idempotencia: si el callback se ejecuta dos veces para la misma inscripción,
  P-10 no duplica el email (INV-4.5.1-01).
- **INV-4.5.5-03:** El wiring no introduce imports directos de `notificaciones` en `registro`.
  El callback se inyecta desde `app.py` — la dependencia fluye hacia adentro, no entre BCs.

### Flujo completo tras el fix

```
POST /inscripciones
  → InscribirAtletaHandler.handle(cmd)
    → inscripcion guardada en repo
    → on_inscripcion_confirmada(inscripcion) llamado  ← GAP actual
        → buscar Atleta por atleta_id
        → buscar Torneo por torneo_id
        → construir InscripcionConfirmada(...)
        → PoliticaP10Handler.handle(InscripcionConfirmada)
            → SolicitarEnvio → EnviarNotificacion → Resend API
```

---

## Implementación

### 1. Variable de módulo + configurador en `registro/api/router.py`

```python
# Al inicio del módulo, junto a las otras variables de configuración
_on_inscripcion_confirmada_callback: Callable[[Inscripcion], Awaitable[None]] | None = None

def configure_inscripcion_notificaciones(
    callback: Callable[[Inscripcion], Awaitable[None]],
) -> None:
    global _on_inscripcion_confirmada_callback
    _on_inscripcion_confirmada_callback = callback
```

```python
# En el endpoint — pasar el callback al handler
@router.post("/inscripciones", status_code=201)
async def inscribir_atleta(body: InscribirAtletaRequest, _: AtletaDep) -> JSONResponse:
    handler = InscribirAtletaHandler(
        _inscripcion_repo(),
        _torneo_consulta(),
        on_inscripcion_confirmada=_on_inscripcion_confirmada_callback,  # ← fix
    )
    ...
```

### 2. Adapter + wiring en `app.py`

```python
def build_on_inscripcion_callback() -> Callable[[Inscripcion], Awaitable[None]]:
    """Composition root: traduce Inscripcion → InscripcionConfirmada y dispara P-10."""
    p10 = build_p10_handler()
    atleta_repo = SQLiteAtletaRepository(os.getenv("REGISTRO_DB_PATH", "data/registro.db"))
    torneo_repo = SQLiteTorneoRepository(os.getenv("TORNEO_DB_PATH", "data/torneo.db"))

    async def _callback(inscripcion: Inscripcion) -> None:
        atleta = await atleta_repo.find_by_id(inscripcion.atleta_id)
        torneo = await torneo_repo.find_by_id(inscripcion.torneo_id)
        if atleta is None or torneo is None:
            return
        evento = InscripcionConfirmada(
            id=str(inscripcion.inscripcion_id),
            atleta_id=str(inscripcion.atleta_id),
            atleta_email=atleta.email,
            atleta_nombre=atleta.nombre,
            torneo_nombre=torneo.nombre,
            torneo_fecha=torneo.fecha_inicio,
            torneo_sede=torneo.sede.nombre,
            disciplinas=tuple(str(d) for d in inscripcion.disciplinas),
        )
        await p10.handle(evento)

    return _callback


# Al crear la app — después de include_router(registro_router):
configure_inscripcion_notificaciones(build_on_inscripcion_callback())
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.5.5 — Cableado P-10 al endpoint de inscripción

  Scenario: email enviado al inscribir atleta vía HTTP
    Given el servidor corre con RESEND_API_KEY y NOTIFICACIONES_EMAIL_FROM configurados
    And existe un atleta con email "test@ataraxiadive.io" y un torneo abierto
    When se hace POST /inscripciones con atleta_id y torneo_id válidos
    Then la inscripción se crea con status 201
    And se envía un email a "test@ataraxiadive.io" con asunto que contiene el nombre del torneo
    And el event store de notificaciones registra un NotificacionEnviada

  Scenario: idempotencia end-to-end — dos llamadas con la misma inscripcion_id
    Given la inscripción "ins-001" ya fue procesada y su NotificacionEnviada existe en el store
    When el callback P-10 se ejecuta de nuevo con inscripcion_id="ins-001"
    Then NO se envía un segundo email
    And el event store sigue con exactamente un NotificacionEnviada para "ins-001"

  Scenario: atleta o torneo no encontrado — fallo silencioso
    Given atleta_id no existe en el repositorio
    When el callback se ejecuta
    Then la inscripción queda guardada con status 201
    And NO se lanza excepción (fallo silencioso del callback)
```

---

## Impacto arquitectónico

- [x] `registro/api/router.py` — variable de módulo + `configure_inscripcion_notificaciones()`
- [x] `src/app.py` — `build_on_inscripcion_callback()` + llamada a `configure_inscripcion_notificaciones()`
- [ ] No requiere cambios en `domain/` ni en `notificaciones/`

**Principio respetado:** el callback se inyecta desde el composition root (`app.py`).
`registro/` no importa `notificaciones/`. La dependencia fluye hacia adentro.

---

## Tests requeridos

| Tipo | Descripción |
|---|---|
| Unit | `test_inscribir_atleta_handler_llama_callback` — verificar que el handler invoca el callback con la `Inscripcion` correcta |
| Integration | `test_p10_e2e_desde_endpoint` — POST `/inscripciones` con mock de Resend → verificar `NotificacionEnviada` en store |
| Manual (smoke) | Arrancar servidor con `RESEND_API_KEY` real, inscribir atleta con email real, verificar recepción |

---

## Referencias

- Prereq: US-4.5.1 · US-4.5.2 · US-4.5.3
- Gap detectado al intentar verificar DoD INC-4.5 con email real
- `src/registro/application/commands/inscribir_atleta.py:30` — puerto del callback ya existe
- `src/app.py:84` — `build_p10_handler()` ya existe, solo falta el adapter + wiring

---

*Redactado: 2026-04-15 — INC-4.5, gap detectado en verificación DoD*
