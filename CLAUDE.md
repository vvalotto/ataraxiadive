# CLAUDE.md — AtaraxiaDive

Este archivo es leído automáticamente por Claude Code al trabajar en este repositorio.

---

## Identidad del Proyecto

**AtaraxiaDive** es una plataforma web para gestión de torneos de apnea (freediving).
- **Stack:** FastAPI (backend) + React PWA (frontend) + PostgreSQL
- **Arquitectura:** Hexagonal + Event Sourcing (fase de competencia)
- **Desarrollador:** Victor Valotto
- **Horizonte:** 2026, sin fecha fija — avance por incrementos con DoD binaria

---

## Estructura del Repositorio

```
src/
├── domain/          ← aggregates, value objects, domain events, invariantes
├── application/     ← use cases, command/query handlers
├── infrastructure/  ← event store, read model, PostgreSQL, repos
└── api/             ← FastAPI routes, schemas Pydantic, dependencias

frontend/            ← React PWA (package.json propio)
tests/
├── unit/            ← tests de aggregates y value objects
├── integration/     ← tests de use cases + infraestructura
└── features/        ← .feature files BDD (Gherkin)
docs/
├── adr/             ← Architecture Decision Records
├── plans/           ← US-IEDD por incremento
└── reports/         ← reportes /implement-us
.cm/
├── baselines/       ← BL-000.md ... BL-NNN.md
└── changes/         ← RFC-NNN.md
skills/              ← claude-dev-kit
```

---

## Regla de Oro: Arquitectura Hexagonal

**El dominio no importa nada de infraestructura.** Esta regla es absoluta.

```
domain/     → no importa nada externo al propio dominio
application/ → importa domain/, nunca infrastructure/ directamente
infrastructure/ → implementa interfaces definidas en domain/
api/         → importa application/, nunca domain/ directamente
```

Si un archivo en `domain/` tiene un import de `infrastructure/` o `api/`, es un error de arquitectura. DesignReviewer lo detectará.

---

## Convenciones de Código

### Python (backend)
- **Formato:** Black, line-length 100
- **Imports:** isort, perfil Black
- **Linting:** Ruff + Pylint ≥ 8.0
- **Tipos:** mypy en modo estricto — todos los métodos públicos tipados
- **Cobertura mínima:** 90% en `domain/` y `application/`

### Commits (Conventional Commits)
```
<type>(<scope>): <descripción en español>

# Types: feat | fix | refactor | test | docs | chore
# Scopes: domain | application | infra | api | frontend | cm | tests

# Ejemplos:
feat(domain): agregar aggregate Performance con invariantes [CI-001]
test(domain): tests unitarios de Performance.asignar_tarjeta
docs(adr): ADR-002 decisión FastAPI como backend
chore(cm): registrar BL-001 cierre SP1
```

### Branching
```
main          ← baselines etiquetadas (v0.1.0, v0.2.0...)
  └── develop ← integración continua
        ├── feature/US-X.Y.Z-descripcion
        └── fix/descripcion-corta
```

### Nomenclatura de Ramas de US
```
feature/US-1.2.1-performance-invariantes
feature/US-1.2.2-registrar-performance-event-store
```

---

## Lenguaje Ubicuo (Glosario Core)

| Término | Significado |
|---------|-------------|
| AP | Announced Performance — marca declarada antes de competir |
| RP | Realized Performance — marca efectivamente lograda |
| OT | Official Top — momento de inicio de la performance |
| DNS | Did Not Start — atleta no se presentó |
| Tarjeta blanca | Performance válida |
| Tarjeta amarilla | Penalización parcial (con deducción) |
| Tarjeta roja | Descalificación |
| Black-out | Pérdida de conciencia → tarjeta roja automática |
| DoD | Definition of Done — criterio binario de cierre de incremento |

---

## Gestión de la Configuración (CM)

### Jerarquía de trabajo
```
Subproyecto (SP1–SP5) → Baseline (BL-NNN)
  Incremento           → DoD binaria de integración
    Historia de Usuario → /implement-us (10 fases)
```

### Al implementar una US
1. La US-IEDD debe estar en `docs/plans/US-X.Y.Z.md` antes de empezar
2. Usar `/implement-us` con las 10 fases
3. Commit con referencia al CI afectado: `feat(domain): ... [CI-001]`
4. Actualizar `docs/traceability/matrix.md` al cerrar

### Al cerrar un Incremento
1. Verificar DoD de integración
2. Merge a `develop` con PR
3. Correr `designreviewer src/` — cero violations CRITICAL

### Al cerrar un Subproyecto (Baseline)
1. Correr `architectanalyst src/ --sprint-id BL-NNN`
2. Registrar métricas en `.cm/baselines/BL-NNN.md`
3. Tag en git: `git tag v0.N.0`
4. Retrospectiva documentada en BL-NNN.md

---

## Comandos Útiles

```bash
# Levantar entorno
docker-compose up

# Tests
pytest tests/unit/
pytest tests/integration/
pytest tests/features/

# Calidad
codeguard src/
designreviewer src/
architectanalyst src/ --sprint-id BL-NNN

# Formato
black src/ tests/
isort src/ tests/
```

---

*Última actualización: 2026-03-14 — Semana 0, inicialización*
