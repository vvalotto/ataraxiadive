# US-4.1.2: Tarjeta Blanca con penalizaciones — performance válida con RP reducido

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `competencia` (domain) + `resultados` (domain)
**Capas afectadas**: `competencia/domain/`, `resultados/domain/`

---

## Descripción

Como **juez**,
quiero **registrar infracciones técnicas al asignar la tarjeta a una performance válida**
para **que el RP final refleje las deducciones reglamentarias sin desclasificar al atleta**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object (nuevo) | `PenalizacionTecnica` | Encapsula una infracción con su deducción en metros |
| Value Object (modificado) | `TipoTarjeta` | Nuevo valor: `BlancaConPenalizaciones` |
| Value Object (modificado) | `TarjetaAsignacion` | Acepta lista de penalizaciones para `BlancaConPenalizaciones` |
| Aggregate (modificado) | `Performance` | Nuevo estado derivado `rp_penalizado`; nuevo comando `asignar_tarjeta(BlancaConPenalizaciones, penalizaciones)` |
| Evento (modificado) | `TarjetaAsignada` | Payload incluye `penalizaciones: list[{tipo, deduccion}]` |
| Aggregate (modificado) | `RankingCompetencia` | Usa `rp_penalizado` si existe, `rp` si no hay penalizaciones |

### Lenguaje ubicuo relevante

- **Tarjeta Blanca con penalizaciones:** resultado válido donde el atleta completó el
  intento y el protocolo de superficie, pero cometió infracciones técnicas que reducen su RP.
  Diferente de la tarjeta amarilla: no hay deliberación ni resolución posterior.
- **Penalización técnica:** infracción que descuenta 3 metros del resultado medido
  (en disciplinas dinámicas). Las penalizaciones se acumulan.
- **RP penalizado:** `RP medido − (N × 3m)`. Es el valor que entra al ranking.
- **RP medido:** distancia física lograda por el atleta, antes de aplicar penalizaciones.

---

## Especificación del comportamiento

### Causas de penalización técnica

| Código | Descripción | Deducción | Fuente |
|--------|-------------|-----------|--------|
| `SIN_CONTACTO_PARED` | Sin contacto con la pared al iniciar (§2.2.1.4) | −3m | §2.2.1.4 |
| `FUERA_DE_CARRIL` | Cuerpo completo fuera del carril (§2.2.2.2) | −3m | §2.2.2.2 |
| `ASISTENTE_EN_ZONA` | Asistente no retiró de zona a 3 min del OT | −3m | §2.1.6.2 |
| `PATADA_DELFIN_BIALETAS` | Patada de delfín en evento de bialetas (por ciclo) | −3m | §1.1.3.3 |

### Invariantes del aggregate

- **INV-P-BWP-01:** `BlancaConPenalizaciones` requiere al menos una penalización (`len(penalizaciones) >= 1`).
- **INV-P-BWP-02:** cada `PenalizacionTecnica` tiene `deduccion > 0`.
- **INV-P-BWP-03:** `rp_penalizado = rp_medido − sum(p.deduccion for p in penalizaciones)`.
- **INV-P-BWP-04:** `rp_penalizado >= 0` — si la suma de penalizaciones supera el RP medido,
  el resultado mínimo es 0 (no puede ser negativo).
- **INV-P-BWP-05:** `BlancaConPenalizaciones` solo aplica a disciplinas dinámicas (DNF, DYN, DBF).
  Para STA la unidad es segundos y las reglas de deducción difieren — fuera de scope de esta US.

### Operación principal

**Nombre**: `asignar_tarjeta(tipo=BlancaConPenalizaciones, penalizaciones=[...], asignada_por)`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `ResultadoRegistrado`; disciplina dinámica (DNF/DYN/DBF) |
| **Postcondición** | Performance en `Ejecutada`; `rp_medido` = RP original; `rp_penalizado` = RP − deducciones; tarjeta = `BlancaConPenalizaciones` |
| **Eventos generados** | `TarjetaAsignada{tipo=BlancaConPenalizaciones, penalizaciones=[...], rp_penalizado=...}` |
| **Excepciones** | `EstadoInvalidoParaAsignarTarjeta`; `PenalizacionesObligatorias` (lista vacía); `RPPenalizadoNegativo` (si resultado < 0, clamear a 0 con advertencia, no excepción) |

**Ejemplo concreto:**

```
Precondición:  Performance en ResultadoRegistrado, disciplina=DYN, rp=Decimal("72")
Operación:     asignar_tarjeta(
                   tipo=BlancaConPenalizaciones,
                   penalizaciones=[PenalizacionTecnica(SIN_CONTACTO_PARED, 3),
                                   PenalizacionTecnica(FUERA_DE_CARRIL, 3)],
                   asignada_por="juez-01"
               )
Postcondición: estado=Ejecutada, tarjeta=BlancaConPenalizaciones,
               rp_medido=72, rp_penalizado=66
Evento:        TarjetaAsignada{tipo="BlancaConPenalizaciones",
                               penalizaciones=[{tipo:"SIN_CONTACTO_PARED", deduccion:3},
                                               {tipo:"FUERA_DE_CARRIL", deduccion:3}],
                               rp_medido="72", rp_penalizado="66"}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.2 — Tarjeta Blanca con penalizaciones

  Background:
    Given una Performance en estado ResultadoRegistrado para disciplina DYN con RP=72m

  Scenario: asignar tarjeta blanca con una penalización
    Given el atleta no tocó la pared al inicio
    When el juez asigna tarjeta BlancaConPenalizaciones con penalización SIN_CONTACTO_PARED
    Then la Performance pasa a estado Ejecutada
    And rp_medido es 72m
    And rp_penalizado es 69m
    And el evento TarjetaAsignada registra tipo="BlancaConPenalizaciones"
    And el evento incluye la penalización SIN_CONTACTO_PARED con deduccion=3

  Scenario: asignar tarjeta blanca con dos penalizaciones acumuladas
    Given el atleta no tocó la pared y salió del carril
    When asigna BlancaConPenalizaciones con [SIN_CONTACTO_PARED, FUERA_DE_CARRIL]
    Then rp_penalizado es 66m (72 − 3 − 3)
    And el evento registra dos penalizaciones

  Scenario: lista de penalizaciones vacía lanza excepción
    When asigna BlancaConPenalizaciones con lista de penalizaciones vacía
    Then se lanza PenalizacionesObligatorias

  Scenario: penalizaciones que superan el RP mínimo resultan en rp_penalizado=0
    Given una Performance con RP=4m
    When asigna BlancaConPenalizaciones con dos penalizaciones de 3m cada una
    Then rp_penalizado es 0 (no negativo)
    And el evento registra rp_penalizado="0"

  Scenario: ranking usa rp_penalizado para ordenar
    Given dos atletas: A con rp_penalizado=66m y B con rp=70m (sin penalizaciones)
    When se calcula el ranking de la disciplina DYN
    Then B (70m) aparece antes que A (66m)
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] Sí → evaluar si crear `ADR-014` para el modelo de penalizaciones acumulables.
  Decidir antes de implementar.

**Capa(s) afectadas:**
- [x] Domain (`competencia/domain/`, `resultados/domain/`)

---

## Referencias

- Plan: `docs/plans/sp4/PLAN-SP4.md §INC-4.1`
- Brechas: `docs/dominio/06-brechas-reglamento.md §3`
- Reglamento: CMAS §1.1.13, §2.2.1.4, §2.2.2.2, §2.1.6.2, §1.1.3.3

---

## Notas de implementación

- `TipoTarjeta` agrega `BlancaConPenalizaciones = "BlancaConPenalizaciones"`.
- `PenalizacionTecnica` es un `StrEnum` `TipoPenalizacion` para el código + `Decimal` deduccion.
  Modelar como `@dataclass(frozen=True) PenalizacionTecnica(tipo: TipoPenalizacion, deduccion: Decimal)`.
- `Performance` agrega `_rp_medido: Decimal | None` y `_rp_penalizado: Decimal | None`.
  `rp_penalizado` es el valor a usar en el ranking. `rp` (propiedad existente) puede
  apuntar a `_rp_penalizado` si existe, o a `_rp_medido` si no hay penalizaciones,
  para mantener compatibilidad con `RankingCompetencia`.
- `RankingCompetencia` en `resultados/domain/`: ya usa el valor devuelto por la propiedad `rp`
  de `PerformanceData`. Si la propiedad `rp` ya devuelve el valor penalizado, no requiere
  cambios en `resultados/`.
- `_apply_tarjeta_asignada()` en `Performance` debe manejar el nuevo tipo y poblar
  `_rp_medido` y `_rp_penalizado` desde el payload del evento.
- La regla INV-P-BWP-05 (solo dinámica) se valida en el command handler, no en el aggregate,
  ya que el aggregate no conoce semántica de disciplina más allá del VO `Disciplina`.

---

*Redactado: 2026-04-08 — INC-4.1 correcciones dominio CMAS/FAAS*
