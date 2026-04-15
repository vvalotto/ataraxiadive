# Reporte de Implementación — US-4.5.5
## Cableado P-10 al endpoint de inscripción

**Sprint:** SP4 — La Plataforma
**Incremento:** INC-4.5
**Branch:** `feature/US-4.5.5-cablear-p10`
**Fecha:** 2026-04-15
**Estado:** Completado

---

## Resumen

Se corrigió el gap de integración de P-10: `POST /registro/inscripciones` ahora dispara
automáticamente la política de confirmación por email cuando una inscripción se confirma
por HTTP.

El BC `registro` mantiene su frontera: no importa `notificaciones`. El router recibe un
callback async configurado desde `src/app.py`. El composition root enriquece la
`Inscripcion` con datos de atleta y torneo, construye `InscripcionConfirmada` y delega en
`PoliticaP10Handler`.

La idempotencia end-to-end usa `str(inscripcion.inscripcion_id)` como `evento_fuente_id`,
por lo que reprocesar el callback para la misma inscripción no duplica emails.

---

## Componentes Implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/registro/api/router.py` | Configurador `configure_inscripcion_notificaciones()` y callback inyectado en `InscribirAtletaHandler` |
| `src/app.py` | `build_on_inscripcion_confirmada_callback()` para enriquecer `Inscripcion` y llamar P-10 |

### Tests

| Archivo | Cobertura |
|---------|-----------|
| `tests/features/US-4.5.5-cablear-p10-inscripcion.feature` | Escenarios BDD aprobados para cableado P-10 desde inscripción |
| `tests/features/steps/cablear_p10_inscripcion_steps.py` | Automatización BDD con HTTP, SQLite temporal y fake email |
| `tests/unit/registro/test_inscribir_atleta_handler.py` | Callback post-save y no reversión ante fallo del callback |
| `tests/unit/test_app_p10_wiring.py` | Enriquecimiento `Inscripcion` -> `InscripcionConfirmada` y fallos silenciosos |
| `tests/integration/registro/test_p10_endpoint_wiring.py` | Endpoint HTTP real, persistencia de `NotificacionEnviada` e idempotencia |

### Documentación

| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp4/US-4.5.5-plan.md` | Plan y checklist de implementación |
| `docs/architecture/15-bc-notificaciones.md` | Wiring real de P-10 desde Registro |
| `docs/design/domain-model.md` | Adapter `build_on_inscripcion_confirmada_callback` |
| `docs/traceability/matrix.md` | US-4.5.5 vinculada a RF-NT-01 |

---

## Decisiones de Diseño

### 1. Callback in-process configurado desde composition root

`registro/api/router.py` solo conoce `Callable[[Inscripcion], Awaitable[None]]`. El
adapter concreto vive en `src/app.py`, donde sí corresponde coordinar repositorios de
distintos BCs y políticas de notificación.

### 2. Enriquecimiento fuera de Registro

`Inscripcion` no contiene email, nombre de torneo ni sede. Esos datos se consultan desde:

- `SQLiteAtletaRepository.find_by_id(inscripcion.atleta_id)`;
- `SQLiteTorneoRepository.find_by_id(inscripcion.torneo_id)`.

Si alguno no existe, el callback retorna sin lanzar excepción.

### 3. Idempotencia por inscripción

El `InscripcionConfirmada.id` se construye con `str(inscripcion.inscripcion_id)`. P-10
usa ese valor como `evento_fuente_id`, preservando la regla exactly-once ya implementada
en `US-4.5.1`.

---

## Validación Ejecutada

### Unitarios

```bash
uv run pytest tests/unit/registro/test_inscribir_atleta_handler.py \
  tests/unit/test_app_p10_wiring.py -q
```

Resultado:

```text
11 passed, 8 warnings in 9.05s
```

### Integración HTTP

```bash
uv run pytest tests/integration/registro/test_p10_endpoint_wiring.py -q
```

Resultado:

```text
2 passed, 3 warnings in 2.32s
```

### BDD

```bash
uv run pytest tests/features/steps/cablear_p10_inscripcion_steps.py -q
```

Resultado:

```text
4 passed, 1 warning in 3.00s
```

### Regresión P-10

```bash
uv run pytest tests/unit/notificaciones/application/test_politica_p10.py \
  tests/integration/notificaciones/test_politica_p10_integration.py -q
```

Resultado:

```text
8 passed in 0.56s
```

### CodeGuard

```bash
.venv/bin/codeguard -c pyproject.toml -f json \
  src/app.py \
  src/registro/api/router.py \
  src/registro/application/commands/inscribir_atleta.py \
  > quality/reports/codeguard/US-4.5.5-quality.json
```

Resultado:

```text
0 errors
0 warnings
9 infos
```

---

## Estado Respecto de la Spec

### Cumplido

- `POST /registro/inscripciones` dispara P-10 automáticamente.
- El email se envía al atleta usando datos reales de Registro y Torneo.
- El event store de Notificaciones registra `NotificacionEnviada`.
- Reprocesar la misma inscripción no duplica emails.
- Atleta o torneo ausente no interrumpe el flujo principal.
- `registro` no importa `notificaciones`.

### Alcance deliberado

- No se introdujo event bus genérico.
- No se cambió el modelo de dominio de `registro`.
- No se ejecutó smoke real contra Resend; las validaciones automatizadas usan fake email.

---

## Riesgos y Próximos Pasos

- El callback queda configurado como estado de módulo en el router, por consistencia con
  la composición actual de FastAPI. Los tests lo resetean explícitamente.
- El envío real depende de `RESEND_API_KEY` y `NOTIFICACIONES_EMAIL_FROM`.
- RF-NT-01 sigue parcialmente completo: email queda cubierto para P-10/P-11; push sigue
  pendiente fuera de INC-4.5.
