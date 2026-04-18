# Plan de Implementación: US-4.5.2 - Adaptador email gestionado

**Sprint:** SP4 - La Plataforma
**Incremento:** INC-4.5
**Bounded Context:** `notificaciones`
**Patrón:** Hexagonal DDD BC-first + adaptador de infraestructura HTTP
**Estimación total:** 2h 20min
**Fecha:** 2026-04-14
**Estado:** ✅ COMPLETADO
**Fecha completado:** 2026-04-14

## Objetivo

Implementar un adaptador concreto para `EmailPort` que permita enviar emails reales
mediante un proveedor gestionado, preservando el desacople del dominio y dejando la
integración lista para ser usada por las políticas `US-4.5.3` y `US-4.5.4`.

## Decisiones de diseño

- Se usará `Resend` como proveedor concreto porque expone una API HTTP simple y
  compatible con el stack actual (`httpx`).
- El adaptador vivirá en `src/notificaciones/infrastructure/email/` para mantener la
  frontera de infraestructura explícita.
- La configuración se resolverá por variables de entorno:
  `RESEND_API_KEY`, `NOTIFICACIONES_EMAIL_FROM` y opcionalmente `RESEND_BASE_URL`.
- El contrato de retorno del puerto será el `provider_id` emitido por el proveedor.
- Los errores HTTP o respuestas incompletas del proveedor se traducen a errores
  explícitos del adaptador, sin filtrar detalles de transporte al dominio.

## Componentes a implementar

### 1. Infraestructura - Adaptador email

- [x] `src/notificaciones/infrastructure/email/resend_email_adapter.py` (35 min)
  - implementar `EmailPort`
  - construir payload HTTP `POST /emails`
  - mapear asunto, texto y HTML opcional
  - devolver `provider_id`
  - validar configuración mínima
  - traducir fallos técnicos del proveedor
- [x] `src/notificaciones/infrastructure/email/__init__.py` (5 min)
  - export público del adaptador
- [x] actualizar `src/notificaciones/infrastructure/__init__.py` (5 min)
  - reexport del adaptador principal
- [x] actualizar `pyproject.toml` (5 min)
  - mover `httpx` a dependencia runtime

### 2. Tests unitarios

- [x] `tests/unit/notificaciones/test_resend_email_adapter.py` (25 min)
  - payload correcto
  - HTML opcional
  - error HTTP
  - ausencia de `provider_id`
  - configuración obligatoria

### 3. Tests de integración

- [x] `tests/integration/notificaciones/test_resend_email_adapter.py` (20 min)
  - contrato HTTP básico contra app ASGI simulada
  - validación de header `Authorization`
  - verificación del payload serializado

### 4. BDD y validación

- [x] `tests/features/US-4.5.2-adaptador-email.feature` (10 min)
  - envío exitoso
  - error técnico del proveedor
  - configuración inválida
- [x] `tests/features/steps/adaptador_email_steps.py` (20 min)
  - automatización de escenarios con FastAPI + `ASGITransport`
- [x] ejecutar pytest focalizado y suite de `notificaciones` (10 min)

### 5. Documentación y reporte

- [x] actualizar `docs/architecture/15-bc-notificaciones.md` (10 min)
  - reflejar estado real del BC y el adaptador Resend
- [x] actualizar `docs/design/domain-model.md` (5 min)
  - documentar `EmailPort` y el adaptador concreto actual
- [x] crear `docs/reports/US-4.5.2-report.md` (10 min)

## Métricas de Tiempo

| Fase | Estimado | Real | Varianza |
|------|----------|------|----------|
| Validación de contexto | 10 min | 8 min | -2 min |
| BDD | 15 min | 10 min | -5 min |
| Plan | 15 min | 12 min | -3 min |
| Implementación | 45 min | 38 min | -7 min |
| Tests unitarios | 20 min | 18 min | -2 min |
| Tests de integración | 15 min | 12 min | -3 min |
| Validación BDD | 10 min | 8 min | -2 min |
| Quality gates | 5 min | 4 min | -1 min |
| Documentación | 10 min | 14 min | +4 min |
| Reporte final | 5 min | 6 min | +1 min |
| **Total** | **150 min** | **130 min** | **-20 min** |

## Riesgos vigilados

- Evitar que el dominio conozca detalles HTTP o del proveedor concreto.
- No depender de red real en tests; toda validación queda con `httpx.MockTransport`
  o `httpx.ASGITransport`.
- Mantener el contrato listo para la siguiente US sin introducir handlers de
  aplicación prematuros en `US-4.5.2`.

## Criterio de cierre de la US

- Adaptador concreto de email implementado y exportado
- Configuración obligatoria validada
- Error handling técnico cubierto por tests
- Suite unitaria, integración y BDD en verde
- Artefactos `implement-us` actualizados en disco
