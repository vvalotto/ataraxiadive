# US-4.1.3: Subdisciplinas SPE — cuatro variantes de velocidad-resistencia

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `torneo` (domain) + `resultados` (domain) + `shared/domain`
**Capas afectadas**: `shared/domain/value_objects/`, `torneo/domain/`, `resultados/domain/`

---

## Descripción

Como **organizador**,
quiero **configurar un torneo con variantes específicas de SPE (2×50m, 4×50m, 8×50m, 16×50m)**
para **que cada variante tenga su propia grilla, ranking y homologación independiente,
tal como establece el reglamento CMAS/FAAS**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object (modificado) | `Disciplina` | Agrega cuatro valores de variante SPE: `SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50` |
| Value Object (modificado) | `DisciplinaDescriptor` | Descriptores para las 4 variantes SPE: `unidad=Segundos`, `orden_ascendente=False` |
| Aggregate (modificado) | `Torneo` | Las disciplinas de un torneo pueden incluir variantes SPE en lugar de `SPE` genérico |
| Aggregate (modificado) | `RankingCompetencia` | Cada variante SPE genera un ranking independiente |

### Lenguaje ubicuo relevante

- **Variante SPE:** una de las cuatro modalidades de velocidad-resistencia definidas por el
  reglamento, identificada por el número de largos: 2×50m, 4×50m, 8×50m, 16×50m.
- **SPE (genérico):** el valor `SPE` existente queda como legacy — no se elimina para
  no romper eventos históricos, pero no se usa en torneos nuevos.
- **Resultado SPE:** siempre un tiempo en segundos (menor es mejor). No es metros.

---

## Especificación del comportamiento

### Nuevos valores de Disciplina

```
SPE_2X50   → 2 largos × 50m = 100m total    → Velocidad
SPE_4X50   → 4 largos × 50m = 200m total    → Velocidad
SPE_8X50   → 8 largos × 50m = 400m total    → Resistencia
SPE_16X50  → 16 largos × 50m = 800m total   → Resistencia
```

Propiedades comunes de las 4 variantes:
- `es_tiempo() = True` (resultado en segundos, no metros)
- `es_spe() = True` (identificador de familia SPE)
- `DisciplinaDescriptor.para(SPE_Nx50).unidad_esperada = Segundos`
- `DisciplinaDescriptor.para(SPE_Nx50).orden_ascendente = False`
  (los más lentos compiten primero — ver US-4.1.4)

### Invariantes del dominio

- **INV-SPE-01:** las disciplinas `SPE_2X50`, `SPE_4X50`, `SPE_8X50`, `SPE_16X50` usan
  `UnidadMedida.Segundos` para AP y RP.
- **INV-SPE-02:** en un mismo torneo, se pueden incluir múltiples variantes SPE
  como eventos independientes (ej: SPE_2X50 + SPE_8X50 simultáneamente).
- **INV-SPE-03:** el valor `Disciplina.SPE` (genérico) no puede usarse en torneos nuevos;
  solo se mantiene para reconstitución de eventos históricos.

### Operación principal

**Nombre**: `agregar_disciplina(torneo_id, disciplina: Disciplina)` — comando de Torneo

| | Descripción |
|---|---|
| **Precondición** | Torneo en estado `CREADO` o `INSCRIPCION_ABIERTA`; disciplina es un valor válido de `Disciplina` |
| **Postcondición** | La disciplina queda registrada en el torneo; si es variante SPE, se almacena el código específico (`SPE_2X50`, etc.) |
| **Eventos generados** | (existente) evento de disciplina agregada al torneo |
| **Excepciones** | `DisciplinaObsoleta` si se intenta agregar `Disciplina.SPE` genérico a un torneo nuevo |

**Ejemplo concreto:**

```
Precondición:  Torneo en INSCRIPCION_ABIERTA, sin disciplinas SPE configuradas
Operación:     agregar_disciplina(torneo_id=T-001, disciplina=Disciplina.SPE_2X50)
Postcondición: torneo.disciplinas incluye SPE_2X50
               competencia SPE_2X50 puede crearse independiente de SPE_8X50
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.3 — Subdisciplinas SPE

  Scenario: SPE_2X50 tiene unidad Segundos y no metros
    Given el DisciplinaDescriptor para SPE_2X50
    Then unidad_esperada es Segundos
    And es_tiempo() retorna True
    And es_spe() retorna True

  Scenario: SPE_4X50 y SPE_8X50 son eventos independientes en el mismo torneo
    Given un torneo con SPE_4X50 y SPE_8X50 configuradas
    When se generan las grillas
    Then SPE_4X50 tiene su propia grilla
    And SPE_8X50 tiene su propia grilla independiente

  Scenario: ranking SPE_2X50 es independiente de SPE_8X50
    Given un torneo con performances en SPE_2X50 y SPE_8X50
    When se consulta el ranking
    Then el ranking de SPE_2X50 no incluye atletas de SPE_8X50

  Scenario: AP en SPE se registra en segundos
    Given una Performance para disciplina SPE_4X50
    When se registra AP con valor=180 y unidad=Segundos
    Then el AP queda registrado correctamente

  Scenario: AP en SPE con unidad metros lanza excepción
    Given una Performance para disciplina SPE_2X50
    When se registra AP con valor=100 y unidad=Metros
    Then se lanza UnidadMedidaInvalida

  Scenario: disciplina SPE genérica no puede agregarse a torneo nuevo
    Given un Torneo recién creado
    When se intenta agregar disciplina Disciplina.SPE (genérico)
    Then se lanza DisciplinaObsoleta
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — extensión del enum existente con método helper

**Capa(s) afectadas:**
- [x] Domain (`shared/domain/value_objects/disciplina.py`,
  `shared/domain/value_objects/disciplina_descriptor.py`,
  `torneo/domain/`, `resultados/domain/`)

---

## Referencias

- Plan: `docs/plans/sp4/PLAN-SP4.md §INC-4.1`
- Brechas: `docs/dominio/06-brechas-reglamento.md §5`
- Reglamento: CMAS §1.1.8.7
- Context Map: `docs/design/context-map.md`

---

## Notas de implementación

- Agregar a `shared/domain/value_objects/disciplina.py`:
  ```python
  SPE_2X50  = "SPE_2X50"
  SPE_4X50  = "SPE_4X50"
  SPE_8X50  = "SPE_8X50"
  SPE_16X50 = "SPE_16X50"

  def es_spe(self) -> bool:
      return self in (Disciplina.SPE, Disciplina.SPE_2X50, Disciplina.SPE_4X50,
                      Disciplina.SPE_8X50, Disciplina.SPE_16X50)

  def es_tiempo(self) -> bool:
      return self in (Disciplina.STA, Disciplina.SPE_2X50, Disciplina.SPE_4X50,
                      Disciplina.SPE_8X50, Disciplina.SPE_16X50)
  ```
- Actualizar `DisciplinaDescriptor.para()` para las 4 variantes:
  `unidad_esperada=Segundos, orden_ascendente=False`.
- `Disciplina.SPE` (genérico) mantiene comportamiento actual (`es_tiempo()=False`) para
  no romper reconstitución de eventos históricos. Solo se rechaza en lógica de negocio
  de torneos nuevos.
- En `resultados/domain/`: `RankingCompetencia` ya opera por disciplina — cada variante
  SPE crea un ranking separado sin cambios en la lógica de ranking.
- En `torneo/domain/`: agregar validación `DisciplinaObsoleta` al agregar `Disciplina.SPE`
  genérico a un torneo (opcionalmente, como advertencia o excepción según DoD del torneo).

---

*Redactado: 2026-04-08 — INC-4.1 correcciones dominio CMAS/FAAS*
