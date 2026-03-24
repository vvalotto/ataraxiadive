# US-2.1.2: Generar / Regenerar Grilla de Salida

**Estado**: `Backlog`
**Incremento**: Inc 2.1 — La Grilla de Salida
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Competencia`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **organizador o sistema**,
quiero **generar la grilla de salida de una competencia a partir de los APs registrados**
para **que los atletas queden ordenados según las reglas de la disciplina con sus OTs calculados**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Competencia` | Genera y gestiona la grilla — calcula posiciones, OTs y asigna andariveles |
| Value Object | `PosicionGrilla` | Posición ordinal del atleta en la grilla (1-based) |
| Value Object | `Andarivel` | Número de carril/andarivel asignado al atleta |
| Value Object | `OTProgramado` | Timestamp calculado del Official Top del atleta |
| Domain Event | `GrillaDeSalidaGenerada` | Snapshot de la grilla completa con todos los atletas ordenados |

### Lenguaje ubicuo relevante

- **Grilla de Salida**: lista ordenada de performances activas con posición, andarivel y OT calculado para cada atleta.
- **AP (Announced Performance)**: la marca declarada es el criterio de ordenamiento — menor a mayor para distancia, mayor a menor para tiempo.
- **Andarivel**: carril de competencia. En SP2 Inc 2.1 se usa un único andarivel (andariveles múltiples en Inc 2.3).
- **OT (Official Top)**: OT_atleta = OT_inicio + (posición − 1) × intervaloDisciplina.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-C-01**: `intervaloDisciplina` debe estar configurado (evento `IntervaloOTConfigurado` en el stream) antes de `GenerarGrilla`. De lo contrario → `IntervaloNoConfigurado`.
- **RF-PR-04** (política P-05): atletas sin AP registrado (`APRegistrado` no emitido para esa competencia) no aparecen en la grilla generada.
- **Regeneración**: permitida mientras `GrillaConfirmada` no fue emitido. Si `GrillaConfirmada` existe → `GrillaYaConfirmada`.

### Regla de ordenamiento (política P-01)

| Tipo de disciplina | Ordenamiento AP |
|-------------------|----------------|
| Distancia (DNF, DYN, DYNB) | AP menor → mayor (primero el más conservador) |
| Tiempo (STA) | AP mayor → menor (primero el más largo) |

### Cálculo de OT (política P-02)

```
OT_atleta = OT_inicio + (posición − 1) × intervaloDisciplina
```

Donde `OT_inicio` es el timestamp de inicio de la competencia (hora de comienzo configurada
o timestamp de `IniciarCompetencia` — se define en US-2.1.4).

### Operación principal

**Nombre**: `generar_grilla(ot_inicio: datetime, andariveles: int = 1)`

| | Descripción |
|---|---|
| **Precondición** | `intervaloDisciplina` configurado. Grilla no confirmada. Existen al menos una Performance en estado `AnunciadaAP` para esta competencia. |
| **Postcondición** | `GrillaDeSalidaGenerada` persiste con la lista ordenada `[{performanceId, atletaId, posicion, andarivel, ot_programado}]`. |
| **Eventos generados** | `GrillaDeSalidaGenerada` |
| **Excepciones** | `IntervaloNoConfigurado` (INV-C-01) · `GrillaYaConfirmada` · `SinPerformancesParaGrilla` |

**Ejemplo concreto — STA (tiempo, mayor→menor):**

```
Input:  3 atletas con AP: A001→5:30, A002→6:00, A003→4:45
        intervaloDisciplina=9 min, OT_inicio=10:00:00

Ordenamiento: A002(6:00) > A001(5:30) > A003(4:45)

Grilla generada:
  Pos 1 | A002 | andarivel=1 | OT=10:00:00
  Pos 2 | A001 | andarivel=1 | OT=10:09:00
  Pos 3 | A003 | andarivel=1 | OT=10:18:00

Evento: GrillaDeSalidaGenerada{
  competenciaId="C001",
  disciplina="STA",
  performances=[
    {performanceId, atletaId="A002", posicion=1, andarivel=1, ot_programado="10:00:00"},
    {performanceId, atletaId="A001", posicion=2, andarivel=1, ot_programado="10:09:00"},
    {performanceId, atletaId="A003", posicion=3, andarivel=1, ot_programado="10:18:00"},
  ],
  generadaEn=<timestamp>
}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: Generar Grilla de Salida

  Background:
    Given una competencia "C001" con disciplina "STA" en estado "Preparacion"
    And el intervalo OT está configurado en 9 minutos
    And OT de inicio es "10:00:00"

  Scenario: Grilla generada con orden correcto para STA (tiempo mayor→menor)
    Given los siguientes APs registrados:
      | atletaId | valorAP |
      | A001     | 5:30    |
      | A002     | 6:00    |
      | A003     | 4:45    |
    When el organizador genera la grilla
    Then la grilla queda:
      | posicion | atletaId | ot_programado |
      | 1        | A002     | 10:00:00      |
      | 2        | A001     | 10:09:00      |
      | 3        | A003     | 10:18:00      |
    And el evento GrillaDeSalidaGenerada persiste en el stream

  Scenario: Atleta sin AP no aparece en la grilla (RF-PR-04)
    Given los siguientes APs registrados: A001→5:30, A002→6:00
    And el atleta A003 está inscripto pero no registró AP
    When el organizador genera la grilla
    Then la grilla contiene solo A002 y A001
    And A003 no aparece en la grilla

  Scenario: Regenerar grilla antes de confirmar
    Given la grilla ya fue generada
    And la grilla no está confirmada
    When el organizador regenera la grilla con nuevos datos
    Then se emite un nuevo GrillaDeSalidaGenerada
    And el Read Model muestra la grilla actualizada

  Scenario: Rechazo — intervalo no configurado
    Given no se configuró el intervalo OT
    When el organizador intenta generar la grilla
    Then el sistema rechaza con error "IntervaloNoConfigurado"

  Scenario: Rechazo — grilla ya confirmada
    Given la grilla ya fue confirmada
    When el organizador intenta regenerar la grilla
    Then el sistema rechaza con error "GrillaYaConfirmada"

  Scenario: Grilla DNF (distancia menor→mayor)
    Given una competencia "C002" con disciplina "DNF"
    And APs: A001→80m, A002→60m, A003→100m
    And intervalo=10min, OT_inicio=09:00:00
    When se genera la grilla
    Then el orden es: A002(60m) pos=1, A001(80m) pos=2, A003(100m) pos=3
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — usa la arquitectura hexagonal ya establecida con el Event Store de SP1

**Capas afectadas:**
- [x] Domain — `Competencia.generar_grilla()`, `GrillaDeSalidaGenerada` event, política P-01/P-02
- [x] Application — `GenerarGrillaHandler`
- [ ] Infrastructure — no requiere cambios (usa `SQLiteEventStore` existente)
- [ ] API — endpoints en US-2.1.4

**Puerto nuevo:** `PerformancesAPPort` en `domain/ports/` — el aggregate consulta las Performances
con AP registrado para esta competencia. El adaptador lee desde el Event Store.

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 1 + Flujo 2
- Invariantes: INV-C-01; Políticas: P-01, P-02, P-03, P-05
- RFs: RF-PR-04, RF-PR-05, RF-PR-08
- `docs/plans/sp2/SP2-candidatas.md` — Inc 2.1

---

*Redactado: 2026-03-24 — IEDD Capa 3*
