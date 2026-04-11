# US-4.3.5: Adaptación STA — "Vías respiratorias en agua" en el Paso 3

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.3
**Bounded Context**: `frontend` (sin cambios en backend)
**Capas afectadas**: `frontend/src/pages/juez/PasosPerformance.tsx`

---

## Descripción

Como **juez de una disciplina STA (Static Apnea)**,
quiero **que el Paso 3 muestre el botón "Vías respiratorias en agua" en lugar de "Atleta inicia"**
para **respetar la reglamentación CMAS que define el inicio del cronómetro en el momento en que las vías respiratorias del atleta entran en contacto con el agua, no cuando el atleta "inicia" voluntariamente**.

---

## Contexto del dominio

### Lenguaje ubicuo relevante

- **STA (Static Apnea):** disciplina de apnea estática en piscina. El atleta flota en la superficie y contiene la respiración el mayor tiempo posible.
- **Vías respiratorias en agua:** el momento reglamentario de inicio del cronómetro en STA — cuando la boca/nariz del atleta entran en contacto con el agua. Es distinto del "inicio voluntario" de las disciplinas de distancia.
- **OT (Official Top):** igual que en otras disciplinas — ventana de ±30s para que el atleta inicie.

### Diferencia reglamentaria STA vs disciplinas de distancia

| Aspecto | DNF / CWTB / FIM / CNF | STA |
|---------|------------------------|-----|
| Inicio cronómetro | Toque de superficie / inicio del buceo | Vías respiratorias en agua |
| Botón Paso 3 | "▶ ATLETA INICIA" (verde) | "💧 VÍAS RESPIRATORIAS EN AGUA" (verde) |
| Descripción | "El atleta comienza a bucear" | "Las vías respiratorias del atleta entran en contacto con el agua" |
| Backend | Sin diferencia — mismo `registrar_resultado` con unidad `Segundos` | Ídem |

---

## Especificación del comportamiento

### Invariantes

- **INV-4.3.5-01:** La variante del Paso 3 se determina por `disciplina === "STA"`. El resto de los pasos (1, 2, 4, 5, 6) son idénticos para todas las disciplinas.
- **INV-4.3.5-02:** El cronómetro del Paso 4 arranca en el momento del tap, independientemente del label del botón.
- **INV-4.3.5-03:** La ventana OT (±30s) funciona igual que en otras disciplinas. El botón aparece solo durante la ventana activa.

### Operación principal

**Nombre**: `iniciarSTA()` — variante del mismo `iniciarPerformance()` de US-4.3.2

| | Descripción |
|---|---|
| **Precondición** | Disciplina es `STA`. Ventana OT activa (countdown entre 30s y 0s). |
| **Postcondición** | Cronómetro arranca. UI pasa al Paso 4. El backend NO recibe ninguna llamada en este momento (igual que el Paso 3 estándar). |
| **Diferencia con estándar** | Solo el label del botón y la descripción contextual cambian. La lógica de negocio es idéntica. |

**Ejemplo concreto:**

```
Disciplina: STA
Precondición:  atleta Rodríguez, Pedro — Llamada, OT activo (countdown 15s)
Paso 3 STA:    Botón "💧 VÍAS RESPIRATORIAS EN AGUA" visible (verde)
               Descripción: "Las vías respiratorias del atleta entran en contacto con el agua"
Tap:           Cronómetro arranca (Paso 4)
Paso 5:        Juez ingresa tiempo en segundos (RpSelector en modo Segundos)
               Unidad: Segundos (no Metros)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.3.5 — Adaptación STA en el Paso 3

  Background:
    Given el juez "juez@ataraxia.com" está autenticado
    And la competencia C1 es de disciplina STA
    And el atleta "Rodríguez, Pedro" tiene AP 4m30s en AnunciadaAP

  Scenario: Paso 3 en STA muestra botón adaptado
    Given el juez llamó a Rodríguez y está en el Paso 3
    And la ventana OT está activa
    Then el botón muestra "💧 VÍAS RESPIRATORIAS EN AGUA" (no "ATLETA INICIA")
    And hay un texto descriptivo "Las vías respiratorias del atleta entran en contacto con el agua"

  Scenario: tap en botón STA arranca el cronómetro normalmente
    Given el juez está en el Paso 3 de STA con ventana activa
    When toca "💧 VÍAS RESPIRATORIAS EN AGUA"
    Then el cronómetro arranca en el Paso 4
    And la UI avanza al Paso 4 normalmente

  Scenario: Paso 3 en DNF muestra botón estándar
    Given el juez está en el Paso 3 de una disciplina DNF
    Then el botón muestra "▶ ATLETA INICIA"
    And no hay mención de "vías respiratorias"

  Scenario: RpSelector en modo Segundos para STA
    Given el juez llegó al Paso 5 de STA
    Then el RpSelector muestra minutos y segundos (no metros y cm)
    And los presets son "2:00 | 3:00 | 4:00 | 5:00 | 6:00"
    And el ajuste es en segundos (−5s | +5s | +30s | +1m)
```

---

## Impacto arquitectónico

- [x] No — cambio de presentación pura en el frontend. Sin cambios en el backend.

**Capa(s) afectadas:**
- [x] Frontend — `PasosPerformance.tsx` — condicional `disciplina === "STA"` para el Paso 3

---

## Referencias

- Wireframes: `docs/design/ux/wireframes-juez.md §S-05` (nota de variante STA)
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §US-4.3.5`
- Reglamento CMAS: definición de inicio del cronómetro en STA (vías respiratorias en agua)

---

## Notas de implementación

- **Detección de disciplina STA:** leer `useCompetenciaStore.disciplinaActiva === "STA"`. Pasar como prop `isSTA: boolean` al componente `OtWindow`.
- **`OtWindow` props:** `{ otTime, onInicia, onDq, isSTA }`. Si `isSTA`, mostrar label alternativo y descripción contextual.
- **RpSelector en modo Segundos:** el Paso 5 necesita manejar el formato MM:SS en lugar de metros+cm cuando `disciplina === "STA"`. La unidad que se envía al backend es `"Segundos"` (el backend ya lo soporta desde SP1).
- **Presets para STA:** en lugar de `[25, 50, 75, 100, 125]` metros, usar `[120, 180, 240, 300, 360]` segundos (2:00, 3:00, 4:00, 5:00, 6:00). Display en formato MM:SS.
- **Sin cambios en el dominio:** `registrar_resultado` con `unidad=Segundos` ya funciona para STA. Esta US es puramente de UI.

---

*Redactado: 2026-04-11 — INC-4.3 Interfaz del Juez*
