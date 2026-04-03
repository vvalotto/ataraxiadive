# Reporte de Implementacion — US-ADJ-3.4
## Mover dependencias de autenticacion a `shared/api/dependencies.py`

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se elimino el acoplamiento directo de los routers de `competencia`,
`registro` y `torneo` con `identidad.api.dependencies`.

El punto transversal de importacion ahora vive en
`shared/api/dependencies.py`, que re-exporta `OrganizadorDep`, `AtletaDep` y
`JuezDep` sin mover la implementacion concreta de auth fuera del BC
`identidad`.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/shared/api/__init__.py` | Shared | Nuevo paquete transversal de API |
| `src/shared/api/dependencies.py` | Shared | Re-export de dependencias auth compartidas |
| `src/competencia/api/router.py` | API | Import actualizado hacia `shared.api.dependencies` |
| `src/registro/api/router.py` | API | Import actualizado hacia `shared.api.dependencies` |
| `src/torneo/api/router.py` | API | Import actualizado hacia `shared.api.dependencies` |
| `docs/plans/sp-adj-03/US-ADJ-3.4-plan.md` | Plan | Plan tecnico aprobado |
| `quality/reports/codeguard/US-ADJ-3.4-quality.txt` | Quality gate | Evidencia de CodeGuard sobre shared/api y routers impactados |

---

## Decisiones Tecnicas

### Re-export transversal

`shared/api/dependencies.py` no implementa autenticacion; solo centraliza el
path de importacion transversal para otros BCs.

Con esto:

- `identidad` conserva la implementacion concreta
- `competencia`, `registro` y `torneo` dejan de depender de `identidad.api`
  directamente
- el cambio queda reducido a frontera de imports, sin afectar la semantica de
  autorizacion

### Composition root sin cambios

`src/app.py` no se modifico en esta US. El composition root puede seguir
importando configuracion concreta de `identidad`, porque no es un BC consumidor
sino el ensamblador de la aplicacion.

---

## Invariantes Verificadas

| ID | Descripcion | Estado |
|----|-------------|--------|
| `INV-ADJ-3.4-1` | El comportamiento de autorizacion permanece igual | ✅ |
| `INV-ADJ-3.4-2` | `competencia`, `registro` y `torneo` ya no importan `identidad.api.dependencies` | ✅ |
| `INV-ADJ-3.4-3` | Los tests existentes de autorizacion siguen pasando | ✅ |

---

## Validacion Ejecutada

| Suite / Gate | Resultado |
|-------------|-----------|
| `tests/unit/identidad/api/test_dependencies.py` | ✅ |
| `tests/integration/torneo/test_disciplinas_torneo_api.py` | ✅ |
| `py_compile` sobre archivos impactados | ✅ |
| `grep -R "from identidad.api.dependencies" src/competencia src/registro src/torneo` | ✅ 0 matches |
| `git diff --check` | ✅ |
| `CodeGuard` sobre `shared/api` + routers impactados | ✅ 0 errores, 0 warnings |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/identidad/api/test_dependencies.py tests/integration/torneo/test_disciplinas_torneo_api.py -q
./.venv/bin/python -m py_compile src/shared/api/__init__.py src/shared/api/dependencies.py src/competencia/api/router.py src/registro/api/router.py src/torneo/api/router.py
grep -R "from identidad.api.dependencies" src/competencia src/registro src/torneo
git diff --check
./.venv/bin/codeguard src/shared/api/dependencies.py src/competencia/api/router.py src/registro/api/router.py src/torneo/api/router.py
```

---

## Observacion metodologica

No se generaron activos BDD para esta US por instruccion explicita del sprint
de ajuste. La validacion observable se sostuvo con tests existentes de auth y
router mas chequeo estructural de imports.

---

## Resultado

`US-ADJ-3.4` queda cerrada funcionalmente: el acoplamiento cross-BC en capa
`api/` se redujo al punto de re-export compartido y el comportamiento de
autorizacion se mantiene intacto.
