# Reporte Final — US-5.1.5

**US:** Asignacion de jueces a disciplinas desde la UI
**Producto:** frontend + `identidad/api`
**Branch:** `feature/US-5.1.5-asignar-jueces`

## Implementacion

- Se agrego `GET /auth/usuarios?rol=JUEZ` para listar usuarios por rol desde Identidad.
- Se extendio `UsuarioRepositoryPort` y `SQLiteUsuarioRepository` con `list_by_rol`.
- Se agrego `frontend/src/api/identidad.ts`.
- Se extendio `frontend/src/api/torneo.ts` con disciplinas del torneo y asignacion de juez.
- Se crearon `JuezSelector`, `TablaJueces` y `JuecesPanel`.
- Se integro el tab `Jueces` en `DetalleTorneoPage`.

## Artefactos

- Feature BDD: `tests/features/US-5.1.5-asignacion-jueces.feature`
- Plan: `docs/plans/sp5/US-5.1.5-plan.md`
- Fase 0: `docs/plans/sp5/US-5.1.5-fase0.md`
- Notas: `docs/plans/sp5/US-5.1.5-implementation-notes.md`
- BDD validation: `docs/reports/US-5.1.5-bdd-validation.md`
- Quality report: `quality/reports/codeguard/US-5.1.5-quality.json`

## Validacion

- `npm run build`: aprobado.
- `npx eslint src vite.config.ts`: aprobado.
- `python3 -m py_compile src/identidad/api/router.py src/identidad/domain/ports/usuario_repository_port.py src/identidad/infrastructure/repositories/sqlite_usuario_repository.py tests/unit/identidad/api/test_listar_usuarios.py tests/integration/identidad/test_sqlite_usuario_repository.py`: aprobado.
- `pytest tests/unit/identidad/api/test_listar_usuarios.py`: bloqueado por `ModuleNotFoundError: aiosqlite`.
- `pytest tests/integration/identidad/test_sqlite_usuario_repository.py -k list_by_rol`: bloqueado por `ModuleNotFoundError: aiosqlite`.

## Tests agregados

- `tests/unit/identidad/api/test_listar_usuarios.py`
- `tests/integration/identidad/test_sqlite_usuario_repository.py` extendido con `list_by_rol`.

## Decisiones

- Se uso `/auth/usuarios?rol=JUEZ` porque el router real de Identidad vive bajo `/auth`.
- No se agrego ACL cross-BC desde Torneo a Identidad para validar rol del `juez_id`; la UI
  lista solo usuarios JUEZ y Torneo conserva su frontera actual.

## Estado

Implementacion completa con gates disponibles aprobados. Tests Python pendientes de ejecutar
cuando el entorno tenga `aiosqlite` instalado.

*Generado en Fase 9 de /implement-us US-5.1.5*
