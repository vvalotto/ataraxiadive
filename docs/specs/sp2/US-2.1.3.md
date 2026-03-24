# US-2.1.3: Ajustar Grilla Manualmente

**Estado**: `Backlog`
**Incremento**: Inc 2.1 — La Grilla de Salida
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Competencia`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **organizador**,
quiero **modificar manualmente el orden o andarivel de uno o más atletas en la grilla**
para **ajustar la grilla generada automáticamente antes de confirmarla**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Aplica ajustes manuales sobre la grilla generada, recalcula OTs si cambia la posición |
| Domain Event | `GrillaDeSalidaAjustada` | Registra los cambios puntuales: qué campo cambió, valor anterior y nuevo |

### Lenguaje ubicuo relevante

- **Ajuste de grilla**: modificación manual de posición y/o andarivel de un atleta, a diferencia de la generación automática que ordena por AP.
- **OT recalculado**: si se cambia la posición de un atleta, su OT se recalcula según P-02.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-C-02** (parcial): `AjustarGrilla` no está permitido después de `GrillaConfirmada`. Una vez confirmada, la grilla es inmutable (v1).
- La grilla debe haber sido generada (`GrillaDeSalidaGenerada` emitido) antes de poder ajustarse.

### Operación principal

**Nombre**: `ajustar_grilla(cambios: list[CambioGrilla])`

donde `CambioGrilla = {performanceId, campo: "posicion"|"andarivel", valor_nuevo}`

| | Descripción |
|---|---|
| **Precondición** | La grilla fue generada. La grilla **no** está confirmada (`GrillaConfirmada` no emitido). |
| **Postcondición** | `GrillaDeSalidaAjustada` persiste con los cambios aplicados. Read Model actualizado. Si se modificó la posición, los OTs se recalculan para todos los atletas afectados. |
| **Eventos generados** | `GrillaDeSalidaAjustada` |
| **Excepciones** | `GrillaNoGenerada` · `GrillaYaConfirmada` (INV-C-02) · `PerformanceNoEncontrada` |

**Ejemplo concreto:**

```
Estado previo: grilla con A002(pos=1), A001(pos=2), A003(pos=3), intervaloDisciplina=9min

Operación: ajustar_grilla([{performanceId_A001, campo="posicion", valor_nuevo=1}])
           (intercambiar A001 y A002)

Resultado:
  A001 → pos=1, OT=10:00:00
  A002 → pos=2, OT=10:09:00
  A003 → pos=3 (sin cambio)

Evento: GrillaDeSalidaAjustada{
  competenciaId="C001",
  cambios=[
    {performanceId: P_A001, campo: "posicion", valorAnterior: 2, valorNuevo: 1},
    {performanceId: P_A002, campo: "posicion", valorAnterior: 1, valorNuevo: 2},
  ],
  ajustadaEn=<timestamp>
}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Ajustar Grilla Manualmente

  Background:
    Given una competencia "C001" con grilla generada (3 atletas: A002 pos=1, A001 pos=2, A003 pos=3)
    And la grilla no está confirmada

  Scenario: Ajustar posición de un atleta
    When el organizador mueve A001 a la posición 1
    Then la grilla queda: A001 pos=1, A002 pos=2, A003 pos=3
    And los OTs se recalculan según el nuevo orden
    And el evento GrillaDeSalidaAjustada persiste con los cambios

  Scenario: Ajustar andarivel de un atleta
    When el organizador asigna andarivel 2 al atleta A002
    Then A002 queda en andarivel=2
    And los demás atletas no se ven afectados
    And el evento GrillaDeSalidaAjustada persiste

  Scenario: Ajuste acumulativo sobre ajuste previo
    Given ya existe un GrillaDeSalidaAjustada previo
    When el organizador realiza otro ajuste
    Then se emite un nuevo GrillaDeSalidaAjustada
    And el Read Model refleja el estado final acumulado

  Scenario: Rechazo — grilla no generada aún
    Given una competencia sin GrillaDeSalidaGenerada
    When el organizador intenta ajustar la grilla
    Then el sistema rechaza con error "GrillaNoGenerada"

  Scenario: Rechazo — grilla ya confirmada (INV-C-02)
    Given la grilla ya fue confirmada
    When el organizador intenta ajustar la grilla
    Then el sistema rechaza con error "GrillaYaConfirmada"
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — sigue el mismo patrón de command/event/handler

**Capas afectadas:**
- [x] Domain — `Competencia.ajustar_grilla()`, `GrillaDeSalidaAjustada` event
- [x] Application — `AjustarGrillaHandler`
- [ ] Infrastructure — sin cambios
- [ ] API — endpoints en US-2.1.4

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 1
- Invariante: INV-C-02 (parcial); Hot Spot HS-P1 (resuelto)
- RF: RF-PR-07
- `docs/plans/sp2/SP2-candidatas.md` — Inc 2.1

---

*Redactado: 2026-03-24 — IEDD Capa 3*
