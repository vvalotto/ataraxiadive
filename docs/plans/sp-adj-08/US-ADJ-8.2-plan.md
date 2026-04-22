# Plan de Implementacion: US-ADJ-8.2 — Restringir operaciones por torneo y fase

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-08 |
| **Tipo** | Fix de regla funcional frontend + validacion de fase |
| **Branch** | `feature/US-ADJ-8.2-restringir-operaciones` |
| **BC** | frontend organizador + `torneo` + `competencia` via composition root |
| **Estimacion** | 3-4 h |
| **Estado** | Implementada |

---

## Alcance

Implementar dos restricciones operativas detectadas por UAT:

- El selector de grilla debe mostrar solo disciplinas configuradas en el torneo actual.
- La transicion `EJECUCION -> PREMIACION` debe bloquearse mientras existan disciplinas
  del torneo sin competencia finalizada.

Hallazgos cubiertos: `UAT-5.2-02`, `UAT-5.2-05`, `UAT-5.2-07`.

---

## Decisiones de implementacion

- Usar `GET /torneos/{torneo_id}/disciplinas` como fuente primaria del selector de grilla.
- En frontend, cruzar disciplinas configuradas con `GET /competencia?torneo_id=...` y
  `GET /competencia/{id}/estado` para derivar disciplinas pendientes de cierre.
- En backend, no importar `competencia` desde `torneo/domain`.
- Agregar un callback configurable en `torneo.api.router` para validar precondiciones
  de premiacion; cablearlo en `src/app.py` usando adaptadores/queries de `competencia`.
- Si no hay callback configurado, mantener compatibilidad de tests aislados del router.

---

## Tareas

### 1. Frontend — selector de grilla

- [x] Modificar `GrillaPanel` para consultar `listarDisciplinasTorneo(torneoId)`.
- [x] Eliminar lista global hardcodeada como fuente del selector.
- [x] Inicializar/ajustar seleccion cuando carguen las disciplinas del torneo.
- [x] Mostrar estado vacio si el torneo no tiene disciplinas configuradas.
- [x] Evitar crear/generar grilla si no hay disciplina valida seleccionada.

### 2. Frontend — bloqueo de premiacion

- [x] Extender `AccionesPanel` para recibir disciplinas pendientes de cierre.
- [x] En `DetalleTorneoPage`, calcular cierre de torneo desde disciplinas configuradas,
  competencias por torneo y estado de cada competencia.
- [x] Cambiar texto `Iniciar premiacion` por `Pasar a premiacion`.
- [x] Bloquear la accion si hay disciplinas no finalizadas.
- [x] Mostrar motivo con cantidad y nombres de disciplinas pendientes.
- [x] No disparar `iniciarPremiacion` si el bloqueo esta activo.

### 3. Backend — precondicion de premiacion

- [x] Agregar excepcion `PremiacionNoPermitida` en `torneo.domain.exceptions`.
- [x] Registrar handler HTTP 409 para `PremiacionNoPermitida`.
- [x] Agregar callback configurable en `torneo.api.router` antes de `IniciarPremiacionHandler`.
- [x] Cablear callback en `src/app.py`:
  - leer torneo y disciplinas configuradas;
  - listar competencias por torneo;
  - obtener estado de cada competencia;
  - rechazar si alguna disciplina configurada no esta `Finalizada`.
- [x] Incluir disciplinas sin competencia como pendientes.

### 4. Tests

- [x] Unit backend: callback/handler rechaza premiacion con pendientes y permite con todas finalizadas.
- [x] Integracion backend: `PUT /torneos/{id}/iniciar-premiacion` retorna 409 si el callback detecta pendientes.
- [x] Frontend: no hay harness automatizado actual; validar con `npm run build` y `npm run lint`.
- [x] BDD: mantener feature como especificacion ejecutable futura; omitir steps si no hay harness UI para browser.

### 5. Documentacion y reporte

- [x] Actualizar `docs/specs/sp-adj-08/US-ADJ-8.2.md` a `Implementada`.
- [x] Actualizar checklist de `PLAN-SP-ADJ-08`.
- [x] Generar `docs/reports/US-ADJ-8.2-report.md`.

---

## Fases omitidas o acotadas

- Fase 4 queda acotada a tests Python de backend si se toca validacion de fase.
- Fase 5 queda acotada al endpoint de `torneo`; no se crea E2E completo de navegador.
- Fase 6 queda como validacion documental BDD: se crea `.feature`, pero no se implementan
  steps UI por falta de harness browser en el repo.
- Fase 7 usa `npm run build`, `npm run lint` y tests Python focalizados; CodeGuard completo
  puede generar ruido fuera del alcance de esta US.

---

## Validacion minima esperada

```bash
npm run build
npm run lint
pytest tests/unit/torneo/application/test_transiciones_handlers.py
pytest tests/integration/torneo/test_premiacion_precondicion.py
```

---

*Creado: 2026-04-22 — Fase 2 para UAT-5.2 reglas operativas*
