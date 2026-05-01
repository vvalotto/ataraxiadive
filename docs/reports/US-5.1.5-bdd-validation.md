# Validacion BDD — US-5.1.5

**Feature:** `tests/features/US-5.1.5-asignacion-jueces.feature`

## Resultado

- Escenarios BDD creados en lenguaje de negocio.
- La US pertenece a frontend React/Vite con interacciones de selector en UI.
- El repositorio no tiene harness automatizado de browser para ejecutar el tab `Jueces`.
- La validacion automatizada se cubre con:
  - `npm run build`.
  - `npx eslint src vite.config.ts`.
  - `python3 -m py_compile` para backend y tests nuevos.

## Estado

Validacion BDD documental/manual pendiente de UAT visual.
