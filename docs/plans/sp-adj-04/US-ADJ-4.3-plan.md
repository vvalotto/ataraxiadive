# Plan de Implementación — US-ADJ-4.3
## Renombrar categoría JUVENIL → JUNIOR

**Branch:** `feature/US-ADJ-4.3-junior-categoria`
**Sprint:** SP-ADJ-04

---

## Cambios identificados

### src/ (3 archivos)
| Archivo | Cambio |
|---------|--------|
| `src/registro/domain/value_objects/categoria.py` | Renombrar `JUVENIL_MASCULINO/FEMENINO` → `JUNIOR_MASCULINO/FEMENINO` |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Sin cambio estructural; validar que persiste/rehidrata `Categoria` por string y sigue funcionando con los nuevos values |
| `src/registro/api/router.py` | Sin cambio de lógica; verificar que `Categoria` en request/response expone los nuevos values automáticamente |

### tests/ (impacto esperado: bajo)
| Archivo | Cambio |
|---------|--------|
| `tests/**` | Buscar y actualizar cualquier fixture, payload o assert que todavía use `JUVENIL_*` |

### docs/ (históricas + sprint actual)
| Archivo | Cambio |
|---------|--------|
| `docs/specs/sp-adj-04/US-ADJ-4.3.md` | Mantener como spec fuente de verdad; no debería requerir cambio funcional |
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | Marcar progreso cuando la US quede implementada |
| `docs/design/domain-model.md` | `Categoria`: `JUVENIL_*` → `JUNIOR_*` |
| `docs/dominio/05-requerimientos_funcionales.md` | Corregir referencias a juvenil si aparecen |
| `docs/specs/sp3/US-3.2.2.md` | Alinear ejemplo/especificación histórica |
| `docs/plans/sp3/US-3.2.2-plan.md` | Alinear inventario histórico |
| `docs/traceability/matrix.md` | Actualizar estado de `US-ADJ-4.3` al cerrar |
| `CLAUDE.md` | Agregar/ajustar lenguaje ubicuo `JUNIOR` si corresponde |

---

## Tareas de implementación

1. **[T1]** Renombrar enum values en `Categoria`
2. **[T2]** Buscar y actualizar tests/fixtures con `JUVENIL_*`
3. **[T3]** Verificar persistencia SQLite y contrato API con `Categoria` renombrada
4. **[T4]** Corregir documentación y artefactos históricos mínimos
5. **[T5]** Ejecutar pytest focalizado sobre `registro`
6. **[T6]** Ejecutar `codeguard` sobre componentes impactados (`src/registro/domain/value_objects` y, si hace falta, `src/registro`)
7. **[T7]** Crear reporte de implementación y actualizar tracking

---

## Riesgos

- El rename cambia el string persistido en SQLite; los tests con DB temporal no requieren migración, pero cualquier dataset viejo con `JUVENIL_*` dejaría de rehidratar.
- Si hay payloads HTTP o fixtures hardcodeados fuera de `registro`, el impacto puede ser más horizontal de lo que muestra el grep inicial.

---

## Notas

- Esta US es de lenguaje ubicuo, no de comportamiento.
- La secuencia debe respetar el gate de fase 2: no implementar hasta tener aprobación explícita.
