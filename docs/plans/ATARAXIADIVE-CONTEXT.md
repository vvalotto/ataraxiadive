# AtaraxiaDive — Contexto de Proyecto para /implement-us

> **Este documento es de lectura obligatoria en Fase 0 de `/implement-us`.**
> Provee el contexto arquitectónico, de paths y de patrones DDD específicos del proyecto.
> Reemplaza y corrige cualquier asunción del perfil genérico `fastapi-rest`.

---

## 1. Arquitectura: Hexagonal DDD BC-First

AtaraxiaDive usa **arquitectura hexagonal con DDD**, organizada por Bounded Context.
No es layered architecture. El perfil `fastapi-rest` es solo la base — este documento lo sobrescribe.

### Regla de Oro (absoluta, sin excepciones)

```
<bc>/domain/         → NO importa nada fuera de su propio domain/
<bc>/application/    → importa <bc>/domain/ únicamente
<bc>/infrastructure/ → implementa puertos definidos en <bc>/domain/ports/
<bc>/api/            → importa <bc>/application/ únicamente
```

Única excepción: cualquier capa puede importar desde `src/shared/domain/`.

**Comunicación entre BCs:** exclusivamente a través de puertos (`domain/ports/`).
Nunca imports directos entre BCs. Los ACLs viven en `infrastructure/` del BC consumidor.

---

## 2. Estructura de Directorios

### Código fuente

```
src/
├── competencia/          ← Core Domain (Event Sourcing)
│   ├── domain/
│   │   ├── aggregates/   ← aggregates raíz con invariantes
│   │   ├── value_objects/ ← value objects inmutables
│   │   ├── events/       ← domain events (DomainEvent base)
│   │   └── ports/        ← interfaces de repositorios y servicios externos
│   ├── application/
│   │   ├── commands/     ← command handlers
│   │   └── queries/      ← query handlers
│   ├── infrastructure/
│   │   ├── event_store/  ← solo BCs con Event Sourcing
│   │   └── repositories/ ← implementaciones de puertos
│   └── api/              ← router FastAPI del BC
├── torneo/               ← Supporting (CRUD — sin event_store)
├── registro/             ← Supporting (CRUD)
├── resultados/           ← Supporting (CRUD)
├── identidad/            ← Generic (CRUD)
├── notificaciones/       ← Generic (Event Sourcing)
├── shared/
│   └── domain/
│       ├── value_objects/ ← tipos primitivos cross-BC
│       └── base/         ← clases base (DomainEvent, AggregateRoot, etc.)
└── app.py                ← ensamble central de routers FastAPI
```

### Tests

```
tests/
├── unit/
│   └── <bc>/             ← espejo de src/<bc>/ — un archivo por componente
├── integration/
│   └── <bc>/             ← stack completo del BC con infraestructura real
└── features/
    ├── steps/            ← step definitions compartidas
    └── US-X.Y.Z-{nombre}.feature
```

---

## 3. Paths Canónicos

| Artefacto | Path |
|-----------|------|
| US-IEDD (input del skill) | `docs/plans/US-X.Y.Z.md` |
| ADRs | `docs/adr/ADR-NNN-*.md` |
| Documento de arquitectura | `docs/design/architecture.md` |
| Domain model | `docs/design/domain-model.md` |
| Traceability matrix | `docs/traceability/matrix.md` |
| Plan de implementación (Fase 2) | `docs/plans/US-X.Y.Z-plan.md` |
| Reporte final (Fase 9) | `docs/reports/US-X.Y.Z-report.md` |
| Reporte CodeGuard (Fase 7) | `quality/reports/codeguard/US-X.Y.Z-quality.json` |
| Feature BDD (Fase 1) | `tests/features/US-X.Y.Z-{nombre}.feature` |
| Template BDD | `.claude/templates/bdd/scenario.feature` |
| Tests unitarios | `tests/unit/<bc>/test_{componente}.py` |
| Tests integración | `tests/integration/<bc>/test_{componente}.py` |
| Quality gates config | `pyproject.toml` → `[tool.codeguard]` |

---

## 4. Tipos de Componente DDD por Capa

Al implementar una US, los componentes a generar son:

### `domain/aggregates/`
- **AggregateRoot** — entidad raíz con identidad, invariantes y domain events
- Encapsula toda la lógica de negocio del BC
- Emite eventos de dominio ante cada cambio de estado
- Ejemplo: `Performance`, `Competencia`, `Grilla`

### `domain/value_objects/`
- **ValueObject** — inmutable, sin identidad, igualdad por valor
- Valida sus propios datos en `__init__`
- Ejemplo: `AnnouncedPerformance`, `Tarjeta`, `TorneoId`

### `domain/events/`
- **DomainEvent** — hereda de `shared/domain/base/DomainEvent`
- Inmutable, describe algo que ocurrió en el dominio
- Ejemplo: `PerformanceRegistrada`, `TarjetaAsignada`, `DNSRegistrado`

### `domain/ports/`
- **Repository interface** — ABC que define el contrato de persistencia
- **Service interface** — ABC para servicios externos
- Ejemplo: `PerformanceRepository`, `NotificacionService`

### `application/commands/`
- **CommandHandler** — orquesta la lógica de aplicación para un comando
- Carga el aggregate desde el repositorio, ejecuta el método, persiste
- Sin lógica de negocio — delega al aggregate
- Ejemplo: `RegistrarAPHandler`, `AsignarTarjetaHandler`

### `application/queries/`
- **QueryHandler** — lee datos del read model o repositorio
- Retorna DTOs o view models
- Ejemplo: `ObtenerPerformancesHandler`

### `infrastructure/repositories/`
- **Repository implementation** — implementa el puerto definido en `domain/ports/`
- Traduce entre domain objects y persistencia (SQLAlchemy, event store)
- Ejemplo: `PerformanceSQLRepository`, `PerformanceEventStoreRepository`

### `infrastructure/event_store/`
- Solo para BCs con Event Sourcing: `competencia` y `notificaciones`
- Implementa la persistencia de domain events

### `api/`
- **APIRouter** — router FastAPI que expone el BC como HTTP API
- Solo importa `application/` — nunca `domain/` directamente
- Traduce HTTP request → Command/Query → HTTP response

---

## 5. Bounded Contexts y Subproyectos

| BC | Tipo | Impl. | SP | Notas |
|----|------|:-----:|----|-------|
| `competencia` | Core Domain | ES | SP1 + SP2 | Aggregates: Performance, Competencia, Grilla |
| `torneo` | Supporting | CRUD | SP3 | Aggregates: Torneo, EntidadOrganizadora, Sede |
| `registro` | Supporting | CRUD | SP3 | Aggregates: Atleta, Inscripcion |
| `resultados` | Supporting | CRUD | SP3 | Aggregates: Ranking, Overall |
| `identidad` | Generic | CRUD | SP3 | Aggregates: Usuario |
| `notificaciones` | Generic | ES | SP4 | Aggregate: Notificacion |

**SP1** trabaja exclusivamente sobre `src/competencia/`.

---

## 6. Lenguaje Ubicuo (usar siempre estos términos)

| Término | Significado |
|---------|-------------|
| AP | Announced Performance — marca declarada |
| RP | Realized Performance — marca lograda |
| OT | Official Top — inicio de la performance |
| DNS | Did Not Start |
| Tarjeta blanca | Performance válida |
| Tarjeta amarilla | Penalización parcial |
| Tarjeta roja | Descalificación |
| Black-out | Pérdida de conciencia → tarjeta roja automática |

---

## 7. Convenciones de Código

- **Formato:** Black, line-length 100
- **Tipos:** mypy modo estricto — todos los métodos públicos tipados
- **Naming:** snake_case para módulos y métodos, PascalCase para clases
- **Invariantes:** se documentan como `INV-P-NN` en docstrings
- **Domain events:** se listan en el aggregate que los emite

---

## 8. Quality Gates (Fase 7)

| Métrica | Umbral | Herramienta |
|---------|--------|-------------|
| Pylint | ≥ 8.0 | `codeguard src/<bc>/` |
| Complejidad ciclomática | ≤ 10 | CodeGuard |
| Cobertura | ≥ 90% en `domain/` + `application/` | `pytest-cov` |

**Nunca usar `radon` directamente** — usar CodeGuard que lo orquesta.

---

*Versión 1.0 — 2026-03-20*
*Leer este documento completo antes de iniciar cualquier fase de `/implement-us`.*
