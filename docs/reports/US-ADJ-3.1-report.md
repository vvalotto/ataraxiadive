# Reporte de Implementacion — US-ADJ-3.1
## Extraer `GrillaDeSalida` + eliminar `_DISCIPLINAS_SP3`

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se desacoplo la logica de grilla del aggregate `Competencia` mediante la nueva
entidad `GrillaDeSalida`, manteniendo intactos los comandos publicos, la
persistencia por eventos y la reconstitucion del aggregate.

En paralelo, `Torneo` dejo de restringir disciplinas por sprint: ahora acepta
cualquier `Disciplina` definida en el enum compartido.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/competencia/domain/entities/grilla_de_salida.py` | Dominio | Entidad interna para generar, ajustar y reconstituir la grilla |
| `src/competencia/domain/entities/__init__.py` | Dominio | Export de la nueva entidad |
| `src/competencia/domain/aggregates/competencia.py` | Dominio | Aggregate simplificado para delegar logica de grilla |
| `src/torneo/domain/aggregates/torneo.py` | Dominio | Eliminacion de `_DISCIPLINAS_SP3` |
| `tests/unit/torneo/domain/test_disciplinas_torneo.py` | Unit | Ajuste de cobertura para nueva regla de dominio |
| `docs/plans/sp-adj-03/US-ADJ-3.1-plan.md` | Plan | Plan tecnico de la US sin BDD nueva |

---

## Decisiones Tecnicas

### Grilla como entidad interna

`GrillaDeSalida` encapsula:

- ordenamiento por AP
- asignacion round-robin de andariveles
- swap de posiciones
- recalculo de OTs
- rehidratacion desde payloads de eventos

`Competencia` conserva la responsabilidad de validar precondiciones y emitir
eventos del stream.

### Dominio de Torneo sin conocimiento de sprint

La validez de una disciplina vuelve a depender solo del enum `Disciplina`. La
restriccion `_DISCIPLINAS_SP3` se elimino por ser una allowlist de roadmap
codificada en dominio.

---

## Validacion Ejecutada

| Suite | Resultado |
|------|-----------|
| Unit focalizado (`competencia` + `torneo`) | ✅ 60/60 |
| Integracion focalizada (`competencia` + `torneo`) | ✅ 21/21 |
| `py_compile` | ✅ |
| `git diff --check` | ✅ |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/competencia/domain/test_generar_grilla.py tests/unit/competencia/domain/test_ajustar_grilla.py tests/unit/competencia/domain/test_confirmar_grilla.py tests/unit/torneo/domain/test_disciplinas_torneo.py -q
./.venv/bin/pytest tests/integration/competencia/test_generar_grilla_integration.py tests/integration/competencia/test_ajustar_grilla_integration.py tests/integration/competencia/test_confirmar_grilla_integration.py tests/integration/torneo/test_torneo_domain_integration.py -q
./.venv/bin/python -m py_compile src/competencia/domain/entities/grilla_de_salida.py src/competencia/domain/aggregates/competencia.py src/torneo/domain/aggregates/torneo.py
git diff --check
```

---

## Alcance no incluido

- No se generaron escenarios BDD nuevos por acuerdo explicito para SP-ADJ-03.
- No se ajustaron endpoints ni contratos HTTP.
- No se tocaron migraciones ni persistencia SQLite.

---

## Resultado

`US-ADJ-3.1` queda lista para commit dentro de `SP-ADJ-03`, con refactor
interno validado y la regla OCP de `Torneo` corregida.
