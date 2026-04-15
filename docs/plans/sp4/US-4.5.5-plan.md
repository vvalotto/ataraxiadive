# Plan de Implementación: US-4.5.5 - Cablear P-10 al endpoint de inscripción

**Sprint:** SP4 - La Plataforma
**Incremento:** INC-4.5
**Bounded Context:** `registro` productor · `notificaciones` consumidor
**Patrón:** Composition root + callback in-process entre BCs
**Estimación total:** 2h 20min
**Estado:** Plan propuesto; pendiente de aprobación
**Fecha:** 2026-04-15

## Objetivo

Cablear la política P-10 al endpoint HTTP `POST /registro/inscripciones` para que una
inscripción confirmada dispare automáticamente el email de confirmación al atleta.

El endpoint debe seguir perteneciendo al BC `registro`; la política P-10 y sus tipos no
deben importarse desde `registro`. El enriquecimiento `Inscripcion` ->
`InscripcionConfirmada` se hará en `src/app.py`, que actúa como composition root.

## Decisiones de Diseño

- `registro/api/router.py` expondrá un configurador de callback opcional para
  `InscribirAtletaHandler`.
- `registro` no importará `notificaciones`; solo conocerá una función async que recibe
  `Inscripcion`.
- `src/app.py` construirá el callback P-10, buscará los datos faltantes en los
  repositorios SQLite de Registro y Torneo, y llamará a `PoliticaP10Handler`.
- Si el atleta o el torneo no existen al enriquecer el evento, el callback retornará sin
  lanzar excepción.
- La idempotencia queda delegada a P-10 usando `str(inscripcion.inscripcion_id)` como
  `evento_fuente_id`.
- No se introduce event bus, queue ni evento persistido de dominio en esta US.

## Componentes a Implementar

### 1. API Registro - punto de inyección del callback

- [ ] `src/registro/api/router.py` (25 min)
  - importar `Awaitable`, `Callable` e `Inscripcion`
  - agregar variable de módulo `_on_inscripcion_confirmada_callback`
  - agregar `configure_inscripcion_notificaciones(callback | None)`
  - pasar el callback a `InscribirAtletaHandler` en `POST /registro/inscripciones`
  - preservar el contrato actual del endpoint y el status `201`

### 2. Composition root - enriquecimiento y wiring P-10

- [ ] `src/app.py` (35 min)
  - importar el configurador del router de Registro
  - importar `Inscripcion`, `InscripcionConfirmada` y `SQLiteAtletaRepository`
  - agregar `build_on_inscripcion_confirmada_callback(...)`
  - buscar atleta por `inscripcion.atleta_id`
  - buscar torneo por `inscripcion.torneo_id`
  - construir `InscripcionConfirmada` con:
    - `id=str(inscripcion.inscripcion_id)`
    - `atleta_id=str(inscripcion.atleta_id)`
    - email y nombre del atleta desde Registro
    - nombre, fecha y sede del torneo desde Torneo
    - disciplinas desde `inscripcion.disciplinas`
  - configurar el callback al crear la app con `configure_inscripcion_notificaciones(...)`

### 3. Ajustes menores de exports si son necesarios

- [ ] `src/notificaciones/application/policies/__init__.py` o imports directos (5 min)
  - usar el punto de import existente más simple
  - no agregar abstracciones nuevas si los imports directos ya son claros

## Tests

### 4. Unitarios de Registro

- [ ] `tests/unit/registro/test_inscribir_atleta_handler.py` (20 min)
  - verifica que el handler invoca el callback luego de guardar la inscripción
  - verifica que un fallo del callback no revierte ni interrumpe la inscripción

### 5. Unitarios de composition root

- [ ] `tests/unit/test_app_p10_wiring.py` (25 min)
  - callback enriquece `Inscripcion` y llama P-10 con `InscripcionConfirmada`
  - `evento_fuente_id` usa `str(inscripcion.inscripcion_id)`
  - atleta inexistente no lanza y no llama P-10
  - torneo inexistente no lanza y no llama P-10

### 6. Integración HTTP focalizada

- [ ] `tests/integration/registro/test_p10_endpoint_wiring.py` (30 min)
  - configurar repos SQLite temporales de Registro, Torneo y Notificaciones
  - configurar email fake para no llamar a Resend
  - hacer `POST /registro/inscripciones`
  - verificar status `201`
  - verificar email enviado al atleta
  - verificar `NotificacionEnviada` persistida
  - reprocesar mismo `inscripcion_id` a nivel callback y verificar no duplicación

### 7. BDD

- [ ] `tests/features/steps/cablear_p10_inscripcion_steps.py` (25 min)
  - automatizar `tests/features/US-4.5.5-cablear-p10-inscripcion.feature`
  - cubrir envío nominal, idempotencia y fallos silenciosos por atleta/torneo ausente

- [ ] Ejecutar validación BDD focalizada (5 min)
  - `uv run pytest tests/features/steps/cablear_p10_inscripcion_steps.py -q`

## Validación y Quality Gates

- [ ] Ejecutar suite focalizada de Registro y Notificaciones (10 min)
  - `uv run pytest tests/unit/registro/test_inscribir_atleta_handler.py -q`
  - `uv run pytest tests/unit/test_app_p10_wiring.py -q`
  - `uv run pytest tests/integration/registro/test_p10_endpoint_wiring.py -q`
  - `uv run pytest tests/features/steps/cablear_p10_inscripcion_steps.py -q`

- [ ] Ejecutar regresión mínima de P-10 (5 min)
  - `uv run pytest tests/unit/notificaciones/application/test_politica_p10.py -q`
  - `uv run pytest tests/integration/notificaciones/test_politica_p10_integration.py -q`

- [ ] Ejecutar CodeGuard focalizado (5 min)
  - `codeguard src/`
  - guardar reporte en `quality/reports/codeguard/US-4.5.5-quality.json`

## Documentación y Reporte

- [ ] Actualizar `docs/architecture/15-bc-notificaciones.md` (10 min)
  - documentar que P-10 queda cableada desde el endpoint HTTP de Registro

- [ ] Actualizar `docs/design/domain-model.md` si el wiring P-10 no está reflejado (5 min)
  - registrar el callback in-process desde `app.py`

- [ ] Actualizar `docs/traceability/matrix.md` (5 min)
  - vincular US-4.5.5 con el cierre del gap de RF-NT relacionado a P-10

- [ ] Crear `docs/reports/US-4.5.5-report.md` (10 min)
  - resumen de implementación
  - validaciones ejecutadas
  - decisiones y riesgos residuales

## Riesgos

- `app.py` es un módulo global: configurar el callback en import puede afectar tests que
  importen la app completa. Los tests deben resetear o reconfigurar el callback de forma
  explícita cuando usen el router.
- El endpoint actual construye handlers dentro de la función HTTP; el callback debe ser
  una dependencia de módulo simple para no introducir un contenedor nuevo.
- El envío real depende de `RESEND_API_KEY` y `NOTIFICACIONES_EMAIL_FROM`. La validación
  automatizada debe usar email fake; el smoke con Resend real queda fuera del test suite.
- Si el nombre completo del atleta no está normalizado, se usará una composición simple
  `"{nombre} {apellido}".strip()` para el email sin cambiar el modelo de Registro.

## Criterio de Cierre

- Feature BDD automatizada y en verde.
- `POST /registro/inscripciones` dispara P-10 automáticamente cuando los datos existen.
- Reprocesar el mismo `inscripcion_id` no duplica emails ni `NotificacionEnviada`.
- Atleta o torneo ausente no interrumpe la inscripción ni lanza excepción al endpoint.
- `registro` no importa módulos de `notificaciones`.
- Tests focalizados, regresión P-10 y quality gate pasan.
- Documentación y reporte final existen en disco antes del cierre del tracker.
