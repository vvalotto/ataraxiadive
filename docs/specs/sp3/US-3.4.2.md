# US-3.4.2: Auth por rol — middleware JWT en APIs

**Estado**: `To Do`
**Sprint**: SP3 — El Torneo
**Incremento**: INC-3.4
**Bounded Context**: `identidad` · `torneo` · `competencia` · `registro`
**Capas afectadas**: `identidad/api/dependencies.py` · `torneo/api/router.py` · `competencia/api/router.py` · `registro/api/router.py`

---

## Descripción

Como **sistema**,
quiero **que los endpoints críticos requieran JWT válido y validen el rol del usuario**
para **que solo usuarios autorizados puedan ejecutar operaciones sensibles**.

---

## Especificación

### Precondición

```python
# US-3.2.1: JWTService + get_current_user() en identidad/api/dependencies.py
# Todos los endpoints de Torneo, Registro y Competencia sin auth (acceso libre)
```

### Postcondición

```python
# identidad/api/dependencies.py (extensión de US-3.2.1):

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """Verifica JWT. Retorna {sub, email, rol}. Lanza 401 si inválido o expirado."""
    ...

def require_rol(*roles: Rol) -> Callable:
    """Factory de dependencia que exige uno de los roles dados."""
    def _dep(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["rol"] not in [r.value for r in roles]:
            raise HTTPException(status_code=403, detail="Rol insuficiente")
        return current_user
    return _dep

OrganizadorDep = Annotated[dict, Depends(require_rol(Rol.ORGANIZADOR, Rol.ADMIN))]
JuezDep        = Annotated[dict, Depends(require_rol(Rol.JUEZ, Rol.ORGANIZADOR, Rol.ADMIN))]
AtletaDep      = Annotated[dict, Depends(require_rol(Rol.ATLETA, Rol.ADMIN))]
```

```
Endpoints que requieren auth y rol:

Torneo:
  POST   /torneos                         → OrganizadorDep
  PUT    /torneos/{id}/*                  → OrganizadorDep (todas las transiciones)
  PUT    /torneos/{id}/disciplinas*       → OrganizadorDep
  GET    /torneos, GET /torneos/{id}      → público (sin auth)

Registro:
  POST   /registro/atletas                → AtletaDep (atleta registra sus propios datos)
  POST   /registro/inscripciones          → AtletaDep
  DELETE /registro/inscripciones/{id}     → AtletaDep
  GET    /registro/torneos/{id}/inscriptos → OrganizadorDep

Competencia:
  POST   /competencias                    → OrganizadorDep
  PUT    /competencias/{id}/grilla/*      → OrganizadorDep
  POST   /competencias/{id}/performances/*/ap     → AtletaDep
  POST   /competencias/{id}/performances/*/resultado → JuezDep
  POST   /competencias/{id}/performances/*/tarjeta   → JuezDep
  GET    /competencias/{id}/grilla        → público
  GET    /competencias/{id}/events        → OrganizadorDep | JuezDep
```

### Invariantes

- `INV-AUTH-01`: Token ausente → 401 Unauthorized
- `INV-AUTH-02`: Token inválido o expirado → 401 Unauthorized
- `INV-AUTH-03`: Token válido pero rol insuficiente → 403 Forbidden
- `INV-AUTH-04`: Endpoints de consulta pública (`GET /torneos`, `GET /competencias/{id}/grilla`) siguen funcionando sin token
- `INV-AUTH-05`: Los tests de integración existentes de SP1/SP2 que no pasan token deben usar `dependency_overrides` para omitir auth en el entorno de test

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-3.4.2 — Auth por rol

  Scenario: organizador crea torneo con token válido
    Given token JWT con rol ORGANIZADOR
    When POST /torneos con Authorization: Bearer {token}
    Then 201

  Scenario: atleta intenta crear torneo
    Given token JWT con rol ATLETA
    When POST /torneos con Authorization: Bearer {token}
    Then 403 Forbidden

  Scenario: request sin token a endpoint protegido
    Given no hay header Authorization
    When POST /torneos
    Then 401 Unauthorized

  Scenario: juez registra tarjeta con su token
    Given token JWT con rol JUEZ
    When POST /competencias/{id}/performances/{perf_id}/tarjeta
    Then 200

  Scenario: atleta registra AP con su token
    Given token JWT con rol ATLETA
    When POST /competencias/{id}/performances/{atleta_id}/ap
    Then 201

  Scenario: GET /torneos sin token
    Given no hay header Authorization
    When GET /torneos
    Then 200 (endpoint público)

  Scenario: tests SP1/SP2 siguen pasando
    Given suite de tests con dependency_overrides
    When pytest tests/unit tests/integration tests/features
    Then 100% pass
```

---

## Notas de implementación

- `get_current_user` y `require_rol` viven en `identidad/api/dependencies.py` — los otros BCs importan desde ahí.
- **No** importar de `identidad/domain/` o `identidad/infrastructure/` desde otros BCs — solo de `identidad/api/dependencies.py` (capa API es la interfaz pública).
- En tests: `app.dependency_overrides[get_current_user] = lambda: {"sub": "...", "email": "test@test.com", "rol": "ORGANIZADOR"}`.
- En SP4 se puede agregar verificación del `sub` para que un atleta solo pueda operar sobre sus propios recursos (autorización basada en ownership). Para SP3 basta verificar el rol.

---

## Referencias

- US-3.2.1: JWTService
- Context Map §3.1: Identidad → otros BCs (Conformist)
- Plan: `docs/plans/sp3/PLAN-SP3.md`

---

*Redactado: 2026-03-28 — SP3*
