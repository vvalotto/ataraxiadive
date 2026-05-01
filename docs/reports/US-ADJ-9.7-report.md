# Reporte de Implementacion - US-ADJ-9.7

## Resumen

- **US:** `US-ADJ-9.7`
- **Titulo:** Declarar AP durante inscripción como precondición de preparación
- **Branch de trabajo:** `feature-US-ADJ-9.7-declarar-ap`
- **Estado:** Implementada

## Alcance implementado

- AP persistido en `registro` por inscripción y disciplina.
- Endpoint de lectura/escritura de AP sobre inscripción.
- Validación de cierre de inscripción bloqueada cuando faltan AP.
- Generación de grilla alimentada desde AP declarados en inscripción.
- Compatibilidad transitoria con el endpoint legado de AP en `competencia`.
- Ajustes de UI en portal atleta e `Inscriptos` del organizador.

## Archivos principales tocados

- `src/registro/api/router.py`
- `src/registro/domain/aggregates/inscripcion.py`
- `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
- `src/torneo/application/commands/transicionar_torneo.py`
- `src/torneo/api/router.py`
- `src/competencia/application/commands/generar_grilla.py`
- `src/competencia/infrastructure/repositories/performances_ap_adapter.py`
- `src/app.py`
- `frontend/src/api/registro.ts`
- `frontend/src/components/organizador/InscriptosPanel.tsx`
- `frontend/src/components/organizador/TablaInscriptos.tsx`
- `frontend/src/pages/atleta/AtletaDeclararAPPage.tsx`

## Evidencia de validacion

### Python

```bash
./.venv/bin/python -m pytest \
  tests/integration/registro/test_inscriptos_detalle_endpoint.py \
  tests/integration/torneo/test_cierre_inscripcion_precondition.py \
  tests/unit/torneo/application/test_transiciones_handlers.py \
  tests/unit/competencia/application/test_generar_grilla_handler.py
```

Resultado: `22 passed`

### Frontend

```bash
npm run build
npm run lint
```

Resultado: ambos comandos completados exitosamente.

## Artefactos de workflow generados

- `docs/plans/sp-adj-09/US-ADJ-9.7-fase0.md`
- `tests/features/US-ADJ-9.7-ap-inscripcion-preparacion.feature`
- `docs/plans/sp-adj-09/US-ADJ-9.7-plan.md`
- `docs/plans/sp-adj-09/US-ADJ-9.7-implementation-notes.md`

## Observaciones

- El spec `docs/specs/sp-adj-09/US-ADJ-9.7.md` quedó incluido en la branch de trabajo.
- La transición preserva compatibilidad operativa para flujos que todavía registran AP en `competencia`.
