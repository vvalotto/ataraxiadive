# Reporte de Implementación — US-4.5.4
## Política P-11 — emails de resultados publicados

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.5  
**Branch:** `feature/US-4.5.4-politica-p11`  
**Fecha:** 2026-04-15  
**Estado:** Completado

---

## Resumen

Se implementó la política P-11 del BC `notificaciones`: ante un evento de aplicación
`ResultadosPublicados`, el sistema genera una notificación por atleta notificable y
envía un email individual con posición, RP, tarjeta y podio de la disciplina.

La implementación reutiliza los command handlers de `US-4.5.3`:
`SolicitarEnvioHandler` y `EnviarNotificacionHandler`.

La idempotencia se garantiza por atleta mediante clave compuesta:
`"{resultados_publicados.id}:{atleta_id}"`.

---

## Componentes Implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/notificaciones/application/policies/politica_p11.py` | DTOs `ResultadosPublicados`, `ResultadoPublicadoAtleta`, `PodioPublicado` y `PoliticaP11Handler` |
| `src/notificaciones/infrastructure/templates/resultados_publicados_template.py` | Template de email con resultado individual, podio y link al ranking |
| `src/notificaciones/application/policies/__init__.py` | Exports públicos de P-11 |
| `src/notificaciones/infrastructure/templates/__init__.py` | Export de `ResultadosPublicadosTemplate` |
| `src/notificaciones/infrastructure/__init__.py` | Reexport de template de resultados |
| `src/app.py` | Factory `build_p11_handler()` con repositorio SQLite, Resend y template real |

### Tests

| Archivo | Cobertura |
|---------|-----------|
| `tests/features/US-4.5.4-politica-p11.feature` | Escenarios BDD aprobados para P-11 |
| `tests/features/steps/politica_p11_steps.py` | Automatización BDD con SQLite temporal y fake email |
| `tests/unit/notificaciones/application/test_politica_p11.py` | Idempotencia por atleta, email ausente, fallo aislado, retirados y DNS |
| `tests/unit/notificaciones/infrastructure/test_resultados_publicados_template.py` | Contenido del email y preservación de DNS |
| `tests/integration/notificaciones/test_politica_p11_integration.py` | Persistencia real en SQLite e idempotencia end-to-end |

### Documentación

| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp4/US-4.5.4-plan.md` | Plan y checklist actualizado |
| `docs/architecture/15-bc-notificaciones.md` | Estado real del BC con P-11 |
| `docs/design/domain-model.md` | Application layer de Notificaciones actualizada con P-11 |
| `docs/traceability/matrix.md` | RF-NT-04 marcado como implementado |

---

## Decisiones de Diseño

### 1. DTO propio en Notificaciones

`ResultadosPublicados` es un DTO de aplicación del BC `notificaciones`, no un import
desde `resultados`. Esto mantiene la frontera BC-first y permite conectar el evento real
mediante composition root o ACL cuando el productor exista.

### 2. Idempotencia por atleta

La clave `"{evento.id}:{atleta_id}"` evita que el primer email enviado para un evento de
publicación bloquee los emails de los demás atletas.

### 3. Fallos independientes

P-11 procesa cada atleta de forma independiente:

- email ausente -> `NotificacionFallida(destinatario_sin_email)`;
- error técnico del proveedor -> `NotificacionFallida`;
- resto de atletas sigue su flujo normal.

### 4. Reglas de elegibilidad

- Atletas con `estado == "Retirado"` se omiten.
- Atletas con `estado == "DNS"` reciben email, porque DNS es un resultado publicado.

---

## Validación Ejecutada

### Tests focalizados completos

```bash
uv run pytest tests/unit/notificaciones \
  tests/integration/notificaciones \
  tests/features/steps/notificacion_idempotencia_steps.py \
  tests/features/steps/adaptador_email_steps.py \
  tests/features/steps/politica_p10_steps.py \
  tests/features/steps/politica_p11_steps.py -q
```

Resultado:

```text
62 passed in 1.77s
```

### Unitarios P-11

```bash
uv run pytest tests/unit/notificaciones/application/test_politica_p11.py \
  tests/unit/notificaciones/infrastructure/test_resultados_publicados_template.py -q
```

Resultado:

```text
8 passed in 0.32s
```

### Integración P-11

```bash
uv run pytest tests/integration/notificaciones/test_politica_p11_integration.py -q
```

Resultado:

```text
3 passed in 0.43s
```

### BDD P-11

```bash
uv run pytest tests/features/steps/politica_p11_steps.py -q
```

Resultado:

```text
6 passed in 0.55s
```

### CodeGuard

```bash
uv run codeguard src/notificaciones --format json \
  > quality/reports/codeguard/US-4.5.4-quality.json
```

Resultado:

```text
0 errors
0 warnings
111 infos
```

---

## Estado Respecto de la Spec

### Cumplido

- Un email enviado por atleta notificable.
- Email personalizado con posición, RP, tarjeta y podio.
- Idempotencia por par `(evento_publicacion, atleta_id)`.
- Atleta sin email no interrumpe a los demás y queda como `NotificacionFallida`.
- Fallo de proveedor en un atleta no bloquea el resto.
- Atleta con DNS recibe email.
- Atleta retirado se omite.

### Alcance deliberado

- No se implementó un event bus genérico.
- No se conectó contra un evento real de `resultados`, porque `ResultadosPublicados`
  aún no existe como productor en código.
- No se implementó rate limiting ni background worker; queda diferido a SP5 si el volumen
  real lo justifica.

---

## Riesgos y Próximos Pasos

- Cuando `resultados` publique un evento real, hará falta mapearlo al DTO
  `ResultadosPublicados` sin romper fronteras entre BCs.
- RF-NT-01 sigue parcialmente implementado: email cubierto para P-10/P-11, push pendiente.
- Si se dispara P-11 con decenas de atletas, el envío sigue siendo secuencial en SP4.
