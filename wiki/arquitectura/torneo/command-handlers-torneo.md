---
title: "Torneo — Command Handlers"
type: arquitectura-componente
bc: torneo
capa: application
tipo_componente: handler
responsabilidad: "9 handlers de comando: CRUD del torneo + 7 transiciones de ciclo de vida + asignación disciplinas/jueces"
interfaces_out:
  - TorneoRepositoryPort
adr_refs: [ADR-004, ADR-005]
last_updated: "2026-05-23"
sources:
  - src/torneo/application/commands/crear_torneo.py
  - src/torneo/application/commands/actualizar_torneo.py
  - src/torneo/application/commands/asignar_disciplinas.py
  - src/torneo/application/commands/asignar_juez.py
  - src/torneo/application/commands/transicionar_torneo.py
---

# Command Handlers — BC Torneo

---

## CrearTorneoHandler

```python
Command: CrearTorneoCommand(nombre, descripcion, fecha_inicio, fecha_fin,
                             sede_nombre, sede_ciudad, sede_pais,
                             entidad_nombre, entidad_tipo, grupos_etarios)
Retorna: UUID
```

Construye el aggregate `Torneo` (estado inicial `CREADO`) y persiste. No hay validaciones previas — las invariantes están en `__post_init__`.

---

## ActualizarTorneoHandler

Carga el torneo, llama `torneo.actualizar(...)`. Lanza `TorneoNoEncontrado` o `EdicionNoPermitida` (si el estado no es CREADO ni INSCRIPCION_ABIERTA).

---

## AsignarDisciplinasHandler

```python
Command: AsignarDisciplinasCommand(torneo_id, disciplinas: frozenset[Disciplina])
```

Llama `torneo.asignar_disciplinas(disciplinas)`. Lanza `AsignacionNoPermitida` (estado incorrecto) o `DisciplinaObsoleta` (`SPE` no permitida).

---

## AsignarJuezHandler

```python
Command: AsignarJuezCommand(torneo_id, disciplina: Disciplina, juez_id: UUID)
```

Llama `torneo.asignar_juez(disciplina, juez_id)`. Lanza `DisciplinaNoEnTorneo` si la disciplina no está configurada.

---

## Handlers de transición de estado

Todos comparten la clase base `_TransicionHandler` con método `_ejecutar(torneo_id, accion)` que carga → llama método del aggregate → persiste.

| Handler | Transición | Mecanismo extra |
|---------|-----------|-----------------|
| `AbrirInscripcionHandler` | CREADO → INSCRIPCION_ABIERTA | — |
| `CerrarInscripcionHandler` | INSCRIPCION_ABIERTA → PREPARACION | `precondition: Callable[[UUID], Awaitable[None]] \| None` — BC Registro verifica APs completos |
| `IniciarEjecucionHandler` | PREPARACION → EJECUCION | `precondition` (BC Competencia verifica grilla) + `post_action` (inicializar grilla) |
| `VolverAPreparacionHandler` | EJECUCION → PREPARACION | — |
| `IniciarPremiacionHandler` | EJECUCION → PREMIACION | `precondition` (BC Competencia verifica resultados) — aplicada en el router |
| `CerrarTorneoHandler` | PREMIACION → CERRADO | — |
| `CancelarTorneoHandler` | cualquier → CANCELADO | — |

El patrón de precondición/post-acción permite que otros BCs participen en las transiciones **sin acoplar el dominio de Torneo** a los demás. Las funciones se inyectan desde `app.py` al inicializar la aplicación.

## Relaciones

- Instanciados en [[router-torneo]]
- Usan [[sqlite-torneo-repository]]
- Las precondiciones/post-acciones son provistas por BC Registro (`build_cierre_inscripcion_precondition`) y BC Competencia
