# ADR-006: Estructura de Código Fuente BC-First

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-005 (Bounded Contexts DDD), ADR-001 (Arquitectura Hexagonal) |

---

## Contexto

Con 6 Bounded Contexts definidos (ADR-005) y arquitectura hexagonal (ADR-001), es necesario
decidir cómo organizar el código fuente: agrupado por **capa técnica** o por **Bounded Context**.

Las dos opciones principales son:

**Layer-first** — agrupa por responsabilidad técnica:
```
src/domain/         ← todos los aggregates de todos los BCs
src/application/    ← todos los casos de uso
src/infrastructure/ ← todos los repositorios
src/api/            ← todos los routers
```

**BC-first** — agrupa por contexto de negocio:
```
src/competencia/
  domain/ · application/ · infrastructure/ · api/
src/torneo/
  domain/ · application/ · infrastructure/ · api/
```

---

## Decisión

**Se adopta BC-first** como estructura principal del código fuente.

Cada Bounded Context es un paquete Python independiente con sus propias capas internas.
Un módulo `shared/` aloja los tipos primitivos y base classes que cruzan BCs.
Un `app.py` central ensambla los routers FastAPI de cada BC.

```
src/
├── competencia/
│   ├── domain/{aggregates,value_objects,events,ports}
│   ├── application/{commands,queries}
│   ├── infrastructure/{event_store,repositories}  ← solo BCs con ES
│   └── api/
├── torneo/
│   ├── domain/{aggregates,value_objects,events,ports}
│   ├── application/{commands,queries}
│   ├── infrastructure/repositories
│   └── api/
├── [registro, resultados, identidad — igual que torneo]
├── notificaciones/
│   ├── domain/{aggregates,value_objects,events,ports}
│   ├── application/{commands,queries}
│   ├── infrastructure/{event_store,repositories}
│   └── api/
├── shared/
│   └── domain/{value_objects,base}
└── app.py              ← ensamble central de routers FastAPI
```

---

## Consecuencias

### Tests

- **Tests unitarios** → `tests/unit/<bc>/` (árbol espejo separado, convención Python)
- **Tests de integración** → `tests/integration/<bc>/` (stack completo por BC)
- **Tests BDD** → `tests/features/` organizados por US-IEDD (no por BC)

### Quality Gates

- `quality/reports/codeguard/` — reportes por US (genera `/implement-us`)
- `quality/reports/designreviewer/` — reportes por Incremento (genera el PR)
- `quality/reports/architectanalyst/` — reportes por Baseline (genera cierre SP)

### Regla de oro (sin cambios)

La regla de importación de la arquitectura hexagonal se aplica dentro de cada BC:

```
<bc>/domain/        → no importa nada fuera de su propio domain/
<bc>/application/   → importa <bc>/domain/, nunca infrastructure/
<bc>/infrastructure → implementa puertos definidos en <bc>/domain/ports/
<bc>/api/           → importa <bc>/application/, nunca domain/ directamente
```

La única excepción permitida: cualquier capa puede importar desde `shared/domain/`.

### Comunicación entre BCs

Los BCs se comunican exclusivamente a través de sus puertos (`domain/ports/`).
Nunca mediante imports directos entre BCs. Los ACLs (Anti-Corruption Layers)
viven en `infrastructure/` del BC consumidor.

---

## Alternativa descartada

**Layer-first** fue descartada porque dispersa la cohesión del dominio: para entender
`Competencia` hay que navegar entre cuatro carpetas top-level. Con BC-first, todo lo
relacionado con un contexto de negocio está en un solo lugar, alineado con el principio
DDD de que los BCs son unidades autónomas de despliegue y comprensión.
