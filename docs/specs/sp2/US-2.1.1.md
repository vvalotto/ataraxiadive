# US-2.1.1: Scaffold Aggregate Competencia + ConfigurarIntervaloOT

**Estado**: `Backlog`
**Incremento**: Inc 2.1 — La Grilla de Salida
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Competencia`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **organizador o juez**,
quiero **configurar el intervalo de tiempo entre Official Tops para una competencia**
para **que el sistema pueda calcular los OTs de cada atleta al generar la grilla**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Gestiona el ciclo de vida de una disciplina: Preparacion → Confirmada → EnEjecucion → Finalizada |
| Value Object | `IntervaloDisciplina` | Tiempo en minutos entre OTs consecutivos |
| Value Object | `EstadoCompetencia` | Máquina de estados: `Preparacion → Confirmada → EnEjecucion → Finalizada` |
| Domain Event | `IntervaloOTConfigurado` | Señala que el intervalo fue establecido (o reconfigurado) para esta competencia |

### Lenguaje ubicuo relevante

- **OT (Official Top)**: momento exacto en que el atleta inicia su performance. Cada atleta tiene su OT calculado.
- **IntervaloDisciplina**: tiempo en minutos entre OTs consecutivos. Configurable por competencia.
- **Competencia**: aggregate que agrupa todas las performances de una disciplina en un torneo. Es el dueño de la grilla.
- **Grilla de Salida**: lista ordenada de atletas con su posición, andarivel y OT asignado.

---

## Nota sobre deuda SOLID (incluida en esta US)

Esta US liquida la deuda SOLID identificada en la retrospectiva de SP1:

| Deuda | Resolución |
|-------|-----------|
| **DIP en `router.py`**: instancia dependencias directamente | Introducir inyección de dependencias via FastAPI `Depends()` — el router recibe handlers/ports como parámetros |
| **OCP en `_apply_stored` de `Performance`**: cadena if/elif | Refactorizar a dispatch por tipo de evento usando un dict o método en cada evento |

El refactor no modifica el comportamiento observable — todos los tests de SP1 deben seguir pasando.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-C-01**: `intervaloDisciplina` debe estar configurado antes de `GenerarGrilla`. Si se intenta generar la grilla sin intervalo configurado → excepción `IntervaloNoConfigurado`.

### Operación principal

**Nombre**: `configurar_intervalo_ot(intervalo_minutos: int)`

| | Descripción |
|---|---|
| **Precondición** | La Competencia existe y está en estado `Preparacion`. |
| **Postcondición** | Evento `IntervaloOTConfigurado` persiste en el stream `competencia-{id}`. La Competencia mantiene estado `Preparacion`. |
| **Eventos generados** | `IntervaloOTConfigurado` |
| **Excepciones** | `IntervaloInvalido` si `intervalo_minutos <= 0` |

> **Nota:** la operación es repetible. Si ya existe un `IntervaloOTConfigurado` previo,
> se emite uno nuevo con el valor actualizado. Los OTs de la grilla quedan desactualizados
> hasta regenerar (P-03). Si la grilla ya está confirmada (`GrillaConfirmada` emitido),
> `ConfigurarIntervaloOT` **no está permitido** — la grilla está congelada.

**Ejemplo concreto:**

```
Precondición:  Competencia C001 en estado Preparacion, sin intervalo previo
Operación:     configurar_intervalo_ot(intervalo_minutos=9)
Postcondición: Competencia tiene intervaloDisciplina=9
Evento:        IntervaloOTConfigurado{
                 competenciaId="C001", disciplina="STA",
                 intervaloDisciplina=9, configuradoPor="organizador-01"
               }
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Configurar Intervalo OT de Competencia

  Background:
    Given una competencia con id "C001" en estado "Preparacion"
    And la disciplina es "STA"

  Scenario: Configurar intervalo exitosamente
    Given no existe un intervalo previo configurado
    When el organizador configura el intervalo en 9 minutos
    Then el intervalo queda registrado en 9 minutos
    And el evento IntervaloOTConfigurado persiste en el stream
    And la competencia sigue en estado "Preparacion"

  Scenario: Reconfigurar intervalo (repetición permitida)
    Given ya existe un IntervaloOTConfigurado de 7 minutos
    When el organizador reconfigura el intervalo a 10 minutos
    Then el nuevo IntervaloOTConfigurado persiste con valor 10
    And el intervalo activo de la competencia es 10 minutos

  Scenario: Rechazo — intervalo cero o negativo
    When el organizador intenta configurar el intervalo en 0 minutos
    Then el sistema rechaza la operación con error "IntervaloInvalido"

  Scenario: Rechazo — grilla ya confirmada
    Given la grilla ya fue confirmada para esta competencia
    When el organizador intenta reconfigurar el intervalo
    Then el sistema rechaza la operación con error "GrillaYaConfirmada"
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] Sí — introduce el segundo aggregate con Event Sourcing en BC Competencia

**Capas afectadas:**
- [x] Domain — `Competencia` aggregate, value objects (`IntervaloDisciplina`, `EstadoCompetencia`), `IntervaloOTConfigurado` event
- [x] Application — `ConfigurarIntervaloOTHandler` command handler
- [x] Infrastructure — nuevo stream `competencia-{id}` en `SQLiteEventStore` (misma tabla `events`, distinto stream prefix)
- [ ] API — endpoints se añaden en US-2.1.4

**Refactors incluidos (deuda SP1):**
- `router.py`: DIP — inyección via `Depends()`
- `Performance._apply_stored`: OCP — dispatch por tipo

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 1, US-C-01
- Invariantes: INV-C-01, INV-C-02 (parcial)
- Políticas: P-03 (OTs desactualizados si se reconfigura intervalo)
- `docs/plans/sp2/SP2-candidatas.md` — Inc 2.1

---

*Redactado: 2026-03-24 — IEDD Capa 3*
