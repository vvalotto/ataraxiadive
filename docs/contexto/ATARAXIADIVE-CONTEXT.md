# AtaraxiaDive — Contexto de Proyecto para /implement-us

> **Este documento es de lectura obligatoria en Fase 0 de `/implement-us`.**
> Provee el contexto arquitectónico, de paths y de patrones DDD específicos del proyecto.
> Complementa el perfil `hexagonal-ddd-bc` con los detalles específicos de AtaraxiaDive.

---

## 1. Arquitectura: Hexagonal DDD BC-First

AtaraxiaDive usa **arquitectura hexagonal con DDD**, organizada por Bounded Context.
No es layered architecture. El perfil activo es `hexagonal-ddd-bc` — este documento provee los overrides específicos del proyecto.

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
│   │   │   ├── {aggregate}.py
│   │   │   ├── {aggregate}_events.py  ← solo ES: aplica eventos al estado
│   │   │   └── {aggregate}_state.py   ← solo ES: objeto de estado del aggregate
│   │   ├── value_objects/ ← value objects inmutables
│   │   ├── events/       ← domain events (DomainEvent base)
│   │   ├── entities/     ← solo ES: entidades con identidad que no son aggregate root
│   │   └── ports/        ← interfaces de repositorios y servicios externos
│   ├── application/
│   │   ├── commands/     ← command handlers
│   │   ├── queries/      ← query handlers
│   │   └── _{policy}.py  ← helpers de política (ej: _p08_finalizacion.py)
│   ├── infrastructure/
│   │   ├── event_store/  ← solo BCs con Event Sourcing
│   │   └── repositories/ ← implementaciones de puertos
│   └── api/              ← router FastAPI del BC
├── torneo/               ← Supporting (CRUD — sin event_store, sin entities/)
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

> **Convenciones específicas de Event Sourcing (competencia, notificaciones):**
> - `{aggregate}_events.py` — módulo de aplicación de eventos al estado del aggregate (para reconstrucción desde event store). NO es un DomainEvent — es lógica interna del aggregate.
> - `{aggregate}_state.py` — dataclass de estado mutable que el aggregate reconstruye.
> - `entities/` — entidades con identidad que participan en el aggregate pero no son aggregate root (ej: `GrillaDeSalida`).
> - `_{policy}.py` en `application/` — helpers de política de aplicación que no encajan como CommandHandler ni QueryHandler (ej: `_p08_finalizacion.py`).
>
> **BCs CRUD (torneo, registro, resultados, identidad) NO tienen** `entities/`, `event_store/`, ni archivos `_state`/`_events`.

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
| US-IEDD (input del skill) | `docs/specs/spX/US-X.Y.Z.md` (donde X = número de SP) |
| ADRs | `docs/adr/ADR-NNN-*.md` |
| Documento de arquitectura | `docs/design/architecture.md` |
| Domain model | `docs/design/domain-model.md` |
| Traceability matrix | `docs/traceability/matrix.md` |
| Plan de implementación (Fase 2) | `docs/plans/spX/US-X.Y.Z-plan.md` |
| Reporte final (Fase 9) | `docs/reports/US-X.Y.Z-report.md` |
| Reporte CodeGuard (Fase 7) | `quality/reports/codeguard/US-X.Y.Z-quality.json` |
| Feature BDD (Fase 1) | `tests/features/US-X.Y.Z-{nombre}.feature` |
| Template BDD | `.claude/templates/bdd/scenario.feature` |
| Tests unitarios | `tests/unit/<bc>/test_{componente}.py` |
| Tests integración | `tests/integration/<bc>/test_{componente}.py` |
| Quality gates config | `pyproject.toml` → `[tool.codeguard]` |

---

## 4. Tipos de Componente DDD por Capa

**Orden de implementación obligatorio** (cada elemento depende del anterior):
ValueObjects → DomainEvents → AggregateRoot → Ports → CommandHandlers → QueryHandlers → Repositories → ApiRouter

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
| AP | Announced Performance — marca declarada antes de competir |
| RP | Realized Performance — marca efectivamente lograda |
| OT | Official Top — momento de inicio de la performance |
| DNS | Did Not Start — atleta no se presentó al OT |
| Tarjeta blanca | Performance válida sin infracciones |
| Tarjeta Blanca con Penalizaciones | Performance válida con infracciones técnicas; RP final = RP medido − Σ deducciones (N × 3m) |
| Tarjeta amarilla | Estado de revisión pendiente |
| Tarjeta roja | Descalificación — requiere `MotivoDQ` obligatorio |
| MotivoDQ | Catálogo de causas de descalificación: `BKO_SUPERFICIE`, `BKO_SUBACUATICO`, `NO_PROTOCOLO`, `INFRACCION_TECNICA`, `NO_INICIO_VENTANA`, `SALIDA_FALSO` |
| Black-out | Pérdida de conciencia → tarjeta roja automática |
| Variante SPE | Sincronizado: `SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50` — cada una genera grilla y ranking independientes |
| DoD | Definition of Done — criterio binario de cierre de incremento |
| US-IEDD | User Story con precondición, postcondición e invariantes formales |

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
