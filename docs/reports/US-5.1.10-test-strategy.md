# Estrategia de Tests - US-5.1.10

## Alcance

US-5.1.10 normaliza el campo `estado` recibido por `fetchTorneo` y `fetchTorneos`
para que `AccionesPanel` opere siempre con claves canonicas de `EstadoTorneo`.

## Unit tests

**Estado:** waiver.

El frontend no tiene harness de tests unitarios configurado para TypeScript/React
(Vitest/Jest). La validacion automatizada disponible es TypeScript y ESLint.

## Validacion aplicada

- TypeScript via `npm run build`.
- ESLint via `npm run lint`.
- Feature BDD materializado en `tests/features/US-5.1.10-acciones-fase.feature`.

## Riesgo residual

No hay test unitario automatizado de `normalizarEstadoTorneo`. La regla queda cubierta
por compilacion, lint y revision manual contra la spec.
