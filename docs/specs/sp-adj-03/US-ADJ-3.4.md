# US-ADJ-3.4: Mover dependencias de autenticación a `shared/api/dependencies.py`

**Estado**: `To Do`
**Sprint**: SP-ADJ-03 — Ajuste Técnico Post-SP3
**Issues**: ADJ-05
**Bounded Context**: `competencia` · `registro` · `torneo` · `shared`
**Capas afectadas**: `*/api/router.py` (3 BCs) · `shared/api/` (nuevo)

---

## Descripción

Como **desarrollador del sistema**,
quiero **mover `OrganizadorDep`, `AtletaDep` y `JuezDep` a `shared/api/dependencies.py`**
para **eliminar el acoplamiento directo de 3 BCs a `identidad.api.dependencies`**.

---

## Contexto de la deuda

### ADJ-05 — Routers importan `identidad.api` directamente

```python
# competencia/api/router.py:67
from identidad.api.dependencies import OrganizadorDep

# registro/api/router.py:9
from identidad.api.dependencies import AtletaDep, OrganizadorDep

# torneo/api/router.py:10
from identidad.api.dependencies import OrganizadorDep
```

`OrganizadorDep`, `AtletaDep` y `JuezDep` son dependencias de autenticación/autorización
transversales — no pertenecen al BC `identidad` sino al vocabulario compartido de la API.

El resultado actual: 3 BCs tienen un import directo hacia `identidad.api`, creando
acoplamiento en la capa `api/` entre contextos que deberían ser independientes.

Si `identidad.api.dependencies` cambia su ubicación o su firma, los 3 BCs se rompen.

---

## Especificación

### Precondición

| Archivo | Import actual |
|---------|--------------|
| `competencia/api/router.py:67` | `from identidad.api.dependencies import OrganizadorDep` |
| `registro/api/router.py:9` | `from identidad.api.dependencies import AtletaDep, OrganizadorDep` |
| `torneo/api/router.py:10` | `from identidad.api.dependencies import OrganizadorDep` |

### Postcondición

```
shared/api/__init__.py             ← NUEVO (paquete vacío)
shared/api/dependencies.py         ← NUEVO
```

```python
# shared/api/dependencies.py
"""Dependencias FastAPI transversales — autorización por rol."""
from identidad.api.dependencies import AtletaDep, JuezDep, OrganizadorDep

__all__ = ["AtletaDep", "JuezDep", "OrganizadorDep"]
```

Los 3 routers actualizan su import:

```python
# competencia/api/router.py, registro/api/router.py, torneo/api/router.py
from shared.api.dependencies import OrganizadorDep   # (o AtletaDep / JuezDep según el router)
```

`identidad/api/dependencies.py` no se modifica — sigue siendo la implementación.
`shared/api/dependencies.py` es el punto de re-exportación transversal.

### Invariantes

- `INV-ADJ-3.4-1`: el comportamiento de autorización es idéntico — mismo código, solo cambia el import path
- `INV-ADJ-3.4-2`: ningún BC distinto de `identidad` importa directamente desde `identidad.api.dependencies`
- `INV-ADJ-3.4-3`: todos los tests de autorización pasan sin modificación

---

## Criterios de aceptación

```gherkin
Scenario: ningún router importa identidad.api.dependencies directamente
  Given los routers de competencia, registro y torneo refactorizados
  Then grep "identidad.api.dependencies" en esos 3 archivos retorna cero matches

Scenario: shared/api/dependencies.py existe y re-exporta las dependencias
  Given el archivo shared/api/dependencies.py
  Then exporta OrganizadorDep, AtletaDep, JuezDep
  And los importa desde identidad.api.dependencies

Scenario: la autorización sigue funcionando en los 3 BCs
  Given un endpoint de competencia, registro o torneo que requiere OrganizadorDep
  When se llama sin token JWT válido
  Then retorna 401 Unauthorized
  When se llama con token de rol incorrecto
  Then retorna 403 Forbidden
  When se llama con token de Organizador válido
  Then retorna 200
```

---

## Notas de implementación

- Crear `src/shared/api/` como nuevo subdirectorio de `shared/`. No existe aún.
- `shared/api/dependencies.py` solo re-exporta — no implementa. La implementación
  (JWT, bcrypt, FastAPI OAuth2) sigue en `identidad/`.
- `JuezDep` también debe estar en `shared/api/` aunque hoy solo `competencia` lo usa —
  es transversal y el patrón debe ser consistente.
- Esta US es **independiente de US-ADJ-3.6** — US-ADJ-3.6 refactoriza la implementación
  interna de identidad; esta US solo mueve el punto de importación.

---

## Referencias

- Revisión de consistencia SP3: `.work/revision-sp3/05-revision-consistencia-sp3.md` (B-01)
- Issues consolidados: `.work/revision-sp3/07-issues-consolidados.md` (ADJ-05)
- Plan SP-ADJ-03: `docs/plans/sp-adj-03/PLAN-SP-ADJ-03.md`
- CLAUDE.md §6 — Regla de Oro: ningún BC importa de otro BC en capa `api/`

---

*Redactado: 2026-04-03 — SP-ADJ-03*
