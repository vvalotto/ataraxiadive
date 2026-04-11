# Reporte de Implementación: US-4.3.3

**US:** US-4.3.3 — Casos alternativos — DNS, BKO y tarjeta blanca con penalizaciones
**Incremento:** INC-4.3
**Sprint:** SP4 — La Plataforma
**Fecha:** 2026-04-11
**Branch:** `feature/US-4.3.3-casos-alternativos-performance`

---

## Resumen de Implementación

### Artefactos creados

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Componente | `frontend/src/components/juez/MotivoDqSelector.tsx` | selector de `MotivoDQ` con labels de UI |
| Componente | `frontend/src/components/juez/PenalizacionesSelector.tsx` | contador de penalizaciones técnicas |
| Fixture | `scripts/setup_us_4_3_3_fixture.py` | reset de fixtures `STA` y `DNF` |
| Estrategia | `docs/reports/US-4.3.3-test-strategy.md` | salida Fases 4-6 |
| Calidad | `quality/reports/codeguard/US-4.3.3-quality.json` | gates tecnicos |

### Artefactos modificados

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| API competencia | `src/competencia/api/router.py` | agrega `POST /registrar-dns` |
| API frontend | `frontend/src/api/competencia.ts` | agrega `registrarDns` y soporte de penalizaciones |
| Página | `frontend/src/pages/juez/PerformanceFlowPage.tsx` | incorpora DNS, BKO, roja con `MotivoDQ` y blanca penalizada |
| Contexto | `docs/reports/US-4.3.3-context.md` | hallazgos de dominio/spec |
| Plan | `docs/plans/sp4/US-4.3.3-plan.md` | plan aprobado |
| Matrix | `docs/traceability/matrix.md` | registra avance de US-4.3.3 |

---

## Decisiones y hallazgos relevantes

1. **DNS quedó alineado al dominio real:**
   el aggregate vigente solo permite DNS desde `Llamada`, por lo que la UX se
   implementa desde Paso 2.

2. **Las penalizaciones no se envían como `Blanca`:**
   la UI mapea a `BlancaConPenalizaciones`, que es el contrato real del backend.

3. **Los códigos reales de `MotivoDQ` no son los de la spec textual:**
   la UI muestra labels en español, pero postea los enums reales del dominio.

4. **La fixture manual ya cubre `STA` y `DNF`:**
   esto permite validar BKO/DNS en `STA` y blanca penalizada en `DNF`.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| `npm run build` | ✅ aprobado |
| `npm run lint` | ✅ aprobado |
| `python -m compileall` | ✅ aprobado |
| Smoke test `TestClient` | ✅ aprobado |
| Validación manual BDD/UI | ⏳ pendiente |

---

## Estado de cierre

`US-4.3.3` quedó implementada a nivel de código y validación técnica.

Pendiente para cierre funcional completo:

- validar manualmente DNS;
- validar manualmente BKO con distancia obligatoria;
- validar manualmente blanca con penalizaciones en `DNF`;
- validar UI deshabilitada de penalizaciones en `STA`.

---

*Generado: 2026-04-11 — implementación manual secuencial de US-4.3.3*
