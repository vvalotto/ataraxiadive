# Reporte de Implementación: US-4.3.4

**US:** US-4.3.4 — Tarjeta amarilla — flujo de revisión y resolución desde la UI  
**Incremento:** INC-4.3  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-12  
**Branch:** `feature/US-4.3.4-tarjeta-amarilla`

---

## Resumen de Implementación

### Artefactos creados

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Contexto | `docs/reports/US-4.3.4-context.md` | hallazgos de Fase 0 |
| Feature | `tests/features/US-4.3.4-tarjeta-amarilla.feature` | escenarios BDD |
| Plan | `docs/plans/sp4/US-4.3.4-plan.md` | plan aprobado |
| Evento | `src/competencia/domain/events/revision_resuelta.py` | cierre definitivo de revisión |
| Command | `src/competencia/application/commands/resolver_revision.py` | command + handler |
| Test | `tests/unit/competencia/application/test_resolver_revision_handler.py` | cobertura del handler nuevo |

### Artefactos modificados

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Aggregate | `src/competencia/domain/aggregates/performance.py` | `Amarilla -> EnRevision` + `resolver_revision()` |
| Reconstitución | `src/competencia/domain/aggregates/performance_state.py` | soporte de `RevisionResuelta` y proyección de amarilla |
| Estado | `src/competencia/domain/value_objects/estado_performance.py` | agrega `EnRevision` |
| Exceptions | `src/competencia/domain/exceptions.py` | agrega `EstadoInvalidoParaResolverRevision` |
| Events | `src/competencia/domain/aggregates/performance_events.py` | factory de `RevisionResuelta` |
| Router API | `src/competencia/api/router.py` | nuevo endpoint `POST /resolver-revision` |
| API frontend | `frontend/src/api/competencia.ts` | `resolverRevision(...)` y soporte de amarilla |
| Tipos frontend | `frontend/src/types/auth.ts` | agrega estado `EnRevision` |
| Grilla juez | `frontend/src/pages/juez/GrillaPage.tsx` | badge/estado `REVISION` |
| Flow juez | `frontend/src/pages/juez/PerformanceFlowPage.tsx` | amarilla, pantalla de revisión y resolución |
| Tests dominio | `tests/unit/competencia/domain/test_performance.py` | cobertura de `EnRevision` |

---

## Decisiones y hallazgos relevantes

1. **Amarilla dejó de ser estado final**  
   `TarjetaAsignada(Amarilla)` ya no cierra la performance. Ahora la deja en `EnRevision`
   y el cierre definitivo ocurre con `RevisionResuelta`.

2. **Se preservó compatibilidad del dominio actual**  
   Para asignar amarilla se sigue requiriendo `motivo_texto`, por lo que el frontend envía
   un motivo mínimo de revisión en esta primera implementación.

3. **La resolución se acotó a Blanca o Roja**  
   La spec mencionaba también blanca con penalizaciones, pero esa variante no se incorporó
   a la revisión para no expandir alcance dentro de la misma US.

4. **La grilla absorbió el nuevo estado sin nueva pantalla dedicada**  
   La fila en `EnRevision` queda visible y tappable, y reutiliza el mismo
   `PerformanceFlowPage` en modo resolución.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| `python3 -m compileall src` | ✅ aprobado |
| `npm run lint` | ✅ aprobado |
| `npm run build` | ✅ aprobado |
| `./.venv/bin/python -m pytest tests/unit/competencia/domain/test_performance.py tests/unit/competencia/application/test_resolver_revision_handler.py -q` | ✅ 76 passed |
| Validación manual BDD/UI | ⏳ pendiente |

---

## Estado de cierre

`US-4.3.4` quedó implementada a nivel de código y validación técnica focalizada.

Pendiente para cierre funcional completo:

- validar manualmente `Amarilla -> Blanca`;
- validar manualmente `Amarilla -> volver a grilla`;
- validar manualmente `Grilla -> retomar revisión`;
- validar manualmente `Amarilla -> Roja` con `MotivoDQ`.

---

*Generado: 2026-04-12 — implementación manual secuencial de US-4.3.4*
