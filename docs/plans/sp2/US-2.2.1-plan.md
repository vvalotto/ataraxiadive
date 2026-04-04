# Plan de Implementación: US-2.2.1 — DisciplinaDescriptor VO + Port

**Patrón:** Hexagonal DDD (BC-first)
**Producto:** ataraxiadive
**BC:** competencia
**Estimación Total:** 55 min

---

## Componentes a Implementar

### 1. Domain — Value Object

- [ ] `src/competencia/domain/value_objects/disciplina_descriptor.py` (10 min)
  - `DisciplinaDescriptor` dataclass inmutable (frozen)
  - Campos: `disciplina: Disciplina`, `unidad_esperada: UnidadMedida`, `orden_ascendente: bool`
  - Factory method de clase `para(disciplina)` que construye el descriptor correcto
  - Invariante: STA → Segundos + orden_ascendente=True; distancia → Metros + orden_ascendente=True

### 2. Domain — Port

- [ ] `src/competencia/domain/ports/disciplina_descriptor_port.py` (5 min)
  - `DisciplinaDescriptorPort` ABC con método `describe(disciplina: Disciplina) -> DisciplinaDescriptor`

### 3. Infrastructure — Adapter

- [ ] `src/competencia/infrastructure/repositories/disciplina_descriptor_adapter.py` (10 min)
  - `DisciplinaDescriptorAdapter` implementa `DisciplinaDescriptorPort`
  - Sin I/O: deriva el descriptor directamente del enum `Disciplina` via `DisciplinaDescriptor.para()`

### 4. Domain — Refactor aggregate

- [ ] `src/competencia/domain/aggregates/competencia.py` (15 min)
  - `_ordenar_performances(performances, descriptor: DisciplinaDescriptor)` — reemplaza `disciplina` por `descriptor`
  - `generar_grilla(..., descriptor: DisciplinaDescriptor)` — nuevo parámetro
  - Eliminar uso directo de `disciplina.es_tiempo()` en `_ordenar_performances`

### 5. Application — Refactor handler

- [ ] `src/competencia/application/commands/generar_grilla.py` (10 min)
  - `GenerarGrillaHandler.__init__` recibe `DisciplinaDescriptorPort` como tercer parámetro
  - `handle()` llama `port.describe(command.disciplina)` y pasa el descriptor a `competencia.generar_grilla()`

### 6. Domain — Actualizar exports

- [ ] `src/competencia/domain/value_objects/__init__.py` (2 min)
  - Agregar `DisciplinaDescriptor` al `__init__`
- [ ] `src/competencia/domain/ports/__init__.py` o similar (2 min)
  - Agregar `DisciplinaDescriptorPort` si corresponde

---

## Tests

### 7. Unit tests — DisciplinaDescriptor VO

- [ ] `tests/unit/competencia/domain/value_objects/test_disciplina_descriptor.py` (10 min)
  - Descriptor STA: unidad=Segundos, orden_ascendente=True
  - Descriptor por cada disciplina de distancia: unidad=Metros, orden_ascendente=True
  - Factory method cubre todas las disciplinas del enum

### 8. Unit tests — DisciplinaDescriptorAdapter

- [ ] `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py` (8 min)
  - `describe(STA)` → descriptor correcto
  - `describe(DNF)` → descriptor correcto
  - Todas las disciplinas retornan descriptor coherente

### 9. Integration tests — GenerarGrillaHandler con adapter real

- [ ] `tests/integration/competencia/test_generar_grilla_integration.py` (ampliar, 10 min)
  - Nuevo test: grilla STA ordenada menor→mayor AP usando adapter real
  - Nuevo test: grilla DNF ordenada menor→mayor AP usando adapter real

### 10. BDD steps

- [ ] `tests/features/steps/disciplina_descriptor_steps.py` (12 min)
  - Steps para `US-2.2.1-disciplina-descriptor.feature`

---

## Validación

- [ ] Ejecutar suite completa — todos los tests existentes deben seguir pasando (0 regresiones)
- [ ] `codeguard src/` — sin nuevas advertencias CRITICAL
- [ ] Cobertura ≥ 90% en los archivos nuevos

---

**Estado:** ✅ COMPLETADO
**Fecha completado:** 2026-03-26

---

## Métricas de Tiempo

| Tarea/Fase | Estimado | Real |
|------------|----------|------|
| T1 DisciplinaDescriptor VO | 10 min | ~5 min |
| T2 Port | 5 min | ~5 min |
| T3 Adapter | 10 min | ~5 min |
| T4 Refactor aggregate | 15 min | ~10 min |
| T5 Refactor handler | 10 min | ~5 min |
| T6 Exports | 2 min | ~2 min |
| T7-T8 Unit tests | 18 min | ~8 min |
| T9 Integration tests | 10 min | ~7 min |
| T10 BDD steps | 12 min | ~7 min |
| Actualizar tests existentes (17 archivos) | — | ~15 min |
| **Total** | **55 min** | **~69 min** |

## Lecciones Aprendidas

- ✅ El patrón Port+Adapter para un VO sin I/O resulta en un adapter de ~10 líneas — overhead mínimo, ganancia en desacoplamiento real
- ⚠️ Al agregar un parámetro a `generar_grilla()`, 17 archivos de tests necesitaron actualización — el impacto horizontal fue mayor al estimado
- 💡 `RegistrarAPCommand` usa `participante_id`, no `atleta_id` — recordar consistencia de naming al escribir tests de integración nuevos

---

*Generado: 2026-03-26 — Fase 2 /implement-us*
