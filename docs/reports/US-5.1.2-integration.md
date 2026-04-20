# US-5.1.2 — Integracion

## Superficie Integrada

- `frontend/src/api/torneo.ts`
  - funciones de transicion de fase
- `frontend/src/components/organizador/FaseBadge.tsx`
- `frontend/src/components/organizador/AccionesPanel.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`

## Comportamiento Integrado

- El detalle muestra la fase actual con `FaseBadge`.
- `AccionesPanel` muestra transiciones segun estado actual.
- Cancelacion se confirma mediante dialogo.
- Las transiciones exitosas ejecutan `refetch()` de `GET /torneos/{id}`.
- Los errores backend se muestran inline sin cambiar el estado en pantalla.
- Estados terminales (`CERRADO`, `CANCELADO`) no muestran acciones.

## Validacion Ejecutada

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
