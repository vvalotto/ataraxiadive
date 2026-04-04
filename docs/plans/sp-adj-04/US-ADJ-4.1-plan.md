# Plan de Implementación — US-ADJ-4.1
## Renombrar disciplinas DYNB→DBF y SPE2X50→SPE

**Branch:** `feature/US-ADJ-4.1-renombrar-disciplinas`
**Sprint:** SP-ADJ-04

---

## Cambios identificados

### src/ (1 archivo)
| Archivo | Cambio |
|---------|--------|
| `src/shared/domain/value_objects/disciplina.py` | `DYNB = "DYNB"` → `DBF = "DBF"` · `SPE2X50 = "SPE2X50"` → `SPE = "SPE"` · Actualizar docstring |

### tests/ (7 archivos)
| Archivo | Cambio |
|---------|--------|
| `tests/unit/torneo/domain/test_disciplinas_torneo.py` | `Disciplina.DYNB` → `Disciplina.DBF`, `Disciplina.SPE2X50` → `Disciplina.SPE` |
| `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py` | Ídem |
| `tests/unit/competencia/domain/test_disciplina_descriptor.py` | Ídem |
| `tests/integration/torneo/test_disciplinas_torneo_api.py` | `"DYNB"` → `"DBF"`, `"SPE2X50"` → `"SPE"` |
| `tests/features/steps/test_US_3_4_1_steps.py` | Ídem |
| `tests/features/US-3.4.1-asignar-disciplinas-juez.feature` | Strings de disciplinas |
| `tests/features/US-2.2.1-disciplina-descriptor.feature` | Strings de disciplinas |

### docs/ (2 archivos — solo los requeridos por la spec)
| Archivo | Cambio |
|---------|--------|
| `docs/design/domain-model.md` | Tabla Disciplina: `DYNB` → `DBF`, `SPE2X50` → `SPE` |
| `docs/dominio/05-requerimientos_funcionales.md` | RF-GT-02: `"DBF, SPE2X50"` → `"DBF, SPE"` |

---

## Tareas de implementación

1. **[T1]** Editar `disciplina.py` — renombrar enum values y actualizar docstring
2. **[T2]** Actualizar 7 archivos de tests con `replace_all`
3. **[T3]** Actualizar 2 archivos de docs
4. **[T4]** Ejecutar `pytest` — suite completa debe pasar sin errores
5. **[T5]** Implementar BDD steps para el feature file de esta US
6. **[T6]** Ejecutar `codeguard` — sin issues nuevos

---

## Notas
- No hay migración de DB (SQLite en memoria en tests)
- No hay cambio de comportamiento — solo renombrado de símbolos
- Los docs históricos (specs, planes, event-storming, ADRs) no se tocan
