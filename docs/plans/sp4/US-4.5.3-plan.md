# Plan de Implementación: US-4.5.3 - Política P-10 email de confirmación

**Sprint:** SP4 - La Plataforma  
**Incremento:** INC-4.5  
**Bounded Context:** `notificaciones`  
**Patrón:** Hexagonal DDD BC-first + política de aplicación in-process  
**Estimación total:** 3h 10min  
**Estado:** Fase 3 implementada; tests pendientes  
**Fecha:** 2026-04-15

## Objetivo

Implementar la política P-10 para que un evento de inscripción confirmada dispare una
notificación por email al atleta, reutilizando el aggregate `Notificacion`, el event store
propio del BC y el `EmailPort` implementado en `US-4.5.1`/`US-4.5.2`.

La política debe ser idempotente: procesar dos veces el mismo `evento_fuente_id` no debe
enviar dos emails ni duplicar `NotificacionEnviada`.

## Decisiones de Diseño

- La política vivirá en `src/notificaciones/application/policies/`.
- `notificaciones` no importará tipos de `registro`; recibirá un DTO/evento de aplicación
  propio llamado `InscripcionConfirmada`.
- La conexión con `registro` quedará en `src/app.py` mediante wiring/callback in-process,
  siguiendo el estilo existente de P-08/P-09.
- No se introduce un event bus genérico en esta US. SP4 necesita una integración
  in-process verificable; una mensajería externa queda diferida a SP5.
- Para `atleta_email` ausente o vacío, la política creará una notificación fallida con
  motivo `destinatario_sin_email` sin llamar al proveedor.
- Los comandos de aplicación serán pequeños y testeables:
  `SolicitarEnvioHandler` crea/persiste `NotificacionSolicitada`;
  `EnviarNotificacionHandler` llama `EmailPort` y persiste `NotificacionEnviada` o
  `NotificacionFallida`.

## Componentes a Implementar

### 1. Application - comandos de notificaciones

- [x] `src/notificaciones/application/commands/solicitar_envio.py` (25 min)
  - `SolicitarEnvioCommand`
  - `SolicitarEnvioHandler`
  - consulta `exists_success_by_evento_fuente_id`
  - persiste eventos pendientes del aggregate
  - retorna `notificacion_id | None` para cubrir idempotencia

- [x] `src/notificaciones/application/commands/enviar_notificacion.py` (30 min)
  - `EnviarNotificacionCommand`
  - `EnviarNotificacionHandler`
  - rehidrata desde `NotificacionRepository.load`
  - llama `EmailPort.enviar`
  - registra éxito con `provider_id`
  - registra fallo técnico sin propagar excepción
  - persiste eventos pendientes

- [x] `src/notificaciones/application/commands/__init__.py` (5 min)
  - exportar comandos y handlers públicos del BC

### 2. Application - política P-10

- [x] `src/notificaciones/application/policies/politica_p10.py` (35 min)
  - DTO `InscripcionConfirmada`
  - `PoliticaP10Handler`
  - render de template
  - orquestación `SolicitarEnvio` -> `EnviarNotificacion`
  - manejo `destinatario_sin_email`

- [x] `src/notificaciones/application/policies/__init__.py` (5 min)
  - export público de la política

### 3. Infrastructure - template de email

- [x] `src/notificaciones/infrastructure/templates/inscripcion_confirmada_template.py` (20 min)
  - `InscripcionConfirmadaTemplate.render(evento)`
  - asunto `Inscripcion confirmada - {torneo_nombre}`
  - cuerpo texto con atleta, torneo, fecha, sede y disciplinas
  - HTML opcional si conviene mantener consistencia con `ContenidoEmail`

- [x] `src/notificaciones/infrastructure/templates/__init__.py` (5 min)
  - export público del template

### 4. Wiring de aplicación

- [x] `src/app.py` (25 min)
  - factory/helper de composición para P-10
  - usar `SQLiteNotificacionRepository`, `SQLiteNotificacionEventStore` y `ResendEmailAdapter`
  - dejar punto de integración preparado para callback desde `registro`

- [x] `src/registro/application/commands/inscribir_atleta.py` (20 min)
  - incorporar callback opcional post-save, sin importar `notificaciones`
  - no revertir inscripción si el callback falla
  - mantener compatibilidad con tests existentes

## Tests

### 5. Unitarios

- [x] `tests/unit/notificaciones/application/test_solicitar_envio_handler.py` (20 min)
  - crea notificación cuando no hay envío exitoso previo
  - no crea ni persiste cuando existe éxito previo

- [x] `tests/unit/notificaciones/application/test_enviar_notificacion_handler.py` (25 min)
  - registra `NotificacionEnviada` con proveedor exitoso
  - registra `NotificacionFallida` ante error del `EmailPort`

- [x] `tests/unit/notificaciones/application/test_politica_p10.py` (30 min)
  - éxito nominal
  - idempotencia
  - atleta sin email
  - fallo del proveedor sin excepción hacia el flujo principal

- [x] `tests/unit/notificaciones/infrastructure/test_inscripcion_confirmada_template.py` (15 min)
  - asunto correcto
  - cuerpo contiene atleta, torneo, fecha, sede y disciplinas

- [x] Ajustar tests de `registro` si el constructor del handler cambia (10 min)
  - validar compatibilidad del callback opcional

### 6. Integración

- [x] `tests/integration/notificaciones/test_politica_p10_integration.py` (30 min)
  - repositorio SQLite real
  - fake `EmailPort`
  - persistencia de `NotificacionSolicitada` + `NotificacionEnviada/Fallida`
  - idempotencia real por `evento_fuente_id`

### 7. BDD

- [x] `tests/features/steps/politica_p10_steps.py` (30 min)
  - automatizar `tests/features/US-4.5.3-politica-p10.feature`
  - usar SQLite temporal y fake email adapter

- [x] Ejecutar validación BDD focalizada (5 min)
  - `uv run pytest tests/features/steps/politica_p10_steps.py -q`

## Validación y Quality Gates

- [x] Ejecutar suite focalizada de notificaciones (10 min)
  - unitarios de application/domain/infrastructure afectados
  - integración de `notificaciones`
  - BDD de `US-4.5.3`

- [x] Ejecutar regresión mínima de `registro` (5 min)
  - `uv run pytest tests/unit/registro/test_inscribir_atleta_handler.py -q`

- [x] Ejecutar CodeGuard sobre `src/notificaciones` (5 min)
  - guardar reporte en `quality/reports/codeguard/US-4.5.3-quality.json`

## Documentación y Reporte

- [x] Actualizar `docs/architecture/15-bc-notificaciones.md` (10 min)
  - documentar P-10 y su wiring in-process

- [x] Actualizar `docs/design/domain-model.md` (10 min)
  - reflejar command handlers y política P-10

- [x] Actualizar `docs/traceability/matrix.md` si cambia estado RF-NT-01/RF-NT-02 (10 min)

- [x] Crear `docs/reports/US-4.5.3-report.md` (10 min)
  - resumen de implementación
  - validaciones ejecutadas
  - decisiones y riesgos

## Riesgos

- `registro` no tiene todavía un evento de dominio persistido `InscripcionConfirmada`.
  La integración debe quedar como callback in-process para no sobredimensionar esta US.
- `InscripcionConfirmada` necesita datos que `InscribirAtletaCommand` no recibe hoy
  (`atleta_email`, `atleta_nombre`, `torneo_nombre`, `torneo_fecha`, `torneo_sede`).
  La política se implementará contra su DTO; el wiring real puede requerir un ACL o
  enriquecimiento en una US posterior si el endpoint actual no entrega esos datos.
- El motivo `destinatario_sin_email` requiere crear y persistir una notificación fallida
  sin construir `Destinatario` inválido.

## Criterio de Cierre

- Feature BDD automatizada y en verde.
- La política P-10 envía un email cuando el evento contiene datos válidos.
- Reprocesar el mismo `evento_fuente_id` no envía un segundo email.
- Email ausente y fallo técnico quedan registrados como `NotificacionFallida`.
- Tests unitarios, integración y quality gate focalizado pasan.
- Documentación y reporte final existen en disco antes del cierre del tracker.
