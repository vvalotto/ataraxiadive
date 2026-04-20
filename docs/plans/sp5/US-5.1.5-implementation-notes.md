# Notas de Implementacion — US-5.1.5

## Backend

Se agrego `GET /auth/usuarios?rol=JUEZ` en `src/identidad/api/router.py`.

La ruta:

- esta protegida por `OrganizadorDep`;
- usa `UsuarioRepositoryPort.list_by_rol`;
- retorna `usuario_id`, `email`, `rol` y `activo`;
- conserva el prefijo `/auth`, que es el prefijo real del router de Identidad.

Se extendio `SQLiteUsuarioRepository` con `list_by_rol(rol)`.

## Frontend

Componentes nuevos:

- `JuezSelector`
- `TablaJueces`
- `JuecesPanel`

API client:

- `frontend/src/api/identidad.ts`: `listarUsuariosPorRol`.
- `frontend/src/api/torneo.ts`: `listarDisciplinasTorneo`, `asignarJuez`.

Integracion:

- `DetalleTorneoPage` ahora renderiza `JuecesPanel` en el tab `Jueces`.

## Validaciones

- `npm run build`: aprobado.
- `npx eslint src vite.config.ts`: aprobado.
- `python3 -m py_compile`: aprobado.
- `pytest`: bloqueado por dependencia faltante `aiosqlite` en el entorno local.

## Decisiones

- La validacion de que el `juez_id` pertenezca a rol JUEZ se resuelve en UI listando
  solo usuarios `JUEZ`. Hacerlo estrictamente en Torneo requeriria ACL/puerto hacia
  Identidad, fuera del alcance de esta US frontend.
