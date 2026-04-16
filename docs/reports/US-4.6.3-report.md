# Reporte de Implementación — US-4.6.3
## UI de auditoría del organizador

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.6  
**Branch:** `feature/US-4.6.3-ui-auditoria`  
**Fecha:** 2026-04-16

---

## Resumen

Se implementó la tercera US de `INC-4.6` en el frontend de organizador: una
navegación de auditoría que permite recorrer torneos, entrar a competencias,
ver la lista de atletas y abrir la traza cronológica de eventos de una
performance puntual.

La solución reutiliza `US-4.6.1` para el audit log puntual, expone el
`hash_sha256` de `US-4.6.2` dentro del read model de estado de competencia y
agrega una UI de solo lectura con acción de copia para el hash cuando la
disciplina ya fue finalizada.

---

## Cambios implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/aggregates/competencia.py` | El aggregate reconstituye y expone `hash_sha256` desde `CompetenciaFinalizada` |
| `src/competencia/application/queries/obtener_estado_competencia.py` | `EstadoCompetenciaDTO` ahora incluye `hash_sha256` |
| `src/competencia/api/router.py` | `GET /competencia/{id}/estado` expone el hash de cierre cuando existe |
| `frontend/src/App.tsx` | Nuevas rutas protegidas de organizador para competencias y auditoría |
| `frontend/src/pages/organizador/*.tsx` | Dashboard navegable, lista de competencias, auditoría de competencia y traza puntual |
| `frontend/src/hooks/useAuditLog.ts` | Nuevo hook para consumir el audit log puntual |
| `frontend/src/hooks/useAuditoriaCompetencia.ts` | Nuevo hook para combinar estado, grilla y ranking |
| `frontend/src/api/resultados.ts` | Nuevo cliente frontend para ranking de competencia |

### Tests y validación

| Archivo / comando | Cobertura |
|-------------------|-----------|
| `tests/unit/competencia/application/queries/test_obtener_estado_competencia.py` | Estado finalizado con `hash_sha256` y backward compatibility sin hash |
| `tests/unit/competencia/domain/test_competencia_finalizar.py` | Persistencia y reconstitución del hash |
| `tests/integration/competencia/test_competencia_finalizada_integration.py` | Payload real de `CompetenciaFinalizada` con hash |
| `npm run build` | Validación de compilación del frontend |
| `npm run lint` | Validación estática del frontend |

### Artefactos de proceso

| Archivo | Propósito |
|---------|-----------|
| `tests/features/US-4.6.3-ui-auditoria-organizador.feature` | Escenarios BDD de la US |
| `docs/plans/sp4/US-4.6.3-plan.md` | Plan aprobado de implementación |
| `docs/reports/US-4.6.3-bdd-waiver.md` | Sustitución explícita de automatización BDD frontend |
| `docs/traceability/matrix.md` | Registro de `US-4.6.3` dentro de `INC-4.6` |
| `quality/reports/codeguard/US-4.6.3-codeguard.json` | Evidencia del quality gate backend focalizado |

---

## Decisiones de diseño

### 1. Extensión mínima del backend en lugar de endpoint nuevo

La UI necesitaba el `hash_sha256` de cierre, pero no existía un endpoint
específico para eso. En vez de abrir una query nueva, se extendió el read model
de `GET /estado`, que ya era la fuente natural del encabezado de competencia.

### 2. La auditoría se apoya en fuentes ya existentes

La lista principal reutiliza `grilla` y `ranking`, mientras que la traza puntual
consume directamente `US-4.6.1`. Esto evitó duplicar endpoints de auditoría
agregada cuando ya había información suficiente en las APIs vigentes.

### 3. Ranking opcional, no dependencia dura

La pantalla no falla si el ranking aún no está disponible. En ese caso, muestra
estado operativo por atleta y usa el ranking solo como enriquecimiento del
“resultado final”.

---

## Validación ejecutada

### Pytest focalizado backend

Comando ejecutado:

```bash
./.venv/bin/pytest \
  tests/unit/competencia/application/queries/test_obtener_estado_competencia.py \
  tests/unit/competencia/domain/test_competencia_finalizar.py \
  tests/integration/competencia/test_competencia_finalizada_integration.py
```

Resultado:

```text
13 passed in 2.58s
```

### Frontend

Comandos ejecutados:

```bash
npm run build
npm run lint
```

Resultado:

```text
build OK
lint OK
```

### CodeGuard focalizado

Comando ejecutado:

```bash
./.venv/bin/codeguard \
  src/competencia/application/queries/obtener_estado_competencia.py \
  src/competencia/api/router.py \
  src/competencia/domain/aggregates/competencia.py \
  tests/unit/competencia/application/queries/test_obtener_estado_competencia.py \
  tests/unit/competencia/domain/test_competencia_finalizar.py \
  tests/integration/competencia/test_competencia_finalizada_integration.py \
  -c pyproject.toml -a pre-commit -t 15 --format json \
  > quality/reports/codeguard/US-4.6.3-codeguard.json
```

Resultado:

```text
0 errors
4 warnings
43 infos
```

Los warnings remanentes corresponden a `assert` en tests, no a código productivo.

---

## Estado respecto de la spec

### Cumplido

- Acceso restringido a rutas de organizador con `RequireRole`
- Lista navegable de torneos y competencias
- Pantalla de auditoría por competencia
- Trazas puntuales en orden cronológico ascendente
- Hash visible solo si la disciplina está finalizada
- Acción de copiar hash con feedback visual
- Juez redirigido fuera de la pantalla de auditoría

### Diferencia menor respecto de la redacción original

- La navegación arranca desde un dashboard de organizador con lista de torneos
  y luego una pantalla de competencias por torneo. Es consistente con el flujo
  propuesto, aunque la primera pantalla original estaba redactada de forma más
  conceptual que implementativa.

---

## Riesgos y próximos pasos

- La lista usa `ranking` como enriquecimiento opcional del resultado final; si
  en el futuro se necesita una vista más rica, puede convenir una query agregada
  específica de auditoría de competencia.
- `US-4.6.4` puede reutilizar esta navegación como punto de entrada para
  exportación por disciplina.
- Falta todavía infraestructura formal de tests frontend; hoy la evidencia se
  apoya en build/lint más validación backend.
