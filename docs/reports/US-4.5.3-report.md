# Reporte de Implementación — US-4.5.3
## Política P-10 — email de confirmación de inscripción

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.5  
**Branch:** `feature/US-4.5.3-politica-p10`  
**Fecha:** 2026-04-15  
**Estado:** Completado

---

## Resumen

Se implementó la política P-10 del BC `notificaciones`: ante un evento de aplicación
`InscripcionConfirmada`, el sistema solicita y envía una notificación por email al
atleta, registrando el ciclo de vida completo en el event store de Notificaciones.

La implementación reutiliza el aggregate `Notificacion`, el repositorio/event store de
`US-4.5.1` y el `EmailPort`/`ResendEmailAdapter` de `US-4.5.2`.

---

## Componentes Implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/notificaciones/application/commands/solicitar_envio.py` | Command + handler para crear `NotificacionSolicitada` con idempotencia por `evento_fuente_id` |
| `src/notificaciones/application/commands/enviar_notificacion.py` | Command + handler para llamar `EmailPort` y registrar `NotificacionEnviada` o `NotificacionFallida` |
| `src/notificaciones/application/policies/politica_p10.py` | DTO `InscripcionConfirmada` y `PoliticaP10Handler` |
| `src/notificaciones/infrastructure/templates/inscripcion_confirmada_template.py` | Template de asunto/cuerpo para confirmación de inscripción |
| `src/notificaciones/domain/aggregates/notificacion.py` | Soporte para registrar fallos de solicitud tempranos, como `destinatario_sin_email` |
| `src/app.py` | Factory `build_p10_handler()` con repositorio SQLite, Resend y template real |
| `src/registro/application/commands/inscribir_atleta.py` | Callback opcional post-save para integración in-process sin acoplar BCs |

### Tests y BDD

| Archivo | Cobertura |
|---------|-----------|
| `tests/features/US-4.5.3-politica-p10.feature` | Escenarios BDD aprobados para P-10 |
| `tests/features/steps/politica_p10_steps.py` | Automatización BDD con SQLite temporal y fake email |
| `tests/unit/notificaciones/application/test_solicitar_envio_handler.py` | Solicitud e idempotencia por éxito previo |
| `tests/unit/notificaciones/application/test_enviar_notificacion_handler.py` | Envío exitoso y fallo técnico del proveedor |
| `tests/unit/notificaciones/application/test_politica_p10.py` | Orquestación P-10, idempotencia, email ausente y fallo del proveedor |
| `tests/unit/notificaciones/infrastructure/test_inscripcion_confirmada_template.py` | Datos requeridos en asunto y cuerpo |
| `tests/integration/notificaciones/test_politica_p10_integration.py` | Persistencia real en SQLite e idempotencia end-to-end |

### Documentación

| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp4/US-4.5.3-plan.md` | Plan y checklist actualizado |
| `docs/architecture/15-bc-notificaciones.md` | Estado real del BC con P-10 y wiring in-process |
| `docs/design/domain-model.md` | Application layer de Notificaciones actualizada |
| `docs/traceability/matrix.md` | RF-NT-01 actualizado con P-10 implementada |

---

## Decisiones de Diseño

### 1. DTO propio en `notificaciones`

`PoliticaP10Handler` recibe `InscripcionConfirmada` como DTO de aplicación del BC
Notificaciones. Esto evita imports desde `registro` y respeta la regla BC-first:
la traducción desde el productor queda en el composition root o en un ACL futuro.

### 2. Integración in-process para SP4

No se introdujo un event bus genérico. Se agregó `build_p10_handler()` en `src/app.py`
como punto de composición con infraestructura real. El handler de inscripción acepta
un callback opcional post-save, sin revertir la inscripción si Notificaciones falla.

### 3. Fallo temprano sin email

Como `Destinatario` valida formato de email, el caso `atleta_email` ausente no puede
pasar por el flujo normal de `SolicitarEnvio`. Se agregó
`Notificacion.registrar_fallo_de_solicitud()` para persistir `NotificacionFallida`
con motivo `destinatario_sin_email`.

---

## Validación Ejecutada

### Tests focalizados completos

```bash
uv run pytest tests/unit/notificaciones \
  tests/integration/notificaciones \
  tests/features/steps/notificacion_idempotencia_steps.py \
  tests/features/steps/adaptador_email_steps.py \
  tests/features/steps/politica_p10_steps.py \
  tests/unit/registro/test_inscribir_atleta_handler.py -q
```

Resultado:

```text
51 passed, 3 warnings in 2.05s
```

Las advertencias provienen de `datetime.utcnow()` en tests existentes de `registro`;
no fueron introducidas por esta US.

### BDD focalizado

```bash
uv run pytest tests/features/steps/politica_p10_steps.py -q
```

Resultado:

```text
5 passed in 0.36s
```

### Integración focalizada

```bash
uv run pytest tests/integration/notificaciones/test_politica_p10_integration.py -q
```

Resultado:

```text
4 passed in 0.34s
```

### CodeGuard

```bash
uv run codeguard src/notificaciones --format json \
  > quality/reports/codeguard/US-4.5.3-quality.json
```

Resultado:

```text
0 errors
0 warnings
105 infos
```

---

## Estado Respecto de la Spec

### Cumplido

- Email enviado exitosamente al confirmar inscripción.
- Idempotencia: reprocesar el mismo `evento_fuente_id` no envía un segundo email.
- Atleta sin email genera `NotificacionFallida` con motivo `destinatario_sin_email`.
- Fallo técnico del proveedor queda registrado como `NotificacionFallida`.
- La inscripción no se revierte por fallos de Notificaciones.
- El email contiene atleta, torneo, fecha, sede y disciplinas.

### Alcance deliberado

- No se creó un bus de eventos genérico.
- No se implementó enriquecimiento automático desde `registro` para obtener email,
  nombre del atleta y datos del torneo. La política queda implementada contra el DTO
  completo esperado por la spec.

---

## Riesgos y Próximos Pasos

- `US-4.5.4` debe reutilizar el patrón de `SolicitarEnvioHandler` +
  `EnviarNotificacionHandler` para `ResultadosPublicados`.
- Para conectar P-10 a endpoints reales de inscripción, falta definir cómo se enriquece
  `InscripcionConfirmada` con datos de atleta y torneo sin acoplar BCs.
- Push sigue fuera de scope de SP4; RF-NT-01 queda parcialmente implementado por email.
