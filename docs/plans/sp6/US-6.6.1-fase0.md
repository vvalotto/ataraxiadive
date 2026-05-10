# US-6.6.1 - Fase 0: Validacion de Contexto

## Historia de Usuario

- **ID:** US-6.6.1
- **Titulo:** Endpoint publico `GET /api/torneos`
- **Producto / BC:** torneo
- **Puntos:** 2
- **Incremento:** INC-6.6 - Portal Publico

## Validacion de Arquitectura

- **Patron:** Hexagonal DDD BC-first.
- **BC verificado:** `src/torneo/`.
- **Capas existentes:** `domain/`, `application/`, `infrastructure/`, `api/`.
- **Documentacion base encontrada:**
  - `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
  - `docs/adr/ADR-006-estructura-bc-first.md`
  - `docs/design/architecture.md`
  - `docs/design/domain-model.md`
  - `docs/contexto/ATARAXIADIVE-CONTEXT.md`

## Validacion Tecnica Inicial

- `src/torneo/api/router.py` expone `@router.get("", response_model=list[TorneoResponse])`.
- `listar_torneos()` no recibe `OrganizadorDep`, `RequireAuth` ni `Depends(get_current_user)`.
- `src/app.py` no define middleware global de autenticacion.
- `TorneoResponse` incluye los campos requeridos por el portal publico:
  `torneo_id`, `nombre`, `descripcion`, `fecha_inicio`, `fecha_fin`, `sede`, `estado`.
- `EstadoTorneo` incluye `CANCELADO`, por lo que el filtro puede implementarse en API sin tocar dominio.

## Quality Gates

- `CLAUDE.md` existe y documenta workflow, arquitectura y quality gates.
- `pyproject.toml` configura pytest, coverage, CodeGuard y DesignReviewer.
- Existen suites `tests/unit/torneo/`, `tests/integration/torneo/` y `tests/features/`.

## Riesgos

- El endpoint existente `GET /torneos` tambien es consumido por frontend organizador. La US acepta mantener el mismo contrato y aplicar filtro de `CANCELADO` en la lista publica.
- La ruta publica real se publica como `/api/torneos` si el entorno monta el backend bajo prefijo `/api`; en FastAPI el router mantiene `prefix="/torneos"`.

## Resultado

Contexto validado. La implementacion puede avanzar con un cambio minimo en API y tests de integracion/BDD enfocados en contrato publico y exclusion de torneos cancelados.
