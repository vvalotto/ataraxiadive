# Reporte de Implementación — US-3.3.1
## BC Competencia — torneo_id en ConfigurarIntervaloOT

**Fecha:** 2026-03-31
**Branch:** `feature/US-3.3.1-torneo-id-competencia`
**Tiempo total:** ~38 min (estimado: 50 min)
**Varianza:** -24% (más rápido que estimado)

---

## Resumen

Implementación completa del campo `torneo_id` opcional en el aggregate `Competencia`.
Permite asociar una competencia a un torneo para habilitar la política P-09 (Overall) en US-3.5.2.
Backward compatible: 657 tests SP1/SP2 siguen pasando sin modificación.

---

## Artefactos Generados

### Modificados
| Archivo | Cambio |
|---------|--------|
| `competencia/domain/events/intervalo_ot_configurado.py` | `torneo_id: str \| None = None`, `to_payload()`, `from_payload()` con `.get()` |
| `competencia/domain/aggregates/competencia.py` | `torneo_id` en `__init__`, property, `configurar_intervalo_ot()`, `_apply_intervalo_ot_configurado()` |
| `competencia/application/commands/configurar_intervalo_ot.py` | `torneo_id: UUID \| None = None` en command + handler |
| `competencia/application/queries/obtener_estado_competencia.py` | `torneo_id` en `EstadoCompetenciaDTO` |
| `competencia/api/router.py` | `POST /competencia`, `GET /competencia?torneo_id=`, `torneo_id` en respuesta de estado |

### Nuevos
| Archivo | Contenido |
|---------|-----------|
| `competencia/application/queries/obtener_competencias_por_torneo.py` | `ObtenerCompetenciasPorTorneoHandler` |
| `tests/features/US-3.3.1-torneo-id-competencia.feature` | 4 escenarios BDD |
| `tests/unit/competencia/domain/test_torneo_id_competencia.py` | 8 tests unitarios |
| `tests/unit/competencia/application/test_obtener_competencias_por_torneo.py` | 6 tests unitarios |
| `tests/integration/competencia/test_torneo_id_integration.py` | 7 tests de integración |
| `tests/features/steps/test_US_3_3_1_steps.py` | 4 escenarios BDD |
| `docs/plans/sp3/US-3.3.1-plan.md` | Plan de implementación |

---

## Métricas de Tests

| Tipo | Nuevos | Total suite | Estado |
|------|--------|-------------|--------|
| Unitarios | 14 | 668 | ✅ 100% pass |
| Integración | 7 | 668 | ✅ 100% pass |
| BDD | 4 | 668 | ✅ 100% pass |
| **Total nuevos** | **25** | | |

**Regresiones:** 0 — INV-CT-03 verificado.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Black | ✅ 0 reformateos pendientes |
| CodeGuard (archivos nuevos) | ✅ 0 errores, 0 advertencias |
| CodeGuard (pre-existente) | ⚠️ `ajustar_grilla` CC=18 — pre-existente, sin cambio |
| DesignReviewer | pendiente (pre-push) |

---

## Invariantes Verificados

| Invariante | Descripción | Verificado |
|------------|-------------|------------|
| INV-CT-01 | `torneo_id=None` → competencia standalone | ✅ |
| INV-CT-02 | `torneo_id` se persiste en el evento | ✅ |
| INV-CT-03 | Streams SP1/SP2 sin `torneo_id` se reconstituyen | ✅ |

---

## API Nueva

```
POST /competencia
  Body: { competencia_id, disciplina, intervalo_minutos, configurado_por, torneo_id? }
  → 201 { competencia_id }

GET /competencia?torneo_id={uuid}
  → 200 [{ competencia_id, disciplina, torneo_id }]

GET /competencia/{id}/estado
  → 200 { estado, intervalo_minutos, grilla_confirmada, torneo_id }  ← nuevo campo
```

---

## Decisiones Técnicas

1. **`POST /competencia`** como endpoint de creación: el primer `ConfigurarIntervaloOT`
   es el acto de creación en Event Sourcing — coherente con la arquitectura.

2. **`ObtenerCompetenciasPorTorneoHandler`** escanea con `load_all_streams_with_prefix("competencia-")`:
   aceptable en SP3 (volumen bajo). En SP4+ se puede proyectar a tabla.

3. **Reconfiguración sin `torneo_id`** no sobreescribe el `torneo_id` existente:
   `if torneo_id is not None: self._torneo_id = torneo_id` — preserva el vínculo.

---

*Generado: 2026-03-31 — /implement-us US-3.3.1*
