# US-4.1.4: Orden de grilla reglamentario — ascendente DNF/DYN/DBF/STA, descendente SPE

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.1
**Bounded Context**: `competencia`
**Capas afectadas**: `competencia/domain/`, `shared/domain/value_objects/`

---

## Descripción

Como **organizador**,
quiero **que la grilla de salida se genere con el orden reglamentario correcto**
para **que los atletas compitan en el orden prescrito por CMAS/FAAS, sin necesidad
de reordenarla manualmente**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object (modificado) | `DisciplinaDescriptor` | Corrige `orden_ascendente` para SPE (variantes): `False` en lugar de `True` |
| Entidad (modificado) | `GrillaDeSalida` | Usa el `orden_ascendente` del descriptor — no requiere cambio en la lógica, solo que el descriptor sea correcto |
| Aggregate (verificado) | `Competencia` | `generar_grilla()` pasa `descriptor` a `GrillaDeSalida.generar()` — verificar que el descriptor correcto llega |

### Lenguaje ubicuo relevante

- **Orden ascendente:** menor AP primero, mayor AP al final. Usado en DNF, DYN, DBF, STA.
  El atleta más fuerte (mayor AP) compite al final, cuando la expectativa es mayor.
- **Orden descendente:** mayor AP primero, menor AP al final. Usado en SPE.
  El atleta más lento (mayor tiempo) compite primero, el más rápido al final.
- **Grilla reglamentaria:** grilla generada automáticamente siguiendo la regla de orden
  del reglamento. El organizador puede ajustarla manualmente después, pero el punto
  de partida debe ser correcto.

---

## Especificación del comportamiento

### Regla de orden por familia de disciplina

| Familia | Disciplinas | Orden inicial | Lógica |
|---------|-------------|---------------|--------|
| Estática | STA | Ascendente por AP (segundos) | Menor tiempo declarado primero |
| Dinámica | DNF, DYN, DBF, CNF, CWT, FIM, VWT | Ascendente por AP (metros) | Menor distancia declarada primero |
| Velocidad-resistencia | SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50 | Descendente por AP (segundos) | Mayor tiempo declarado primero (los más lentos) |

### Invariantes del dominio

- **INV-GR-01:** `DisciplinaDescriptor.para(d).orden_ascendente == False` para todo `d` en familia SPE.
- **INV-GR-02:** `DisciplinaDescriptor.para(d).orden_ascendente == True` para todo `d` fuera de SPE.
- **INV-GR-03:** el orden reglamentario es el punto de partida de la grilla generada;
  los ajustes manuales posteriores no violan el reglamento.

### Operación principal

**Nombre**: `generar_grilla(ot_inicio, performances, descriptor, intervalo, andariveles)`

| | Descripción |
|---|---|
| **Precondición** | Competencia en `Configurada`; performances con AP registrados; `descriptor.orden_ascendente` correcto según la disciplina |
| **Postcondición** | Las entradas de la grilla están ordenadas: ascendente para dinámicas, descendente para SPE |
| **Eventos generados** | `GrillaGenerada{entradas: [...ordenadas reglamentariamente...]}` |
| **Excepciones** | (existentes) sin cambios |

**Ejemplo concreto — disciplina DYN:**

```
Precondición:  Competencia DYN, performances:
               A(AP=80m), B(AP=60m), C(AP=75m)
Operación:     generar_grilla(descriptor=DisciplinaDescriptor.para(DYN), ...)
Postcondición: grilla = [B(pos=1, AP=60m), C(pos=2, AP=75m), A(pos=3, AP=80m)]
               (menor AP primero — orden ascendente)
```

**Ejemplo concreto — disciplina SPE_4X50:**

```
Precondición:  Competencia SPE_4X50, performances:
               A(AP=180s), B(AP=210s), C(AP=195s)
Operación:     generar_grilla(descriptor=DisciplinaDescriptor.para(SPE_4X50), ...)
Postcondición: grilla = [B(pos=1, AP=210s), C(pos=2, AP=195s), A(pos=3, AP=180s)]
               (mayor tiempo primero = más lento primero — orden descendente)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.1.4 — Orden de grilla reglamentario

  Scenario: grilla DYN ordena menor AP primero
    Given una competencia DYN con tres performances:
      | atleta | AP    |
      | A      | 80m   |
      | B      | 60m   |
      | C      | 75m   |
    When se genera la grilla
    Then el orden de salida es: B (pos=1), C (pos=2), A (pos=3)

  Scenario: grilla STA ordena menor AP primero en segundos
    Given una competencia STA con tres performances:
      | atleta | AP    |
      | A      | 300s  |
      | B      | 180s  |
      | C      | 240s  |
    When se genera la grilla
    Then el orden de salida es: B (pos=1), C (pos=2), A (pos=3)

  Scenario: grilla SPE_4X50 ordena mayor tiempo primero (más lento primero)
    Given una competencia SPE_4X50 con tres performances:
      | atleta | AP    |
      | A      | 180s  |
      | B      | 210s  |
      | C      | 195s  |
    When se genera la grilla
    Then el orden de salida es: B (pos=1), C (pos=2), A (pos=3)

  Scenario: grilla SPE_2X50 también ordena mayor tiempo primero
    Given una competencia SPE_2X50 con tres performances:
      | atleta | AP    |
      | A      | 70s   |
      | B      | 90s   |
      | C      | 80s   |
    When se genera la grilla
    Then el orden de salida es: B (pos=1), C (pos=2), A (pos=3)

  Scenario: DisciplinaDescriptor para SPE_4X50 tiene orden_ascendente=False
    Given el DisciplinaDescriptor para SPE_4X50
    Then orden_ascendente es False
    And unidad_esperada es Segundos

  Scenario: DisciplinaDescriptor para DNF tiene orden_ascendente=True
    Given el DisciplinaDescriptor para DNF
    Then orden_ascendente es True
    And unidad_esperada es Metros
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — corrección de valor en `DisciplinaDescriptor.para()` para variantes SPE

**Capa(s) afectadas:**
- [x] Domain (`shared/domain/value_objects/disciplina_descriptor.py`)

---

## Referencias

- Plan: `docs/plans/sp4/PLAN-SP4.md §INC-4.1`
- Brechas: `docs/dominio/06-brechas-reglamento.md §6`
- Reglamento: CMAS §1.2.4.3
- Entidad GrillaDeSalida: `src/competencia/domain/entities/grilla_de_salida.py`
- Descriptor: `src/shared/domain/value_objects/disciplina_descriptor.py`

---

## Notas de implementación

- El cambio central es mínimo: en `DisciplinaDescriptor.para()`, agregar rama para
  variantes SPE antes de la rama `es_tiempo()`:
  ```python
  if disciplina.es_spe() and disciplina != Disciplina.SPE:
      return cls(
          disciplina=disciplina,
          unidad_esperada=UnidadMedida.Segundos,
          orden_ascendente=False,
      )
  ```
  (requiere que `es_spe()` esté implementado en US-4.1.3)
- `GrillaDeSalida.generar()` no cambia: ya usa `descriptor.orden_ascendente`.
- `Disciplina.SPE` (genérico) mantiene su descriptor actual (`orden_ascendente=True`,
  `unidad=Metros`) para no romper reconstitución histórica.
- **Dependencia:** esta US requiere que `Disciplina.es_spe()` esté disponible (US-4.1.3).
  Implementar US-4.1.3 primero, o en el mismo branch.

---

*Redactado: 2026-04-08 — INC-4.1 correcciones dominio CMAS/FAAS*
