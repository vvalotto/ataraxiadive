# Fases 4-6 — US-4.4.2
## Estrategia de tests y validación

`US-4.4.2` extiende comportamiento frontend offline sin harness e2e/browser automático en el repositorio.

Cobertura aplicada:

- `npm run lint`
- `npm run build`
- contrato BDD en `.feature` para validación manual.

Smoke manual requerido:

- flujo offline: llamar/resultado/tarjeta;
- DNS offline;
- visualización de pendientes en grilla.

