# US-1.2.2: Llamar Atleta

**Estado**: `Pendiente`
**Incremento**: Inc 1.2 — El Dominio Habla
**Subproyecto**: SP1 — La Performance
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **sistema de gestión de competencia**,
quiero **llamar a un atleta según el orden de grilla para que inicie su performance**
para **dar inicio formal al OT y registrar el momento en que la competencia pasa a esperar la actuación del atleta**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Gestiona el ciclo de vida — aquí transiciona de `AnunciadaAP` a `Llamada` |
| Value Object | `EstadoPerformance` | Máquina de estados: `AnunciadaAP → Llamada → Ejecutada / DNS` |
| Domain Event | `AtletaLlamado` | Señala que el atleta fue convocado, su OT está programado |
| Port | `CompetenciaEstadoPort` | Consulta si la Competencia está en estado `EnEjecucion` (INV-P-05) |

### Lenguaje ubicuo relevante

- **OT (Official Top)**: el momento exacto (horario) en que comienza la actuación del atleta.
- **Llamada**: estado en que la Performance entra cuando el atleta es convocado. A partir de aquí puede DNS o registrar resultado.
- **posicionGrilla**: número de orden del atleta en la grilla de salida.
- **EnEjecucion**: estado del aggregate Competencia mientras se ejecutan las Performances.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-P-05**: `AtletaLlamado` solo permitido si Competencia en estado `EnEjecucion`.

### Precondición de estado

- Performance en estado `AnunciadaAP` (si está en otro estado, la operación es inválida).

### Operación principal

**Nombre**: `llamar(ot_programado: datetime, posicion_grilla: int)`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `AnunciadaAP`. Competencia en estado `EnEjecucion` (INV-P-05). |
| **Postcondición** | Evento `AtletaLlamado` persiste en el stream de la Performance. El aggregate pasa al estado `Llamada`. |
| **Eventos generados** | `AtletaLlamado` |
| **Excepciones** | `EstadoInvalidoParaLlamar` (Performance no está en `AnunciadaAP`) · `CompetenciaNoEnEjecucion` (INV-P-05) |

**Ejemplo concreto:**

```
Precondición:  Performance P001 en estado AnunciadaAP. Competencia en EnEjecucion.
Operación:     llamar(ot_programado=datetime(2026,3,22,10,30), posicion_grilla=3)
Postcondición: Performance en estado Llamada.
Evento:        AtletaLlamado{ performanceId=P001, atletaId=A001, disciplina=STA,
               posicionGrilla=3, otProgramado=2026-03-22T10:30:00, llamadoEn=<timestamp> }
```

**Nota SP1:** En SP1 el aggregate Competencia no existe. `is_en_ejecucion()` se implementa
con un stub en `infrastructure/` que retorna siempre `True` (competencia always `EnEjecucion`).
El stub se reemplaza en SP2.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Llamar Atleta

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un atleta con id "P001" en disciplina "STA"
    And la performance del atleta está en estado "AnunciadaAP"

  Scenario: Sistema llama al atleta exitosamente
    Given la competencia está en estado "EnEjecucion"
    When el sistema llama al atleta con OT programado "10:30:00" y posición en grilla 3
    Then la performance pasa al estado "Llamada"
    And el evento AtletaLlamado persiste en el event stream
    And el evento contiene posicionGrilla=3 y otProgramado="10:30:00"

  Scenario: Rechazo — performance no está en estado AnunciadaAP
    Given la performance del atleta está en estado "Llamada"
    When el sistema intenta llamar al atleta nuevamente
    Then el sistema rechaza la operación con error "EstadoInvalidoParaLlamar"

  Scenario: Rechazo — competencia no está en ejecución
    Given la competencia NO está en estado "EnEjecucion"
    And la performance está en estado "AnunciadaAP"
    When el sistema intenta llamar al atleta
    Then el sistema rechaza la operación con error "CompetenciaNoEnEjecucion"
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente (hexagonal + ES + puertos ya establecidos)

**Capas afectadas:**
- [x] Domain — método `llamar()` en `Performance`, nuevo evento `AtletaLlamado`, nuevo método `is_en_ejecucion()` en `CompetenciaEstadoPort`
- [x] Application — `LlamarAtletaCommand` + `LlamarAtletaHandler`
- [x] Infrastructure — stub `CompetenciaEstadoStub.is_en_ejecucion()` retorna `True`
- [ ] API — los endpoints se añaden en Inc 1.3

**Extensión del puerto `CompetenciaEstadoPort`:**
Se agrega `is_en_ejecucion(competencia_id)` al puerto existente. El stub de SP1 retorna `True`.
No rompe compatibilidad con US-1.2.1 — el stub ya existe, solo se extiende.

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 3
- ADR-005: BCs estratégico (Competencia como Core Domain)
- ADR-008: Event Store append-only
- US mapeada desde: US-P-02 (ES Competencia)
- Incremento: Inc 1.2 en `docs/plans/sp1/SP1-candidatas.md`

---

## Notas de implementación

- **`llamar()` en el aggregate**: recibe `ot_programado: datetime` y `posicion_grilla: int`. Verifica estado interno (`AnunciadaAP`) antes de emitir. La verificación de INV-P-05 es responsabilidad del handler (necesita el puerto).
- **`LlamarAtletaHandler`**: carga el aggregate desde el Event Store vía `reconstitute()`, consulta `CompetenciaEstadoPort.is_en_ejecucion()`, ejecuta `llamar()`, persiste con `event_store.append()`.
- **`AtletaLlamado` event data**: `performance_id`, `participante_id`, `disciplina`, `posicion_grilla`, `ot_programado` (ISO 8601), `llamado_en` (timestamp).
- **`EstadoInvalidoParaLlamar`**: nueva excepción de dominio. El aggregate la lanza si su estado no es `AnunciadaAP`.
- **`CompetenciaNoEnEjecucion`**: nueva excepción de dominio. El handler la lanza si `is_en_ejecucion()` retorna `False`.
- **`_apply_stored` en Performance**: debe reconocer `AtletaLlamado` y setear `self._estado = EstadoPerformance.Llamada`.

---

*Redactado: 2026-03-22 — IEDD Capa 3 completa*
