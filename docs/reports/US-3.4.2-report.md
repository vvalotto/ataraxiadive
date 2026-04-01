# Reporte US-3.4.2 — Auth por rol: middleware JWT en APIs

**Fecha:** 2026-04-01
**Branch:** feature/US-3.4.2-auth-jwt-middleware
**Incremento:** INC-3.4 (Disciplinas + Auth)

---

## Resumen

Implementación de control de acceso por rol en todos los endpoints escribibles del sistema.
Se introdujo el factory `require_rol()` en `identidad/api/dependencies.py` y tres alias
tipados (`OrganizadorDep`, `JuezDep`, `AtletaDep`) que se usan como parámetros FastAPI
con `Depends()` implícito a través de `Annotated`.

---

## Artefactos Producidos

### Código de producción

| Archivo | Cambio |
|---------|--------|
| `src/identidad/api/dependencies.py` | `require_rol()` factory + `OrganizadorDep`, `JuezDep`, `AtletaDep` |
| `src/torneo/api/router.py` | `OrganizadorDep` en endpoints POST/PUT |
| `src/registro/api/router.py` | `AtletaDep`/`OrganizadorDep` en endpoints protegidos |
| `src/competencia/api/router.py` | `OrganizadorDep` en 4 endpoints POST |

### Tests

| Archivo | Tipo | Tests |
|---------|------|-------|
| `tests/unit/identidad/api/test_dependencies.py` | Unit | 9 |
| `tests/features/steps/test_US_3_4_2_steps.py` | BDD | 6 |
| `tests/features/US-3.4.2-auth-jwt-middleware.feature` | Feature | 6 escenarios |

### Suite total post-US: **724 tests, 0 fallos**

---

## Diseño de `require_rol()`

```python
def require_rol(*roles: Rol) -> Callable:
    _roles_values = {r.value for r in roles}
    def _dep(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if current_user.get("rol") not in _roles_values:
            raise HTTPException(status_code=403, detail="Rol insuficiente")
        return current_user
    return _dep

OrganizadorDep = Annotated[dict, Depends(require_rol(Rol.ORGANIZADOR, Rol.ADMIN))]
JuezDep        = Annotated[dict, Depends(require_rol(Rol.JUEZ, Rol.ORGANIZADOR, Rol.ADMIN))]
AtletaDep      = Annotated[dict, Depends(require_rol(Rol.ATLETA, Rol.ADMIN))]
```

**Decisiones clave:**
- ADMIN pasa cualquier dependencia (superrol)
- JUEZ pasa JuezDep y NO OrganizadorDep (menor privilegio)
- ATLETA solo pasa AtletaDep
- `require_rol()` es un factory puro: no hay estado global, es testeable en aislamiento
- `from __future__ import annotations` debe **omitirse** en tests que usen `dep` como anotación local en endpoints de test (FastAPI usa `get_type_hints()` que no puede resolver strings de variables locales)

---

## Decisión de Testing para JuezDep/AtletaDep

Los endpoints de tarjeta y AP no existen como rutas HTTP en SP3 (solo capa application).
Los escenarios BDD 4 y 5 se implementaron con apps FastAPI mínimas creadas en el step,
replicando el patrón de los tests unitarios. Esto mantiene fidelidad al comportamiento
real de los middlewares sin exponer endpoints ficticios en producción.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Pylint (módulos afectados) | 8.53/10 |
| Black | OK (168 archivos reformateados) |
| Tests unitarios US-3.4.2 | 9/9 ✅ |
| Tests integración | 135/135 ✅ |
| BDD US-3.4.2 | 6/6 ✅ |
| Suite completa | 724/724 ✅ |
