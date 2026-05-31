---
title: "RF-EJ-05 — No. El juez toma el tiempo manualmente e ingresa el valor."
type: trazabilidad-rf-item
rf_id: RF-EJ-05
area: ejecucion
parent_page: "[[RF-ejecucion]]"
us_refs:
  - US-1.2.3-registrarresultado
  - US-1.3.1-read-models-performanceactual-proximosatletas
  - US-1.4.2-flujo-e2e-audit-log-get-events
  - US-4.3.2-grillapage-operativa-wizard-movil-de-performance
estado: implementado
last_updated: "2026-05-28"
---

# RF-EJ-05

**Área:** [[RF-ejecucion|Ejecución de Competencias]]  
**BCs:** [[competencia]]

---

**Requerimiento:** ¿El cronometraje lo hace el sistema?  
**Respuesta:** **No.** El juez toma el tiempo manualmente e ingresa el valor.

## US que implementan este RF

### [[US-1.2.3-registrarresultado]]
*RegistrarResultado*

**Tests:**
- `tests/features/US-1.2.3-registrar-resultado.feature`
- `tests/integration/competencia/test_registrar_resultado_integration.py`

### [[US-1.3.1-read-models-performanceactual-proximosatletas]]
*Read Models: PerformanceActual, ProximosAtletas, ProgresoCompetencia*

**Tests:**
- `tests/features/US-1.3.1-interfaz-juez.feature`
- `tests/integration/competencia/test_api_interfaz_juez.py`

### [[US-1.4.2-flujo-e2e-audit-log-get-events]]
*Flujo E2E + audit log GET /events*

**Tests:**
- `tests/features/US-1.4.2-flujo-e2e.feature`
- `tests/integration/competencia/test_flujo_e2e.py`

### [[US-4.3.2-grillapage-operativa-wizard-movil-de-performance]]
*GrillaPage operativa + wizard móvil de performance*
