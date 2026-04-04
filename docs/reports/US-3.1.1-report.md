# Reporte de Implementación: US-3.1.1 — Aggregate Torneo — máquina de estados

**Fecha:** 2026-03-29
**Sprint:** SP3 — El Torneo
**Incremento:** INC-3.1
**Branch:** feature/US-3.1.1-aggregate-torneo
**Duración total:** ~12 min (tracker)

---

## Resumen

Implementación del aggregate `Torneo` con máquina de estados completa para el BC `torneo`.
BC Supporting/CRUD — sin Event Sourcing. Primera US de SP3.

---

## Artefactos generados

### Dominio (`src/torneo/domain/`)

| Archivo | Contenido |
|---------|-----------|
| `value_objects/estado_torneo.py` | `EstadoTorneo(StrEnum)` — 7 estados |
| `value_objects/sede.py` | `Sede` — dataclass frozen |
| `value_objects/entidad_organizadora.py` | `EntidadOrganizadora` — dataclass frozen |
| `value_objects/__init__.py` | Exports |
| `exceptions.py` | `TorneoNoEncontrado`, `TransicionEstadoInvalida`, `TorneoCerrado` |
| `ports/torneo_repository_port.py` | `TorneoRepositoryPort(ABC)` |
| `ports/__init__.py` | Exports |
| `aggregates/torneo.py` | `Torneo` — aggregate con `_TRANSICIONES_VALIDAS` dict |
| `aggregates/__init__.py` | Exports |
| `__init__.py` | Exports completos del dominio |

### Tests

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `tests/unit/torneo/domain/test_torneo.py` | 18 | 100% |
| `tests/integration/torneo/test_torneo_domain_integration.py` | 5 | 100% |
| `tests/features/US-3.1.1-aggregate-torneo.feature` | 13 escenarios | — |
| `tests/features/steps/torneo_aggregate_steps.py` | 13 BDD | — |

**Total: 36 tests — 100% pass — 100% cobertura `torneo/domain/`**

### Documentación

| Archivo | Actualización |
|---------|--------------|
| `docs/plans/sp3/US-3.1.1-plan.md` | Plan generado en Fase 2 |
| `docs/traceability/matrix.md` | §9 SP3 creado, §10 Tests actualizado (v1.4) |

---

## Decisiones de diseño

- **`_TRANSICIONES_VALIDAS` como dict de clase:** el grafo de estados se declara una vez, `_transicionar()` lo consulta. Evita chain de `if/elif` y hace el grafo explícito y legible.
- **`cancelar()` separado del grafo:** cancelar desde cualquier estado activo es semánticamente distinto a una transición normal — tiene su propio método con validación explícita de CERRADO y CANCELADO.
- **Sin eventos de dominio en SP3:** opcionales según la spec. Se agregan en SP4 para integración con BC Notificaciones.
- **`TorneoYaCancelado` eliminado:** unificado en `TransicionEstadoInvalida` — más simple y consistente con el resto del dominio.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| CodeGuard | ✅ 0 errores, 0 advertencias |
| Cobertura `torneo/domain/` | ✅ 100% |
| Pylint | ✅ (PEP8 compliant) |
| Hexagonal: sin imports infra en domain | ✅ |

---

## Notas experimentales

Primera US de SP3 sobre un BC CRUD (no Event Sourcing). El patrón dataclass + máquina de estados con dict es significativamente más simple que el aggregate con Event Sourcing de SP1/SP2 — refleja correctamente la naturaleza Supporting del BC Torneo.

El overhead del workflow se mantuvo bajo (~12 min tracker) consistente con la estabilización observada en SP2.
