# Reporte Final — US-5.1.4

**US:** Generacion y ajuste de grilla desde la UI del organizador
**Producto:** frontend + `competencia/api`
**Branch:** `feature/US-5.1.4-grilla-ui`

## Implementacion

- Se agrego `POST /competencia/{competencia_id}/generar-grilla` para exponer
  `GenerarGrillaCommand` con `ot_inicio` y `andariveles`.
- Se extendio `frontend/src/api/competencia.ts` con crear competencia, generar grilla,
  ajustar grilla y confirmar grilla.
- Se agrego el tab funcional `Grilla` en `DetalleTorneoPage`.
- Se crearon `ConfigurarGrillaForm`, `TablaGrilla` y `GrillaPanel`.
- La tabla permite reordenar posiciones con Drag and Drop HTML nativo y persiste cambios
  en un unico `POST ajustar-grilla`.
- La confirmacion deja la grilla en modo solo lectura y oculta la accion de confirmar.

## Artefactos

- Feature BDD: `tests/features/US-5.1.4-generacion-ajuste-grilla.feature`
- Plan: `docs/plans/sp5/US-5.1.4-plan.md`
- Fase 0: `docs/plans/sp5/US-5.1.4-fase0.md`
- Notas: `docs/plans/sp5/US-5.1.4-implementation-notes.md`
- BDD validation: `docs/reports/US-5.1.4-bdd-validation.md`
- Quality report: `quality/reports/codeguard/US-5.1.4-quality.json`

## Validacion

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
- `python3 -m py_compile src/competencia/api/router.py tests/unit/competencia/api/test_generar_grilla_endpoint.py tests/integration/competencia/test_generar_grilla_api.py`: aprobado.
- `npm run lint`: falla por `frontend/.vite/deps/react-router-dom.js`, archivo generado preexistente.
- `pytest tests/unit/competencia/api/test_generar_grilla_endpoint.py`: bloqueado por `ModuleNotFoundError: aiosqlite`.
- `pytest tests/integration/competencia/test_generar_grilla_api.py`: bloqueado por `ModuleNotFoundError: aiosqlite`.

## Tests agregados

- `tests/unit/competencia/api/test_generar_grilla_endpoint.py`
- `tests/integration/competencia/test_generar_grilla_api.py`

## Decisiones

- Se aprobo agregar endpoint backend minimo para satisfacer el criterio de primer OT.
- No se agrego `@dnd-kit/core`; se uso Drag and Drop nativo para evitar cambiar dependencias.
- La validacion BDD UI queda documental/manual por ausencia de harness browser automatizado.

## Estado

Implementacion completa con gates disponibles aprobados. Tests Python pendientes de ejecutar
cuando el entorno tenga `aiosqlite` instalado.

*Generado en Fase 9 de /implement-us US-5.1.4*
