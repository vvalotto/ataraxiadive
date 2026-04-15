# Plan de Implementación: US-4.5.4 - Política P-11 resultados publicados

**Sprint:** SP4 - La Plataforma  
**Incremento:** INC-4.5  
**Bounded Context:** `notificaciones`  
**Patrón:** Hexagonal DDD BC-first + política de aplicación in-process  
**Estimación total:** 3h 25min  
**Estado:** Fase 3 implementada; tests pendientes  
**Fecha:** 2026-04-15

## Objetivo

Implementar la política P-11 para que un evento `ResultadosPublicados` dispare un email
individual a cada atleta de la disciplina publicada, con posición, RP, tarjeta y podio.

La política debe ser idempotente por par `(evento_publicacion, atleta_id)` mediante una
clave compuesta `"{evento.id}:{atleta_id}"`, evitando que el primer envío bloquee a los
demás atletas del mismo evento.

## Decisiones de Diseño

- `ResultadosPublicados` será un DTO de aplicación de `notificaciones`, no un import desde
  `resultados`.
- Se reutilizan `SolicitarEnvioHandler` y `EnviarNotificacionHandler` de `US-4.5.3`.
- `PoliticaP11Handler` procesa atletas en forma independiente: un fallo no corta el resto.
- Para atletas sin email, se registra `NotificacionFallida` con motivo
  `destinatario_sin_email`, usando el soporte agregado en `US-4.5.3`.
- No se introduce queue, rate limiting ni event bus genérico en SP4.
- Atletas con `estado = "Retirado"` se omiten; atletas con `estado = "DNS"` se notifican.

## Componentes a Implementar

### 1. Application - política P-11

- [x] `src/notificaciones/application/policies/politica_p11.py` (45 min)
  - DTO `ResultadoPublicadoAtleta`
  - DTO `PodioPublicado`
  - DTO `ResultadosPublicados`
  - `ResultadosPublicadosTemplatePort`
  - `PoliticaP11Handler`
  - clave compuesta `"{evento.id}:{resultado.atleta_id}"`
  - omitir `estado == "Retirado"`
  - registrar fallo por email ausente sin interrumpir la iteración
  - continuar ante fallos técnicos por atleta

- [x] `src/notificaciones/application/policies/__init__.py` (5 min)
  - exportar P-11 junto con P-10

### 2. Infrastructure - template de resultados

- [x] `src/notificaciones/infrastructure/templates/resultados_publicados_template.py` (30 min)
  - asunto `Resultados publicados - {disciplina} - {torneo_nombre}`
  - cuerpo con atleta, disciplina, torneo, posición, RP, tarjeta y podio
  - incluir URL de ranking si `torneo_id` está disponible
  - representar DNS sin transformarlo

- [x] `src/notificaciones/infrastructure/templates/__init__.py` (5 min)
  - export público del template

### 3. Wiring de aplicación

- [x] `src/app.py` (15 min)
  - factory `build_p11_handler()`
  - usar repositorio SQLite, `ResendEmailAdapter` y template real
  - mantener P-11 preparado para integración in-process futura desde `resultados`

## Tests

### 4. Unitarios

- [x] `tests/unit/notificaciones/application/test_politica_p11.py` (40 min)
  - envía un email por atleta
  - idempotencia por atleta
  - atleta sin email no interrumpe los demás
  - fallo de proveedor en un atleta continúa con los demás
  - atleta retirado no se notifica
  - atleta DNS sí se notifica

- [x] `tests/unit/notificaciones/infrastructure/test_resultados_publicados_template.py` (20 min)
  - asunto correcto
  - cuerpo contiene posición, RP, tarjeta y podio
  - cuerpo conserva DNS

### 5. Integración

- [x] `tests/integration/notificaciones/test_politica_p11_integration.py` (35 min)
  - SQLite real del BC Notificaciones
  - fake `EmailPort`
  - tres atletas exitosos -> tres `NotificacionEnviada`
  - reproceso del mismo evento no duplica
  - fallo por email ausente persiste `NotificacionFallida`

### 6. BDD

- [x] `tests/features/steps/politica_p11_steps.py` (40 min)
  - automatizar `tests/features/US-4.5.4-politica-p11.feature`
  - usar SQLite temporal y fake email adapter

- [x] Ejecutar validación BDD focalizada (5 min)
  - `uv run pytest tests/features/steps/politica_p11_steps.py -q`

## Validación y Quality Gates

- [x] Ejecutar suite focalizada de notificaciones (10 min)
  - unitarios, integración y BDD de `notificaciones`
  - BDD previos de `US-4.5.1`, `US-4.5.2`, `US-4.5.3`

- [x] Ejecutar CodeGuard sobre `src/notificaciones` (5 min)
  - guardar reporte en `quality/reports/codeguard/US-4.5.4-quality.json`

## Documentación y Reporte

- [x] Actualizar `docs/architecture/15-bc-notificaciones.md` (10 min)
  - documentar P-11 y clave compuesta por atleta

- [x] Actualizar `docs/design/domain-model.md` (10 min)
  - reflejar `PoliticaP11Handler` y `ResultadosPublicadosTemplate`

- [x] Actualizar `docs/traceability/matrix.md` (10 min)
  - marcar RF-NT-04 como implementado

- [x] Crear `docs/reports/US-4.5.4-report.md` (10 min)
  - resumen de implementación
  - validaciones ejecutadas
  - decisiones y riesgos

## Riesgos

- `ResultadosPublicados` no existe aún como evento real en `resultados`; la política se
  implementa contra DTO propio del BC Notificaciones.
- Si un evento tiene muchos atletas, el procesamiento sigue siendo secuencial en SP4.
  Rate limiting/background workers quedan para SP5.
- El contenido del email usa strings ya formateados (`rp`, `tarjeta`) para evitar que
  Notificaciones conozca reglas internas de `resultados`.

## Criterio de Cierre

- Feature BDD automatizada y en verde.
- Se envía un email por atleta notificable.
- Reprocesar el mismo `ResultadosPublicados` no duplica emails.
- Email ausente y fallos técnicos quedan registrados sin bloquear a otros atletas.
- Atletas DNS reciben email; atletas retirados se omiten.
- Tests unitarios, integración y quality gate focalizado pasan.
- Documentación y reporte final existen en disco antes del cierre del tracker.
