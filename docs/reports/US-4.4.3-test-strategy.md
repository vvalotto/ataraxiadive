# Fases 4-6 — US-4.4.3
## Estrategia de tests y validación

`US-4.4.3` agrega sincronización offline en frontend y trigger de Service Worker.  
El repositorio no tiene harness e2e/browser automatizado para simular reconexión y SW en CI.

Cobertura aplicada:

- `npm run lint`
- `npm run build`
- contrato BDD en `.feature`
- smoke manual de reconexión y estados del badge.

