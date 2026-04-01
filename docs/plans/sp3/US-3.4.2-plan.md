# Plan de Implementación — US-3.4.2

**US:** Auth por rol: middleware JWT en APIs
**Fecha:** 2026-04-01
**Incremento:** INC-3.4

---

## Contexto

Los endpoints de performances (AP/resultado/tarjeta) no existen como HTTP en SP3 — se
ejecutan via application layer. El auth se aplica a los endpoints HTTP existentes.

---

## Artefactos a modificar

| Artefacto | Acción |
|-----------|--------|
| `identidad/api/dependencies.py` | Agregar `require_rol()`, `OrganizadorDep`, `JuezDep`, `AtletaDep` |
| `torneo/api/router.py` | Proteger POST/PUT; GET público |
| `registro/api/router.py` | Proteger POST/DELETE con AtletaDep; GET inscriptos con OrganizadorDep |
| `competencia/api/router.py` | Proteger POST configurar/ajustar/confirmar/iniciar; GET público |
| Tests de integración (torneo, registro, competencia) | Agregar `dependency_overrides` |

---

## Tareas

### T1 — `require_rol()` en dependencies.py (10 min)
```python
def require_rol(*roles: Rol) -> Callable:
    def _dep(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["rol"] not in [r.value for r in roles]:
            raise HTTPException(status_code=403, detail="Rol insuficiente")
        return current_user
    return _dep

OrganizadorDep = Annotated[dict, Depends(require_rol(Rol.ORGANIZADOR, Rol.ADMIN))]
JuezDep        = Annotated[dict, Depends(require_rol(Rol.JUEZ, Rol.ORGANIZADOR, Rol.ADMIN))]
AtletaDep      = Annotated[dict, Depends(require_rol(Rol.ATLETA, Rol.ADMIN))]
```

### T2 — Proteger Torneo router (10 min)
- `POST /torneos` → `OrganizadorDep`
- `PUT /torneos/{id}/*` (todas las transiciones) → `OrganizadorDep`
- `PUT /torneos/{id}/disciplinas*` → `OrganizadorDep`
- `GET /torneos`, `GET /torneos/{id}`, `GET /torneos/{id}/disciplinas` → público
- `GET /torneos/{id}/jueces/{juez_id}/disciplinas` → público

### T3 — Proteger Registro router (5 min)
- `POST /registro/atletas` → `AtletaDep`
- `POST /registro/inscripciones` → `AtletaDep`
- `DELETE /registro/inscripciones/{id}` → `AtletaDep`
- `GET /registro/atletas/{id}` → público
- `GET /registro/torneos/{id}/inscriptos` → `OrganizadorDep`

### T4 — Proteger Competencia router (10 min)
- `POST /competencias` → `OrganizadorDep`
- `POST /competencias/{id}/ajustar-grilla` → `OrganizadorDep`
- `POST /competencias/{id}/confirmar-grilla` → `OrganizadorDep`
- `POST /competencias/{id}/iniciar` → `OrganizadorDep`
- `GET /competencias/{id}/grilla` → público
- `GET /competencias`, `GET /competencias/{id}/events` → público (sin restricción extra en SP3)

### T5 — Actualizar tests de integración (15 min)
- Torneo: agregar `dependency_overrides[get_current_user]` con rol ORGANIZADOR
- Registro: idem con rol ATLETA/ORGANIZADOR según endpoint
- Competencia: ya usa `dependency_overrides` — agregar override de `get_current_user`

---

## Notas
- `get_current_user` se importa desde `identidad.api.dependencies` en los 3 BCs
- En tests: `app.dependency_overrides[get_current_user] = lambda: {"sub": "...", "email": "test@test.com", "rol": "ORGANIZADOR"}`
- SP3: no hay autorización por ownership (atleta solo opera sus recursos) — queda para SP4
