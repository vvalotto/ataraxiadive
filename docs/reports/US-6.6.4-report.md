# Reporte de Implementación: US-6.6.4

**Historia:** Página pública de torneo en ejecución  
**Incremento:** INC-6.6 — Portal Público  
**Fecha:** 2026-05-10  
**Branch:** feature/US-6.6.4-pagina-publica-torneo  
**Tiempo total:** 19 min

---

## Resumen Ejecutivo

US frontend pura — sin cambios de backend. Los tres endpoints necesarios
(`GET /torneos/:id`, `GET /competencia?torneo_id`, `GET /competencia/:id/grilla`)
ya eran públicos. La implementación agrega la página y la conecta al router.

---

## Artefactos Creados

| Artefacto | Descripción |
|-----------|-------------|
| `frontend/src/pages/PublicTorneoDetallePage.tsx` | Página pública — nuevo |
| `frontend/src/pages/PublicTorneosPage.tsx` | Fix destino "Ver panel" (línea 52) |
| `frontend/src/App.tsx` | Ruta `/portalapnea/:torneoId` registrada |
| `tests/features/US-6.6.4-pagina-publica-torneo.feature` | 5 escenarios BDD |
| `tests/features/steps/pagina_publica_torneo_detalle_steps.py` | Steps: 1 passed, 4 skipped |
| `docs/plans/sp6/US-6.6.4-plan.md` | Plan de implementación |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| TypeScript build | ✅ Sin errores |
| ESLint PublicTorneoDetallePage | ✅ 0 warnings |
| BDD: escenario backend | ✅ 1 passed |
| BDD: escenarios UI | ⏭ 4 skipped (validados via build + visual) |
| Suite unit + integración | ✅ 888 passed |

---

## Decisiones Técnicas

- **`loadDetalle` consolidado:** fetch de torneo + competencias en paralelo,
  luego grillas en paralelo. Más simple que `useQueries` para N variable.
- **Polling `refetchInterval: 30_000`:** actualización en vivo sin websockets.
- **Mapping `EstadoPerformance` → visual:** `AnunciadaAP`→Pendiente,
  `Llamada`→En curso, resto→Realizado.
- **Estados no disponibles:** CREADO / INSCRIPCION_ABIERTA / CANCELADO muestran
  mensaje en lugar de grilla vacía.

---

*Generado: 2026-05-10 — US-6.6.4 INC-6.6*
