# Fases 4-6 — US-4.3.1
## Estrategia de tests y validacion para frontend

`US-4.3.1` implementa una pantalla React/Vite en un repo que hoy no tiene harness
automatizado de unit tests o browser tests para frontend.

Por ese motivo:

- **Fase 4 (tests unitarios):** no se agregan suites nuevas; la logica introducida
  queda validada por TypeScript estricto, `npm run build` y `eslint`.
- **Fase 5 (tests de integracion):** no se agregan tests automáticos de navegador;
  la integracion real queda diferida a validacion manual con backend corriendo.
- **Fase 6 (validacion BDD):** los escenarios del `.feature` se conservan como
  contrato de aceptacion y su ejecucion es manual en esta US.

Cobertura sustitutiva aplicada:

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- revision manual pendiente de:
  - torneo activo
  - disciplinas asignadas
  - estado ACTIVA/PENDIENTE
  - navegacion a `/juez/grilla`

Esto mantiene la secuencia del pipeline sin fingir suites automatizadas que el
repositorio aun no tiene.
