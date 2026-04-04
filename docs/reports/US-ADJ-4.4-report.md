# Reporte de Implementación — US-ADJ-4.4
## Agregar campo `club` al atleta

**Sprint:** SP-ADJ-04
**Branch:** `feature/US-ADJ-4.4-club-atleta`
**Fecha:** 2026-04-03

---

## Resumen

Se extendió el aggregate `Atleta` para incorporar `club` como dato obligatorio de
registro. El campo pasa a formar parte del contrato de alta y consulta de atletas,
se persiste en SQLite y queda reflejado en la documentación mínima del BC Registro.

El ajuste deja alineado el modelo con el dominio real y prepara la propagación de
`club` hacia grillas y reportes en consumidores posteriores.

---

## Cambios implementados

### Código
| Archivo | Cambio |
|---------|--------|
| `src/registro/domain/aggregates/atleta.py` | Agrega `club: str` e invariante `INV-A-05` para rechazar vacío/espacios |
| `src/registro/application/commands/registrar_atleta.py` | Agrega `club` a `RegistrarAtletaCommand` y al armado del aggregate |
| `src/registro/infrastructure/repositories/sqlite_atleta_repository.py` | Persiste/rehidrata `club` y lo incorpora al esquema SQLite |
| `src/registro/api/router.py` | Expone `club` en `RegistrarAtletaRequest` y `AtletaResponse` |

### Tests
| Archivo | Cambio |
|---------|--------|
| `tests/unit/registro/test_atleta.py` | Casos válidos e inválidos para `club` |
| `tests/unit/registro/test_registrar_atleta_handler.py` | Commands/aggregates con `club` |
| `tests/unit/registro/test_obtener_atleta_handler.py` | Fixtures con `club` |
| `tests/integration/registro/test_sqlite_atleta_repository.py` | Persistencia y lectura de `club` |
| `tests/features/steps/test_US_3_2_2_steps.py` | Payloads BDD de registro alineados al nuevo contrato |
| `tests/features/steps/test_US_3_2_3_steps.py` | Seed BDD de atletas para inscripción alineado al nuevo contrato |

### Documentación
| Archivo | Cambio |
|---------|--------|
| `docs/design/domain-model.md` | `Atleta` ahora incluye `club` en su responsabilidad |
| `docs/dominio/05-requerimientos_funcionales.md` | Se explicita que `club` es obligatorio y visible en grillas/reportes |
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | `US-ADJ-4.4` marcada como implementada |

---

## Resultados de calidad

| Gate | Resultado |
|------|-----------|
| Pytest focalizado `registro` + BDD impactados | ✅ 59/59 |
| CodeGuard componentes impactados | ✅ 0 errores, 0 advertencias |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/registro tests/integration/registro tests/features/steps/test_US_3_2_2_steps.py tests/features/steps/test_US_3_2_3_steps.py -q
./.venv/bin/codeguard src/registro/domain src/registro/application src/registro/infrastructure/repositories src/registro/api
```

Observaciones:

- `pytest` emitió 26 warnings deprecados preexistentes vinculados a `datetime.utcnow()`.
- No se detectaron errores ni advertencias nuevas de calidad sobre los componentes modificados.

---

## Riesgos y notas

- La tabla `atletas` se crea con `CREATE TABLE IF NOT EXISTS`; una base SQLite ya
  existente sin columna `club` requerirá migración explícita fuera de esta US.
- La exposición de `club` en grillas/reportes queda habilitada desde el dato fuente
  del BC Registro, pero los read models consumidores se ajustarán en US posteriores.
