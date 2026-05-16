# US-ADJ-11.4 — Plan de Implementación: BC Registro entidad Juez

| Campo | Valor |
|-------|-------|
| **US** | US-ADJ-11.4 |
| **Branch** | `feature/US-ADJ-11.4-juez` |
| **Estimación total** | 45 min |
| **Story points** | 3 |
| **Patrón** | Idéntico a Atleta — aggregate + port + repo SQLite + commands + query + endpoints |

---

## Tareas de implementación

### T1 — Domain: aggregate Juez + port + excepciones (15 min)

**Archivos:**
- `src/registro/domain/aggregates/juez.py` (nuevo)
- `src/registro/domain/ports/juez_repository_port.py` (nuevo)
- `src/registro/domain/exceptions.py` (agregar JuezNoEncontrado, JuezYaRegistrado)

**Contratos:**
```python
@dataclass
class Juez:
    juez_id: UUID
    email: str
    numero_licencia: str | None = None
    federacion: str | None = None

    def __post_init__(self) -> None: ...  # INV-11.4-01/03/04
    def actualizar(self, numero_licencia=None, federacion=None) -> None: ...  # patch parcial
```

---

### T2 — Infrastructure: SQLiteJuezRepository (10 min)

**Archivo:** `src/registro/infrastructure/repositories/sqlite_juez_repository.py` (nuevo)

**Tabla:** `jueces(juez_id TEXT PK, email TEXT UNIQUE NOT NULL, numero_licencia TEXT, federacion TEXT)`

**Mismo patrón que** `SQLiteAtletaRepository`: `_ensure_table`, `save` (INSERT OR REPLACE), `find_by_email`, `find_by_id`.

---

### T3 — Application: commands + query (10 min)

**Archivos:**
- `src/registro/application/commands/registrar_juez.py` (nuevo)
- `src/registro/application/commands/actualizar_juez.py` (nuevo)
- `src/registro/application/queries/obtener_juez.py` (nuevo)

**Contratos:**
```python
RegistrarJuezCommand(email, numero_licencia=None, federacion=None)  # handler genera juez_id
ActualizarJuezCommand(email, numero_licencia=None, federacion=None)  # patch parcial
ObtenerJuezHandler.handle(email) -> Juez  # lanza JuezNoEncontrado
```

---

### T4 — API: schemas y endpoints en router.py (10 min)

**Archivo:** `src/registro/api/router.py` (modificar)

**Schemas nuevos:**
```python
class RegistrarJuezRequest(BaseModel):
    numero_licencia: str | None = None
    federacion: str | None = None

class JuezResponse(BaseModel):
    juez_id: UUID; email: str
    numero_licencia: str | None; federacion: str | None

class ActualizarJuezMeRequest(BaseModel):
    numero_licencia: str | None = None
    federacion: str | None = None
```

**Endpoints:**
```
POST  /registro/jueces        → JuezDep — 201 JuezResponse | 409
GET   /registro/jueces/me     → JuezDep — 200 JuezResponse | 404
PATCH /registro/jueces/me     → JuezDep — 200 JuezResponse | 404
```

---

## Checklist

- [ ] T1: aggregate Juez + port + excepciones
- [ ] T2: SQLiteJuezRepository
- [ ] T3: commands + query
- [ ] T4: router.py schemas + endpoints

---

*Creado: 2026-05-16*
