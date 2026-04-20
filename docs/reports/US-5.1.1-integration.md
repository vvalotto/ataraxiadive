# US-5.1.1 — Integracion

## Superficie Integrada

- `frontend/src/api/torneo.ts`
  - `crearTorneo()`
  - `asignarDisciplinas()`
  - `fetchTorneo()`
- `frontend/src/pages/organizador/CrearTorneoPage.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- `frontend/src/App.tsx`
- `frontend/src/pages/organizador/DashboardPage.tsx`

## Contratos HTTP Consumidos

- `POST /torneos`
  - Envia bearer token si existe.
  - Envia `nombre`, `descripcion`, fechas, `sede` y `entidad_organizadora`.
  - Espera `{ "torneo_id": "..." }`.
- `PUT /torneos/{torneo_id}/disciplinas`
  - Envia bearer token si existe.
  - Envia `{ "disciplinas": [...] }`.
  - Maneja `409` preservando el formulario y ofreciendo ir al detalle.
- `GET /torneos/{torneo_id}`
  - Carga el detalle minimo post-creacion.

## Validacion Ejecutada

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
- `npm run lint`: falla por archivos generados preexistentes en `frontend/.vite/deps`,
  fuera del codigo fuente de la US.
