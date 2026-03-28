# US-2.2.1: DisciplinaDescriptor — VO + Port

**Estado**: `Backlog`
**Incremento**: Inc 2.2 — Dos Mecánicas, un Modelo
**Subproyecto**: SP2 — La Competencia
**Agregado principal**: `Competencia` · `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **sistema**,
quiero **encapsular las reglas de cada disciplina (unidad esperada, orden de grilla) en un objeto explícito**
para **que la lógica de "esta disciplina es de tiempo / de distancia" no quede dispersa como condicionales inline, sino expresada en el modelo de dominio**.

Esta US no introduce nuevos eventos ni endpoints. Es una refactorización de dominio que
prepara el terreno para la validación de unidades en US-2.2.2.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Value Object (existente) | `Disciplina` | Enum de las disciplinas reconocidas (STA, DNF, DYN...) — tiene `es_tiempo()` / `es_distancia()` |
| Value Object (nuevo) | `DisciplinaDescriptor` | Encapsula unidad esperada y regla de orden de grilla para una Disciplina |
| Port (nuevo) | `DisciplinaDescriptorPort` | Permite a los handlers consultar el descriptor sin acoplarse a la implementación |
| Adaptador (nuevo) | `DisciplinaDescriptorAdapter` | Implementación concreta derivada del enum `Disciplina` |

### Lenguaje ubicuo relevante

- **Descriptor de disciplina**: conjunto de reglas que caracterizan cómo se mide y ordena una disciplina. Para STA: unidad = Segundos, orden = mayor a menor AP. Para DNF/DYN/...: unidad = Metros, orden = menor a mayor AP.
- **Unidad esperada**: la única unidad válida para registrar un AP o un RP en una disciplina dada.
- **Orden de grilla**: si los atletas se ordenan con AP ascendente (distancia) o descendente (tiempo).

---

## Especificación del comportamiento

### El Value Object DisciplinaDescriptor

```
DisciplinaDescriptor(
    disciplina: Disciplina,
    unidad_esperada: UnidadMedida,     # Segundos para STA, Metros para el resto
    orden_ascendente: bool,            # False (mayor→menor) para STA; True (menor→mayor) para distancia
)
```

`DisciplinaDescriptor` es inmutable. No puede construirse con combinaciones inválidas
(e.g., STA + Metros es un estado imposible — debe rechazarse con `DescriptorInvalido`).

**Invariante del VO:**
- `DisciplinaDescriptor` para STA → `unidad_esperada = Segundos`, `orden_ascendente = False`
- `DisciplinaDescriptor` para disciplinas de distancia → `unidad_esperada = Metros`, `orden_ascendente = True`

### El Port DisciplinaDescriptorPort

```python
class DisciplinaDescriptorPort:
    def describe(self, disciplina: Disciplina) -> DisciplinaDescriptor: ...
```

### Refactor: _ordenar_performances en Competencia

La función `_ordenar_performances(performances, disciplina)` que usa `disciplina.es_tiempo()`
se refactoriza para aceptar un `DisciplinaDescriptor` y usar `descriptor.orden_ascendente`.

```
# Antes (inline)
reverse = disciplina.es_tiempo()   # True para STA, False para distancia

# Después (descriptor)
reverse = not descriptor.orden_ascendente
```

`Competencia.generar_grilla()` recibe el `descriptor` como parámetro adicional.
El handler `GenerarGrillaHandler` lo obtiene del `DisciplinaDescriptorPort` e inyecta.

### Operación: construir un DisciplinaDescriptor

| | Descripción |
|---|---|
| **Precondición** | `disciplina` es un valor válido del enum `Disciplina` |
| **Postcondición** | Retorna un `DisciplinaDescriptor` inmutable con `unidad_esperada` y `orden_ascendente` correctos para esa disciplina |
| **Excepciones** | `DescriptorInvalido` si se intenta construir un descriptor con combinación imposible (no aplica vía port — solo en construcción directa) |

**Ejemplo concreto:**

```
Port.describe(Disciplina.STA)
→ DisciplinaDescriptor(STA, Segundos, orden_ascendente=False)

Port.describe(Disciplina.DNF)
→ DisciplinaDescriptor(DNF, Metros, orden_ascendente=True)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: DisciplinaDescriptor — VO que encapsula reglas de disciplina

  Scenario: Descriptor STA retorna unidad Segundos y orden descendente
    Given la disciplina es "STA"
    When se consulta el DisciplinaDescriptorPort
    Then unidad_esperada es "Segundos"
    And orden_ascendente es False

  Scenario: Descriptor DNF retorna unidad Metros y orden ascendente
    Given la disciplina es "DNF"
    When se consulta el DisciplinaDescriptorPort
    Then unidad_esperada es "Metros"
    And orden_ascendente es True

  Scenario: GenerarGrilla usa descriptor para ordenar STA (mayor AP primero)
    Given una competencia STA con 3 atletas: AP 120s, 300s, 180s
    And el intervalo OT está configurado en 9 minutos
    When se genera la grilla usando el DisciplinaDescriptorPort
    Then el orden de la grilla es: 300s → 180s → 120s (mayor AP primero)

  Scenario: GenerarGrilla usa descriptor para ordenar DNF (menor AP primero)
    Given una competencia DNF con 3 atletas: AP 80m, 40m, 60m
    And el intervalo OT está configurado en 9 minutos
    When se genera la grilla usando el DisciplinaDescriptorPort
    Then el orden de la grilla es: 40m → 60m → 80m (menor AP primero)
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [ ] No — es una refactorización interna al BC Competencia con la arquitectura existente

**Capas afectadas:**
- [x] Domain — `DisciplinaDescriptor` VO nuevo; `DisciplinaDescriptorPort`; refactor de `_ordenar_performances` y firma de `generar_grilla()`
- [x] Application — `GenerarGrillaHandler` inyecta `DisciplinaDescriptorPort` e invoca `describe()`
- [x] Infrastructure — `DisciplinaDescriptorAdapter` implementación concreta del port

**Impacto en tests existentes:**
- `test_generar_grilla_*` deben proveer un `DisciplinaDescriptorPort` (el adapter real o un test double)
- El adapter real es determinista (deriva del enum) — se puede usar directamente en tests de integración

---

## Notas de implementación

- `DisciplinaDescriptorAdapter` vive en `infrastructure/repositories/` o en `infrastructure/` directamente — es una implementación sin I/O.
- `Competencia.generar_grilla()` recibe `descriptor: DisciplinaDescriptor` como parámetro (no el port — el aggregate no conoce ports). El handler resuelve el descriptor y lo pasa.
- La lógica de `es_tiempo()` / `es_distancia()` en el enum `Disciplina` puede mantenerse como helpers internos; `DisciplinaDescriptor` es la superficie pública para los handlers.

---

## Referencias

- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Política P-01
- SP2 candidatas: `docs/plans/sp2/SP2-candidatas.md` — Inc 2.2, US-2.2.1
- RF-EJ-08 (decimales en distancia) · RF-PR-05 (criterio de ordenamiento)
- US-2.2.2 depende de este port para la validación de unidades en `RegistrarResultado`

---

*Redactado: 2026-03-26 — IEDD Capa 3*
