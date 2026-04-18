# US-4.1.1: Motivos de tarjeta roja — catálogo formal de causas de DQ

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/`

---

## Descripción

Como **juez**,
quiero **seleccionar el motivo específico al asignar una tarjeta roja**
para **que el registro refleje la causa reglamentaria de la descalificación y permita
estadísticas precisas por tipo de DQ**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object | `MotivoDQ` | Encapsula el código y descripción de una causa de descalificación |
| Value Object (modificado) | `TarjetaAsignacion` | Agrega `motivo_dq: MotivoDQ` en reemplazo del string libre para Roja |
| Aggregate (modificado) | `Performance` | `asignar_tarjeta(Roja, ...)` requiere `MotivoDQ` en lugar de string libre |
| Evento (modificado) | `TarjetaAsignada` | Payload incluye `motivo_dq_codigo` en lugar de `motivo` string |

### Lenguaje ubicuo relevante

- **Motivo de DQ (MotivoDQ):** causa reglamentaria que origina una tarjeta roja.
  Cada motivo tiene un código formal y una descripción legible.
- **BKO superficie:** black-out al emerger — pérdida de conciencia en la superficie.
  Tiene implicancias para los días siguientes del torneo.
- **BKO subacuático:** black-out bajo el agua — implica rescate y descalificación.
- **Protocolo de superficie:** secuencia obligatoria de señales al emerger (OK + sin apoyo).
- **Salida en falso:** en SPE, el atleta comienza a nadar antes del OT.

---

## Especificación del comportamiento

### Catálogo inicial de causas (MotivoDQ)

| Código | Descripción | Fuente reglamentaria |
|--------|-------------|---------------------|
| `BKO_SUPERFICIE` | Black-out en superficie | §1.1.10 |
| `BKO_SUBACUATICO` | Black-out subacuático | §1.1.10 |
| `PROTOCOLO_SUPERFICIE` | No siguió protocolo de superficie (sin OK, apoyo en carril) | §1.2.2 |
| `INFRACCION_TECNICA_DQ` | Infracción técnica con descalificación directa | §1.1.14 |
| `NO_INICIO_EN_VENTANA` | No inició dentro de la ventana OT+30s | §1.2.1.9 |
| `SALIDA_EN_FALSO` | Salida en falso (SPE) — inicio antes del OT | §4.2.1.3 |

### Invariantes del aggregate

- **INV-P-11 (modificado):** al asignar tarjeta Roja, se requiere `MotivoDQ` del catálogo —
  el string libre ya no es válido para Roja.
- **INV-P-11b:** al asignar tarjeta Amarilla, el motivo sigue siendo string libre
  (refleja duda, no causa formal de DQ).
- **INV-DQ-01:** `MotivoDQ` con código `BKO_SUPERFICIE` o `BKO_SUBACUATICO` requiere
  `distancia_blackout > 0`.
- **INV-DQ-02:** `MotivoDQ` con cualquier otro código no debe tener `distancia_blackout`.

### Operación principal

**Nombre**: `asignar_tarjeta(tipo=Roja, motivo_dq=MotivoDQ, asignada_por, distancia_blackout?)`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `ResultadoRegistrado` |
| **Postcondición** | Performance en `Ejecutada`; tarjeta = `Roja`; `motivo_dq` registrado en el evento |
| **Eventos generados** | `TarjetaAsignada{tipo=Roja, motivo_dq_codigo=..., distancia_blackout=?}` |
| **Excepciones** | `EstadoInvalidoParaAsignarTarjeta` (no en ResultadoRegistrado); `MotivoDQObligatorio` (Roja sin MotivoDQ); `DistanciaBlackoutObligatoria` (BKO sin distancia) |

**Ejemplo concreto:**

```
Precondición:  Performance en ResultadoRegistrado, disciplina=DYN
Operación:     asignar_tarjeta(tipo=Roja, motivo_dq=MotivoDQ.BKO_SUPERFICIE,
                               asignada_por="juez-01", distancia_blackout=Decimal("45"))
Postcondición: estado=Ejecutada, tarjeta=Roja,
               motivo_dq_codigo="BKO_SUPERFICIE", distancia_blackout=45
Evento:        TarjetaAsignada{tipo="Roja", motivo_dq_codigo="BKO_SUPERFICIE",
                               distancia_blackout="45"}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.1 — Motivos de tarjeta roja con catálogo formal

  Background:
    Given una Performance en estado ResultadoRegistrado para disciplina DYN

  Scenario: asignar tarjeta roja con motivo BKO superficie
    Given el juez detectó black-out en superficie
    When asigna tarjeta Roja con motivo BKO_SUPERFICIE y distancia_blackout=45
    Then la Performance pasa a estado Ejecutada
    And el evento TarjetaAsignada registra motivo_dq_codigo="BKO_SUPERFICIE"
    And distancia_blackout=45 queda registrada

  Scenario: asignar tarjeta roja con motivo protocolo de superficie
    Given el atleta no realizó el protocolo de superficie reglamentario
    When asigna tarjeta Roja con motivo PROTOCOLO_SUPERFICIE
    Then la Performance pasa a estado Ejecutada
    And el evento TarjetaAsignada registra motivo_dq_codigo="PROTOCOLO_SUPERFICIE"
    And distancia_blackout no aplica y no se registra

  Scenario: tarjeta roja sin motivo_dq lanza excepción
    When asigna tarjeta Roja sin especificar MotivoDQ
    Then se lanza MotivoDQObligatorio

  Scenario: BKO superficie sin distancia_blackout lanza excepción
    When asigna tarjeta Roja con motivo BKO_SUPERFICIE sin distancia_blackout
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: BKO subacuático con distancia_blackout cero lanza excepción
    When asigna tarjeta Roja con motivo BKO_SUBACUATICO y distancia_blackout=0
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: motivo de DQ no BKO no debe tener distancia_blackout
    When asigna tarjeta Roja con motivo SALIDA_EN_FALSO y distancia_blackout=20
    Then se lanza DistanciaBlackoutNoAplica

  Scenario: tarjeta amarilla mantiene motivo string libre
    When asigna tarjeta Amarilla con motivo="duda sobre protocolo"
    Then la Performance pasa a estado Ejecutada
    And el evento TarjetaAsignada registra el motivo como texto libre
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Domain (`competencia/domain/value_objects/`, `competencia/domain/aggregates/`,
  `competencia/domain/events/`, `competencia/domain/exceptions.py`)

---

## Referencias

- Plan: `docs/plans/sp4/PLAN-SP4.md §INC-4.1`
- Brechas: `docs/dominio/06-brechas-reglamento.md §1` y `§9`
- Reglamento: CMAS §1.1.10, §1.2.2, §1.1.14, §1.2.1.9, §4.2.1.3

---

## Notas de implementación

- `MotivoDQ` es un `StrEnum` en `competencia/domain/value_objects/motivo_dq.py`.
  El catálogo es el enum mismo — no requiere persistencia ni tabla de base de datos.
- `TarjetaAsignacion` reemplaza `motivo: str | None` por:
  - `motivo_dq: MotivoDQ | None` — para tarjeta Roja (obligatorio)
  - `motivo_texto: str | None` — para tarjeta Amarilla (string libre)
- La validación del blackout se mueve de `if self.motivo == "black-out"` a
  `if self.motivo_dq in (MotivoDQ.BKO_SUPERFICIE, MotivoDQ.BKO_SUBACUATICO)`.
- `TarjetaAsignada` evento: reemplazar campo `motivo` por `motivo_dq_codigo` (str | None)
  más `motivo_texto` (str | None).
- **Migración de datos:** los events store existentes usan `motivo="black-out"` (string libre).
  Los handlers de reconstitución deben aceptar el formato antiguo por compatibilidad.
  Estrategia: si `motivo == "black-out"` en payload antiguo → mapear a `motivo_dq_codigo = "BKO_SUPERFICIE"`.
- Nuevas excepciones: `MotivoDQObligatorio`, `DistanciaBlackoutNoAplica` en `competencia/domain/exceptions.py`.

---

*Redactado: 2026-04-08 — INC-4.1 correcciones dominio CMAS/FAAS*
