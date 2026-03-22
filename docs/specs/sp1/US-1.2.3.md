# US-1.2.3: Registrar Resultado

**Estado**: `Pendiente`
**Incremento**: Inc 1.2 — El Dominio Habla
**Subproyecto**: SP1 — La Performance
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **registrar el resultado efectivo de un atleta una vez que completa su performance**
para **documentar el RP (Realized Performance) que luego determinará la tarjeta a asignar**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Gestiona el ciclo de vida — aquí transiciona de `Llamada` a `ResultadoRegistrado` |
| Value Object | `EstadoPerformance` | Máquina de estados: `Llamada → ResultadoRegistrado` |
| Domain Event | `ResultadoRegistrado` | Registra el RP efectivo del atleta (marca realizada) |

### Lenguaje ubicuo relevante

- **RP (Realized Performance)**: la marca efectivamente lograda por el atleta durante su actuación.
- **valorRP**: valor numérico del RP. Puede ser menor, igual o mayor al AP declarado.
- **ResultadoRegistrado**: estado intermedio entre `Llamada` y `Ejecutada`. Indica que el juez
  registró la marca pero aún no asignó la tarjeta.
- **Mutuamente excluyente**: una Performance en estado `Llamada` puede resultar en
  `ResultadoRegistrado` (atleta actuó) o `DNS` (atleta no se presentó), pero no ambos.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-P-06**: `RegistrarResultado` solo permitido si Performance en estado `Llamada`.
- **INV-P-09**: `DNSRegistrado` y `ResultadoRegistrado` son mutuamente excluyentes.
  En la práctica: si la Performance está en `Llamada` (no en `DNS`), INV-P-09 queda
  protegido implícitamente por INV-P-06. Se documenta para trazabilidad.

### Precondición de estado

- Performance en estado `Llamada` (si está en otro estado, la operación es inválida).

### Operación principal

**Nombre**: `registrar_resultado(valor_rp: Decimal, unidad: UnidadMedida, registrado_por: str)`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `Llamada`. |
| **Postcondición** | Evento `ResultadoRegistrado` persiste en el stream. El aggregate pasa al estado `ResultadoRegistrado`. |
| **Eventos generados** | `ResultadoRegistrado` |
| **Excepciones** | `EstadoInvalidoParaRegistrarResultado` (Performance no está en `Llamada`) |

**Ejemplo concreto:**

```
Precondición:  Performance P001 en estado Llamada.
Operación:     registrar_resultado(valor_rp=Decimal("50.5"), unidad=Metros, registrado_por="juez-001")
Postcondición: Performance en estado ResultadoRegistrado.
Evento:        ResultadoRegistrado{ performanceId=P001, participanteId=A001, disciplina=DNF,
               valorRP=50.5, unidad=Metros, registradoPor="juez-001", registradoEn=<timestamp> }
```

**Nota SP1:** `registrado_por` es un string arbitrario (ID del juez). BC Identidad no existe en SP1.

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Registrar Resultado

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un atleta con id "P001" en disciplina "DNF"
    And la performance del atleta tiene AP registrado de 50 metros
    And la performance está en estado "Llamada"

  Scenario: Juez registra el resultado exitosamente
    When el juez registra el resultado con valorRP=50.5 metros y registrado_por="juez-001"
    Then la performance pasa al estado "ResultadoRegistrado"
    And el evento ResultadoRegistrado persiste en el event stream
    And el evento contiene valorRP=50.5, unidad=Metros, registradoPor="juez-001"

  Scenario: Rechazo — performance no está en estado Llamada
    Given la performance del atleta está en estado "AnunciadaAP"
    When el juez intenta registrar el resultado
    Then el sistema rechaza la operación con error "EstadoInvalidoParaRegistrarResultado"

  Scenario: Rechazo — performance ya tiene DNS registrado
    Given la performance del atleta está en estado "DNS"
    When el juez intenta registrar el resultado
    Then el sistema rechaza la operación con error "EstadoInvalidoParaRegistrarResultado"
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente (hexagonal + ES + puertos ya establecidos)

**Capas afectadas:**
- [x] Domain — método `registrar_resultado()` en `Performance`, nuevo estado `ResultadoRegistrado`
  en `EstadoPerformance`, nuevo evento `ResultadoRegistrado`, nueva excepción
  `EstadoInvalidoParaRegistrarResultado`
- [x] Application — `RegistrarResultadoCommand` + `RegistrarResultadoHandler`
- [ ] Infrastructure — no requiere cambios (EventStore y stub ya existen)
- [ ] API — los endpoints se añaden en Inc 1.3

**Extensión de `EstadoPerformance`:**
Se agrega el estado `ResultadoRegistrado` al StrEnum existente. No rompe compatibilidad con
US-1.2.1 ni US-1.2.2 — los estados anteriores (`AnunciadaAP`, `Llamada`, `Ejecutada`, `DNS`)
no cambian.

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 3
- ADR-005: BCs estratégico (Competencia como Core Domain)
- ADR-008: Event Store append-only
- US mapeada desde: US-P-03 (ES Competencia)
- Incremento: Inc 1.2 en `docs/plans/sp1/SP1-candidatas.md`

---

## Notas de implementación

- **`registrar_resultado()` en el aggregate**: recibe `valor_rp: Decimal`, `unidad: UnidadMedida`,
  `registrado_por: str`. Verifica estado interno (`Llamada`) antes de emitir. No requiere consulta
  a puertos externos.
- **`RegistrarResultadoHandler`**: carga el aggregate desde el Event Store vía `reconstitute()`,
  ejecuta `registrar_resultado()`, persiste con `event_store.append()`. Sin puertos externos.
- **`ResultadoRegistrado` event data**: `performance_id`, `participante_id`, `disciplina`,
  `valor_rp` (str de Decimal), `unidad`, `registrado_por`, `registrado_en` (ISO 8601).
- **`EstadoInvalidoParaRegistrarResultado`**: nueva excepción de dominio inline en `performance.py`.
- **`_apply_stored` en Performance**: debe reconocer `ResultadoRegistrado` y setear
  `self._estado = EstadoPerformance.ResultadoRegistrado`.
- **`EstadoPerformance`**: agregar `ResultadoRegistrado = "ResultadoRegistrado"` al StrEnum.
  La docstring del StrEnum ya indica `Llamada → Ejecutada` — actualizar para reflejar el estado intermedio.

---

*Redactado: 2026-03-22 — IEDD Capa 3 completa*
