# Plan de Implementación — US-ADJ-4.4
## Agregar campo `club` al atleta

**Branch:** `feature/US-ADJ-4.4-club-atleta`
**Sprint:** SP-ADJ-04

---

## Cambios identificados

### src/ (4 archivos)
| Archivo | Cambio |
|---------|--------|
| `src/registro/domain/aggregates/atleta.py` | Agregar `club: str` y validar `INV-A-05` en `__post_init__` |
| `src/registro/application/commands/registrar_atleta.py` | Agregar `club` a `RegistrarAtletaCommand` y al armado del aggregate |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Agregar columna `club` en `CREATE TABLE`, `INSERT`, `SELECT` y rehidratación |
| `src/registro/api/router.py` | Agregar `club` a `RegistrarAtletaRequest` y `AtletaResponse`; incluirlo en POST/GET |

### tests/ (impacto esperado: medio)
| Archivo | Cambio |
|---------|--------|
| `tests/unit/registro/test_atleta.py` | Casos válidos e inválidos para `club` |
| `tests/unit/registro/test_registrar_atleta_handler.py` | Commands y aggregates con `club` |
| `tests/unit/registro/test_obtener_atleta_handler.py` | Fixtures con `club` |
| `tests/integration/registro/test_sqlite_atleta_repository.py` | Persistencia/rehidratación de `club` |
| `tests/**/registro*` | Buscar cualquier factory/fixture de `Atleta` o `RegistrarAtletaCommand` sin `club` |

### docs/ (mínimas de la US)
| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | Marcar progreso cuando la US cierre |
| `docs/reports/US-ADJ-4.4-report.md` | Evidencia de implementación |
| `docs/design/domain-model.md` | Atleta incluye `club` |
| `docs/dominio/05-requerimientos_funcionales.md` | Reflejar `club` como dato obligatorio si corresponde |

---

## Tareas de implementación

1. **[T1]** Extender `Atleta` con `club` y validar vacío/espacios
2. **[T2]** Extender `RegistrarAtletaCommand` y handler
3. **[T3]** Adaptar persistencia SQLite de atletas
4. **[T4]** Adaptar request/response HTTP de registro de atletas
5. **[T5]** Actualizar documentación mínima de la US si cambia contrato visible

---

## Validación pipeline

1. Ejecutar `pytest` focalizado sobre `registro`
2. Ejecutar `codeguard` sobre componentes impactados (`src/registro`)
3. Crear reporte de implementación
4. Actualizar tracking y cerrar la US

---

## Riesgos

- El cambio rompe cualquier factory de `Atleta` o `RegistrarAtletaCommand` que no provea `club`.
- La tabla `atletas` usa `CREATE TABLE IF NOT EXISTS`; en DBs persistentes viejas no habrá migración automática de columna. En tests con DB temporal no bloquea.
- La parte “grillas/reportes” hoy no parece tener implementación directa en `registro`; puede quedar documentada pero no ejercitable aún si no existe un read model consumidor.

---

## Notas

- Esta US sí cambia contrato API y persistencia.
- No implementar hasta cerrar esta fase 2 con aprobación explícita.
