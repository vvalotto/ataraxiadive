# Reporte de Implementación — US-4.6.1
## API de audit log de performance

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.6  
**Branch:** `feature/US-4.6.1-api-audit-log`  
**Fecha:** 2026-04-16

---

## Resumen

Se implementó la primera US de `INC-4.6` en el BC `competencia`: un endpoint de
auditoría por performance que expone la secuencia cronológica de eventos del
event store para un atleta dentro de una competencia puntual.

La solución reutiliza el event store existente como fuente oficial del audit log,
agrega una query dedicada de application y restringe el acceso al endpoint a
usuarios con rol `organizador` o `admin`.

---

## Cambios implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/competencia/application/queries/obtener_audit_log.py` | Nueva query `ObtenerAuditLog` con DTOs `AuditLogDTO` y `AuditLogEventoDTO`, resolución de disciplina desde `stream_id` y excepción `PerformanceNoEncontrada` |
| `src/competencia/api/router.py` | Nuevo endpoint `GET /competencia/{competencia_id}/performances/{atleta_id}/audit-log` con respuesta conforme a la spec y manejo explícito de `404` |
| `src/competencia/api/dependencies.py` | Wiring del nuevo handler reutilizando `AtletaNombreAdapter` |

### Tests

| Archivo | Cobertura |
|---------|-----------|
| `tests/unit/competencia/application/queries/test_obtener_audit_log.py` | Caso nominal, preservación de `sequence`/payload y `404` lógico por ausencia de performance |
| `tests/integration/competencia/test_audit_log_api.py` | `200`, `404`, `403` por rol insuficiente y caso con `ResultadoCorregido` |

### Artefactos de proceso

| Archivo | Propósito |
|---------|-----------|
| `tests/features/US-4.6.1-audit-log-performance.feature` | Escenarios BDD de la US |
| `docs/plans/sp4/US-4.6.1-plan.md` | Plan aprobado de implementación |
| `docs/reports/US-4.6.1-bdd-waiver.md` | Sustitución explícita de automatización BDD por tests unitarios + integración |
| `docs/traceability/matrix.md` | Registro de `US-4.6.1` dentro de `INC-4.6` |
| `quality/reports/codeguard/US-4.6.1-codeguard.json` | Evidencia del quality gate focalizado |

---

## Decisiones de diseño

### 1. Audit log por prefijo de stream, no por tabla adicional

No se creó una tabla de auditoría separada. La query filtra el event store por
prefijo `performance-{competencia_id}-{atleta_id}-` y proyecta la respuesta sobre
el stream encontrado.

Esto mantiene alineación con ADR-001 y evita duplicación de información.

### 2. Nombre real del atleta vía ACL existente

La nueva query reutiliza `AtletaNombreAdapter` para resolver `atleta_nombre` desde
`registro.db`, evitando repetir el fallback sintético de otras queries legacy.

### 3. Seguridad apoyada en `OrganizadorDep`

El endpoint quedó protegido con el mecanismo transversal ya existente en
`identidad.api.dependencies`, sin introducir reglas ad hoc en el router.

---

## Validación ejecutada

### Pytest focalizado

Comando ejecutado:

```bash
./.venv/bin/pytest \
  tests/unit/competencia/application/queries/test_obtener_audit_log.py \
  tests/integration/competencia/test_audit_log_api.py
```

Resultado:

```text
7 passed in 1.53s
```

### CodeGuard focalizado

Comando ejecutado:

```bash
./.venv/bin/codeguard \
  src/competencia/application/queries/obtener_audit_log.py \
  src/competencia/api/router.py \
  src/competencia/api/dependencies.py \
  -c pyproject.toml -a pre-commit -t 15 --format json \
  > quality/reports/codeguard/US-4.6.1-codeguard.json
```

Resultado:

```text
0 errors
0 warnings
9 infos
```

---

## Estado respecto de la spec

### Cumplido

- Endpoint puntual por performance
- Orden cronológico estricto por `sequence`
- Payload con `sequence`, `tipo`, `timestamp`, `datos`
- `404` cuando no existe performance para el atleta indicado
- `403` para rol `juez`
- Inclusión de correcciones históricas (`ResultadoCorregido`) en la traza

### Diferencia menor respecto de la redacción original

- La spec habla de `performances/{atleta_id}`; la implementación resuelve el
  stream real por prefijo porque el identificador técnico del stream también
  incluye `disciplina`. La API pública permanece igual.

---

## Riesgos y próximos pasos

- `US-4.6.2` puede reutilizar la lectura ordenada del event store, pero a nivel
  competencia completa y con serialización canónica para hash.
- `US-4.6.3` ya tiene backend suficiente para la traza puntual; faltará diseñar
  la navegación de organizador y definir de dónde obtiene la lista de atletas.
- El harness BDD HTTP para auditoría/autenticación quedó diferido y conviene
  incorporarlo cuando haya más endpoints de organizador dentro de `INC-4.6`.
