# Plan de Implementación — US-3.2.2: BC Registro — Aggregate Atleta

**Fecha:** 2026-03-31
**Branch:** feature/US-3.2.2-aggregate-atleta
**Estimación:** 3 puntos (~90 min)

---

## Estructura de archivos a crear

```
src/registro/
├── domain/
│   ├── aggregates/
│   │   └── atleta.py                        # T1
│   ├── value_objects/
│   │   └── categoria.py                     # T1
│   ├── ports/
│   │   └── atleta_repository_port.py        # T2
│   └── exceptions.py                        # T2
├── application/
│   ├── commands/
│   │   └── registrar_atleta.py              # T3
│   └── queries/
│       └── obtener_atleta.py                # T3
├── infrastructure/
│   └── repositories/
│       └── sqlite_atleta_repository.py      # T4
└── api/
    └── router.py                            # T5
```

---

## Tareas

### T1 — Domain: `Categoria` VO + `Atleta` aggregate
- `Categoria(StrEnum)`: 6 valores (SENIOR_M/F, MASTER_M/F, JUNIOR_M/F)
- `Atleta`: dataclass con atleta_id, nombre, apellido, email, fecha_nacimiento, categoria, brevet
- Validación de invariantes en `__post_init__`: INV-A-01, INV-A-02, INV-A-04
- **Est:** 10 min

### T2 — Domain: puerto + excepciones
- `AtletaRepositoryPort(ABC)`: save, find_by_id, find_by_email
- `AtletaNoEncontrado`, `AtletaYaRegistrado`
- **Est:** 5 min

### T3 — Application: command + handlers
- `RegistrarAtletaCommand` (frozen dataclass) + `RegistrarAtletaHandler`: verifica duplicado por ID, crea Atleta, persiste
- `ObtenerAtletaHandler`: find_by_id, lanza AtletaNoEncontrado
- **Est:** 15 min

### T4 — Infrastructure: SQLiteAtletaRepository
- `data/registro.db`, tabla `atletas`
- Columnas: atleta_id, nombre, apellido, email, fecha_nacimiento, categoria, brevet
- upsert por INSERT OR REPLACE; `fecha_nacimiento` como ISO string
- **Est:** 15 min

### T5 — API: Router FastAPI
- `POST /registro/atletas` → 201 `{atleta_id}`
- `GET /registro/atletas/{atleta_id}` → 200 `{atleta}`
- Exception handlers: AtletaYaRegistrado→409, AtletaNoEncontrado→404, ValueError→422
- `app.py` actualizado con registro router
- **Est:** 15 min

---

## Restricciones arquitectónicas

- `registro/domain/` → no importa nada fuera de su propio `domain/`
- `registro/application/` → solo importa `registro/domain/`
- `registro/infrastructure/` → implementa puerto de `registro/domain/ports/`
- `registro/api/` → solo importa `registro/application/`
- Comunicación con Identidad: soft reference por `atleta_id = usuario_id` — sin FK real, sin import cross-BC

---

## Commit final

```
feat(registro): BC Registro — aggregate Atleta + CRUD [US-3.2.2]
```
