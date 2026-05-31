---
title: "Torneo — Aggregate Torneo"
type: arquitectura-componente
bc: torneo
capa: domain
tipo_componente: aggregate
responsabilidad: "Ciclo de vida completo del torneo: estados, transiciones, disciplinas con jueces asignados, sede y grupos etarios"
interfaces_out:
  - TorneoRepositoryPort
adr_refs: [ADR-004, ADR-005, ADR-007]
last_updated: "2026-05-23"
sources:
  - src/torneo/domain/aggregates/torneo.py
  - src/torneo/domain/value_objects/estado_torneo.py
  - src/torneo/domain/value_objects/disciplina_torneo.py
us_origen:
  - US-3.1.1-aggregate-torneo-maquina-de-estados
tests:
  - tests/features/US-3.1.1-aggregate-torneo.feature
  - tests/integration/torneo/test_torneo_domain_integration.py
---

# Aggregate Torneo

## Responsabilidad

Modela el **ciclo de vida completo de un torneo de apnea**. Controla las transiciones de estado, las disciplinas habilitadas con sus jueces asignados, la sede y los grupos etarios participantes.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `torneo_id` | UUID | Autogenerado |
| `nombre` | str | No puede ser vacío |
| `descripcion` | str | Texto libre |
| `fecha_inicio` | date | Debe ser ≤ `fecha_fin` |
| `fecha_fin` | date | |
| `sede` | `Sede` | VO — nombre, ciudad, país |
| `entidad_organizadora` | `EntidadOrganizadora` | VO — nombre, tipo |
| `estado` | `EstadoTorneo` | Ver ciclo de vida abajo |
| `disciplinas_torneo` | `list[DisciplinaTorneo]` | Disciplinas habilitadas con juez opcional |
| `tipo_reglamento` | `TipoReglamento` | Default: `FAAS` |
| `grupos_etarios` | `frozenset[GrupoEtario]` | Default: `{SENIOR}` — al menos uno |

## Ciclo de vida

```
CREADO ──→ INSCRIPCION_ABIERTA ──→ PREPARACION ──→ EJECUCION ──→ PREMIACION ──→ CERRADO
                                                    ↑_________↓
                                              (volver_a_preparacion)
```

Desde cualquier estado no terminal → `CANCELADO` (excepto CERRADO)

| Estado | Descripción |
|--------|-------------|
| `CREADO` | Estado inicial — edición libre, asignación de disciplinas permitida |
| `INSCRIPCION_ABIERTA` | Atletas pueden inscribirse; edición restringida |
| `PREPARACION` | Inscripción cerrada; declaración de APs; asignación de disciplinas aún permitida |
| `EJECUCION` | Competencia en curso — puede volver a PREPARACION (ej. mal tiempo) |
| `PREMIACION` | Competencia finalizada; cálculo de resultados |
| `CERRADO` | Terminal — sin transiciones |
| `CANCELADO` | Terminal — sin transiciones |

## Operaciones

| Método | Transición / Efecto | Precondición |
|--------|---------------------|-------------|
| `abrir_inscripcion()` | CREADO → INSCRIPCION_ABIERTA | — |
| `cerrar_inscripcion()` | INSCRIPCION_ABIERTA → PREPARACION | todos los APs deben estar declarados (precondición externa) |
| `iniciar_ejecucion()` | PREPARACION → EJECUCION | grilla generada (precondición externa) |
| `volver_a_preparacion()` | EJECUCION → PREPARACION | — |
| `iniciar_premiacion()` | EJECUCION → PREMIACION | resultados completos (precondición externa) |
| `cerrar()` | PREMIACION → CERRADO | — |
| `cancelar()` | cualquier no-terminal → CANCELADO | no CERRADO ni ya CANCELADO |
| `actualizar(...)` | sin transición | solo en CREADO o INSCRIPCION_ABIERTA |
| `asignar_disciplinas(disciplinas)` | sin transición | en CREADO, INSCRIPCION_ABIERTA o PREPARACION; `Disciplina.SPE` no permitida (legacy) |
| `asignar_juez(disciplina, juez_id)` | sin transición | mismos estados que asignar_disciplinas; disciplina debe existir en torneo |
| `obtener_disciplinas_de_juez(juez_id)` | query | — |

## Value Object: DisciplinaTorneo

```python
@dataclass(frozen=True)
class DisciplinaTorneo:
    disciplina: Disciplina
    juez_id: UUID | None = None

    def con_juez(self, juez_id: UUID) -> DisciplinaTorneo: ...
```

Inmutable — la reasignación de juez crea una nueva instancia. Serializable a dict (`to_dict` / `from_dict`) para persistencia JSON en SQLite.

## Invariantes

- Nombre no vacío
- `fecha_fin >= fecha_inicio`
- `grupos_etarios` no vacío (mínimo uno)
- `Disciplina.SPE` no puede ser asignada a torneos nuevos — es disciplina legacy

## Relaciones

**Contenedor:** [[arquitectura/torneo]]

- Persiste en `torneo.db` via [[sqlite-torneo-repository]]
- Sus datos de estado (`INSCRIPCION_ABIERTA`, `fecha_inicio`) son leídos por BC Registro via [[torneo-consulta-port]]
- Las transiciones son orquestadas por [[command-handlers-torneo]]
- El aggregate expone hooks (precondiciones/post-acciones) que permiten a BC Registro y BC Competencia participar en transiciones de estado sin violar la arquitectura hexagonal

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/torneo/domain/aggregates/torneo.py` | Aggregate Torneo — máquina de estados, disciplinas, sede |
| `src/torneo/domain/value_objects/estado_torneo.py` | Value Object EstadoTorneo — StrEnum con 7 estados |
| `src/torneo/domain/value_objects/disciplina_torneo.py` | Value Object DisciplinaTorneo — disciplina con juez asignado |
