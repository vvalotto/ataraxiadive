# Discrepancias: /implement-us vs AtaraxiaDive

> **Estado: RESUELTO — 2026-04-09**
> Perfil migrado a `hexagonal-ddd-bc`. Las discrepancias documentadas abajo
> estaban activas con el perfil `fastapi-rest` (v2.0.0). Se conservan como
> registro histórico del problema que motivó la migración.

**Fecha original:** 2026-03-20
**Perfil en ese momento:** `fastapi-rest` (asumía arquitectura layered)
**Perfil actual:** `hexagonal-ddd-bc` (hexagonal DDD BC-first — resuelve todas las discrepancias)

---

## Discrepancias por Fase

### Fase 0 — Validación

| Elemento | Skill espera | AtaraxiaDive tiene | Impacto |
|----------|-------------|-------------------|---------|
| Ubicación US | `docs/user-stories/US-*.md` | `docs/plans/US-X.Y.Z.md` | No encuentra la US |
| ADRs | `docs/architecture/ADR-*.md` | `docs/adr/ADR-*.md` | No valida arquitectura |
| Quality config | `.pylintrc` | `pyproject.toml [tool.codeguard]` | Advertencia falsa |
| Contexto proyecto | No lee ningún contexto | `docs/plans/ATARAXIADIVE-CONTEXT.md` | No conoce arquitectura real |

### Fase 1 — BDD

| Elemento | Skill espera | AtaraxiaDive tiene | Impacto |
|----------|-------------|-------------------|---------|
| Template BDD | `.claude/templates/bdd-scenario.feature` | `.claude/templates/bdd/scenario.feature` | Template no encontrado |
| Ubicación `.feature` | `tests/features/US-XXX-{nombre}.feature` | `tests/features/US-X.Y.Z-{nombre}.feature` | Leve — coincide ✅ |

### Fase 3 — Implementación ← crítico

| Elemento | Skill espera | AtaraxiaDive tiene | Impacto |
|----------|-------------|-------------------|---------|
| `project_root` | `app/` | `src/` | Paths incorrectos en todo el código generado |
| `component_path` | `app/api/{name}/` | `src/{bc}/` | Genera archivos en lugar equivocado |
| Patrón arquitectónico | `layered` (router→service→repository) | `hexagonal` (domain→application→infrastructure→api) | Genera componentes incorrectos |
| Tipos de componente | `Endpoint, Service, Repository, Schema` | `Aggregate, ValueObject, DomainEvent, Port, CommandHandler, QueryHandler, ApiRouter` | Patrones DDD ausentes |
| Regla de oro | No existe | `<bc>/domain/` no importa `infrastructure/` ni `api/` | Puede generar violaciones hexagonales |
| Comunicación entre BCs | No definida | Solo vía puertos — ACL en `infrastructure/` | Puede generar imports directos entre BCs |

### Fases 4 y 5 — Tests Unitarios e Integración

| Elemento | Skill espera | AtaraxiaDive tiene | Impacto |
|----------|-------------|-------------------|---------|
| Tests unitarios | `tests/api/test_*.py`, `tests/services/test_*.py` | `tests/unit/<bc>/test_*.py` | Archivos creados en path incorrecto |
| Tests integración | `tests/integration/test_{feature}_e2e.py` | `tests/integration/<bc>/test_*.py` | Path incorrecto |
| `conftest.py` | `tests/conftest.py` | `tests/conftest.py` | Coincide ✅ |

### Fase 7 — Quality Gates

Adaptada correctamente. Sin discrepancias. ✅

### Fase 9 — Reporte Final

| Elemento | Skill espera | AtaraxiaDive tiene | Impacto |
|----------|-------------|-------------------|---------|
| Reporte narrativo | `docs/reports/{US_ID}-report.md` | `docs/reports/{US_ID}-report.md` | Coincide ✅ |
| Reporte quality | `quality/reports/{US_ID}-quality.json` | `quality/reports/codeguard/{US_ID}-quality.json` | Subdirectorio diferente |

---

## Solución

1. `docs/plans/ATARAXIADIVE-CONTEXT.md` — contexto del proyecto que Fase 0 lee obligatoriamente
2. `.claude/skills/implement-us/customizations/fastapi-rest.json` — actualizado con paths y patrones reales
3. `phases/phase-0-validation.md` — paso 0 obligatorio: leer `ATARAXIADIVE-CONTEXT.md`

---

*Generado en sesión 2026-03-20*
