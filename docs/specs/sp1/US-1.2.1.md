# US-1.2.1: Registrar AP

**Estado**: `En progreso`
**Incremento**: Inc 1.2 — El Dominio Habla
**Subproyecto**: SP1 — La Performance
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **atleta o sistema**,
quiero **declarar mi Announced Performance (AP) para una disciplina y competencia**
para **quedar registrado en la grilla de salida y participar en la competencia**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Raíz del ciclo de vida de la actuación de un atleta en una disciplina |
| Value Object | `AP` | Encapsula el valor declarado y su unidad (metros / segundos) |
| Value Object | `Disciplina` | Identifica la modalidad apnea (STA, DNF, DYN…) |
| Value Object | `UnidadMedida` | `Metros` o `Segundos` según la disciplina |
| Value Object | `EstadoPerformance` | Máquina de estados: `AnunciadaAP → Llamada → Ejecutada / DNS` |
| Domain Event | `APRegistrado` | Señala que el AP fue declarado y el aggregate Performance fue creado |

### Lenguaje ubicuo relevante

- **AP (Announced Performance)**: marca que el atleta declara ANTES de competir. Define su posición en la grilla.
- **Performance**: la actuación de un atleta en una disciplina dentro de una competencia. Aggregate que gestiona todo su ciclo de vida.
- **GrillaConfirmada**: evento que bloquea toda modificación de AP — grilla congelada.
- **PlazoAPVencido**: evento que cierra el período de registro de APs para una disciplina.
- **Competencia**: contexto en el que se ejecutan múltiples Performances de distintos atletas.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-P-01**: `valorAP > 0` — un AP de cero o negativo es inválido.
- **INV-P-02**: Un atleta solo puede tener un AP activo por (atleta, disciplina, competencia). No se pueden registrar dos APs para la misma combinación.
- **INV-P-03**: `APRegistrado` no permitido después de `PlazoAPVencido` (plazo de registro cerrado).
- **INV-P-04**: `APRegistrado` no permitido después de `GrillaConfirmada` (grilla congelada).

### Operación principal

**Nombre**: `registrarAP(valor: Decimal, unidad: UnidadMedida)`

| | Descripción |
|---|---|
| **Precondición** | La Performance no existe aún para esta (competencia, participante, disciplina). El plazo de AP no ha vencido. La grilla no está confirmada. |
| **Postcondición** | Evento `APRegistrado` persiste en el stream `performance-{competenciaId}-{participanteId}-{disciplina}`. El aggregate Performance está en estado `AnunciadaAP`. |
| **Eventos generados** | `APRegistrado` |
| **Excepciones** | `APYaRegistrado` (INV-P-02) · `ValorAPInvalido` (INV-P-01) · `PlazoAPVencido` (INV-P-03) · `GrillaYaConfirmada` (INV-P-04) |

**Ejemplo concreto:**

```
Precondición:  No existe AP para atleta A123, disciplina STA, competencia C456
Operación:     registrarAP(valor=Decimal("5.50"), unidad=Segundos)
Postcondición: Performance existe con estado=AnunciadaAP, ap=AP(5.50, Segundos)
Evento:        APRegistrado{ performanceId, competenciaId="C456", participanteId="A123",
               disciplina=STA, valorAP=5.50, unidad=Segundos, registradoEn=<timestamp> }
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Registrar Announced Performance

  Background:
    Given una competencia activa con id "C001"
    And un atleta con id "P001"
    And la disciplina "STA"

  Scenario: Atleta registra AP exitosamente
    Given no existe un AP previo del atleta para esta disciplina y competencia
    And el plazo de AP no ha vencido
    And la grilla no está confirmada
    When el atleta registra un AP de 5 minutos 30 segundos en STA
    Then el AP queda registrado exitosamente
    And la performance queda en estado "AnunciadaAP"
    And el evento APRegistrado persiste en el event stream

  Scenario: Rechazo — AP ya registrado para la misma combinación
    Given ya existe un AP del atleta "P001" en disciplina "STA" para la competencia "C001"
    When el atleta intenta registrar otro AP de 6 minutos
    Then el sistema rechaza la operación con error "APYaRegistrado"

  Scenario: Rechazo — valor AP igual a cero
    Given no existe un AP previo del atleta
    When el atleta intenta registrar un AP de 0 segundos
    Then el sistema rechaza la operación con error "ValorAPInvalido"

  Scenario: Rechazo — valor AP negativo
    Given no existe un AP previo del atleta
    When el atleta intenta registrar un AP de -1 metros
    Then el sistema rechaza la operación con error "ValorAPInvalido"

  Scenario: Rechazo — plazo de AP vencido
    Given el plazo de AP ya venció para esta disciplina y competencia
    And no existe un AP previo del atleta
    When el atleta intenta registrar su AP
    Then el sistema rechaza la operación con error "PlazoAPVencido"

  Scenario: Rechazo — grilla ya confirmada
    Given la grilla ya fue confirmada para esta competencia
    And no existe un AP previo del atleta
    When el atleta intenta registrar su AP
    Then el sistema rechaza la operación con error "GrillaYaConfirmada"
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente (hexagonal + ES ya establecidos en Inc 1.1)

**Capas afectadas:**
- [x] Domain — `Performance` aggregate, value objects, `APRegistrado` event
- [x] Application — `RegistrarAPHandler` command handler
- [ ] Infrastructure — no requiere nueva infraestructura (usa `SQLiteEventStore` de Inc 1.1)
- [ ] API — los endpoints se añaden en Inc 1.3

**Nota sobre INV-P-03 e INV-P-04 en SP1:**
En SP1 el aggregate `Competencia` no existe. Los checks de `PlazoAPVencido` y `GrillaConfirmada`
se implementan vía el puerto `CompetenciaEstadoPort` con un stub que retorna `False` (plazo activo,
grilla no confirmada). El stub se reemplaza en SP2 con la implementación real que lee el stream
de Competencia.

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 2
- ADR-005: BCs estratégico (Competencia como Core Domain)
- ADR-008: Event Store append-only
- US mapeada desde: US-P-01 (ES Competencia)
- Incremento: Inc 1.2 en `docs/plans/sp1/SP1-candidatas.md`

---

## Notas de implementación

- **Stream ID**: `performance-{competencia_id}-{participante_id}-{disciplina.value}` — el natural key está en el stream ID; si el stream ya tiene eventos, INV-P-02 está violado.
- **Creación del aggregate**: `Performance` se crea con `RegistrarAP`; no existe un estado "vacío" previo. El aggregate se reconstitituye desde eventos con `reconstitute(events)`.
- **Clases base**: `shared/domain/base/DomainEvent` y `shared/domain/base/AggregateRoot` se crean en esta US (primera US que los necesita).
- **CompetenciaEstadoPort**: nuevo puerto en `competencia/domain/ports/` con `is_plazo_vencido()` e `is_grilla_confirmada()`. Stub en `infrastructure/` retorna siempre `False`.

---

*Redactado: 2026-03-21 — IEDD Capa 3 completa*
