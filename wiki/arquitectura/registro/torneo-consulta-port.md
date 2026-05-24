---
title: "Registro — TorneoConsultaPort + SQLiteTorneoConsulta"
type: arquitectura-componente
bc: registro
capa: domain
tipo_componente: port
responsabilidad: "ACL read-only sobre BC Torneo para validar inscripciones (apertura, fecha inicio, disciplinas disponibles)"
interfaces_out: []
adr_refs: [ADR-005, ADR-007]
last_updated: "2026-05-23"
sources:
  - src/registro/domain/ports/torneo_consulta_port.py
  - src/registro/infrastructure/acl/sqlite_torneo_consulta.py
---

# TorneoConsultaPort — ACL a BC Torneo

## Responsabilidad

Puerto de lectura que BC Registro usa para validar invariantes de inscripción contra datos de BC Torneo. Implementa el patrón ACL (Anti-Corruption Layer): el dominio de Registro nunca importa módulos de BC Torneo — sólo conoce esta interfaz.

## Interfaz (ABC)

```python
class TorneoConsultaPort(ABC):
    async def esta_abierto_para_inscripcion(self, torneo_id: UUID) -> bool: ...
    async def obtener_fecha_inicio(self, torneo_id: UUID) -> date: ...
    async def obtener_disciplinas(self, torneo_id: UUID) -> frozenset[Disciplina]: ...
```

| Método | Usado por | Invariante que protege |
|--------|-----------|----------------------|
| `esta_abierto_para_inscripcion` | `InscribirAtletaHandler` | INV-I-02: torneo debe estar `INSCRIPCION_ABIERTA` |
| `obtener_fecha_inicio` | `CancelarInscripcionHandler` | INV-I-03: cancelar solo antes de inicio del torneo |
| `obtener_disciplinas` | `InscribirAtletaHandler` | INV-I-01: disciplinas elegidas deben existir en el torneo |

---

## Implementación: SQLiteTorneoConsulta

Clase `SQLiteAtletaTorneoConsulta` — lee directamente `torneo.db` via `aiosqlite`.

```python
class SQLiteTorneoConsulta(TorneoConsultaPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("TORNEO_DB_PATH", "data/torneo.db")
```

- **No importa** nada de `bc-torneo/` — solo lee la tabla `torneos` de la DB
- `esta_abierto_para_inscripcion`: compara `estado == "INSCRIPCION_ABIERTA"`
- `obtener_fecha_inicio`: lee columna `fecha_inicio`; lanza `TorneoNoDisponible` si no existe
- `obtener_disciplinas`: **TODO pendiente** (US-3.4.1): hasta que Torneo tenga campo `disciplinas`, retorna `frozenset(Disciplina)` — todas las disciplinas disponibles sin restricción

## Nota de diseño

El TODO en `obtener_disciplinas` es una deuda técnica conocida: la validación de disciplinas contra las realmente habilitadas en el torneo estaba prevista para INC-3.4 pero quedó postergada. El comportamiento actual (aceptar cualquier disciplina) es intencionalmente permisivo.

## Relaciones

- Implementa el puerto definido en `domain/ports/` — relación de dependencia hacia adentro
- Usada por [[command-handlers-registro]] (InscribirAtletaHandler, CancelarInscripcionHandler)
- Análoga a `AtletaNombreAdapter` en BC Competencia: ambas leen DBs ajenas directamente (sin API HTTP)
- Registrada en [[router-registro]] como dependencia via `_torneo_consulta()`
