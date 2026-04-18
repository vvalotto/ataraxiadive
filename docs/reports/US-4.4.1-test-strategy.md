# Fases 4-6 — US-4.4.1
## Estrategia de tests y validación para frontend offline

`US-4.4.1` implementa comportamiento offline en React usando IndexedDB. El repositorio
actual no incluye harness automatizado de browser/e2e para validar escenarios de red
online-offline desde CI.

Por ese motivo:

- **Fase 4 (tests unitarios):** no se agregan suites nuevas; se valida tipado y coherencia
  con `eslint` + `tsc` vía `npm run lint` y `npm run build`.
- **Fase 5 (tests de integración):** sin tests automáticos de navegador en esta US.
- **Fase 6 (validación BDD):** se mantiene archivo `.feature` como contrato de aceptación
  y se define ejecución manual de smoke para escenarios offline.

Cobertura sustitutiva aplicada:

- `npm run lint` en `frontend/`
- `npm run build` en `frontend/`
- smoke manual pendiente:
  - carga online con persistencia en cache;
  - carga offline con cache existente;
  - carga offline sin cache;
  - aviso de cache expirado (>24h).

