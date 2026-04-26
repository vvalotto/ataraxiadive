# US-5.6.6: UI podios — 6 divisiones por categoría/género

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.6
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/organizador/ResultadosPage.tsx`, `frontend/src/components/organizador/`

---

## Descripcion

Como **organizador**,
quiero **ver los podios de cada disciplina separados por las 6 categorías (SENIOR M/F, MASTER M/F, JUNIOR M/F) con puntaje, nombre, club y RP, y el Overall del torneo cuando todas las disciplinas estén cerradas**,
para **proclamar los campeones por categoría y género al cierre de cada disciplina y del torneo completo**.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §S-04 Resultados`
- `docs/plans/sp5/PLAN-SP5.md §Presentación de Resultados — Vista 2`
- `docs/design/ux/decisiones-frontend.md §D-04, §D-05`

---

## Contexto de diseño

Los podios viven dentro de la misma página `ResultadosPage` (S-04), en una sección separada de la tabla de ejecución. La estructura usa el mismo tema dark y tokens del panel del organizador.

La sección de podios **por disciplina** muestra resultados agrupados en 6 paneles: uno por cada `Categoria`. La sección **Overall** se activa solo cuando todas las disciplinas del torneo están cerradas.

---

## Alcance funcional

### A. Podios por disciplina

Al seleccionar una disciplina finalizada en el selector (US-5.6.5), debajo de la tabla de ejecución aparece la sección "Podios".

**Estructura de la sección Podios:**

```
Podios — [Nombre disciplina]

[SENIOR M]    [SENIOR F]    [MASTER M]    [MASTER F]    [JUNIOR M]    [JUNIOR F]
  1º Atleta     1º Atleta     ...
  2º Atleta     2º Atleta
  3º Atleta     3º Atleta
```

**Por cada panel de categoría:**

| Columna | Descripción |
|---------|-------------|
| Posición | 1º, 2º, 3º — con medallas (oro/plata/bronce); posiciones 4+ sin medalla |
| Nombre | Apellido, Nombre |
| Club | Nombre del club |
| RP | Resultado realizado |
| Puntos | Puntos FAAS — `--accent` bold |

Si una categoría tiene menos de 3 atletas (o 0), el panel muestra los atletas disponibles sin posiciones vacías. Si una categoría tiene 0 participantes: panel con empty state "Sin participantes".

### B. Overall del torneo

Una sección "Overall" aparece debajo de los podios por disciplina. Mientras no todas las disciplinas estén finalizadas, muestra el estado de disponibilidad como en `wireframes-organizador.md §S-04`:

```
🏆  Disponible al cerrar todas las disciplinas
    (N de M disciplinas cerradas)
```

Cuando el Overall está disponible, la sección muestra los mismos 6 paneles pero con `puntos_overall` (suma de todas las disciplinas).

### C. Colores de posición (podio)

| Posición | Color del badge |
|----------|----------------|
| 1º | Oro (`#f59e0b` / `text-amber-400`) |
| 2º | Plata (`#94a3b8` / `text-slate-400`) |
| 3º | Bronce (`#b45309` / `text-amber-700`) |
| 4º+ | Muted (`--muted`) |

---

## Invariantes

- **INV-5.6.6-01**: los podios solo se muestran si la disciplina está FINALIZADA y el ranking tiene `puntos` calculados.
- **INV-5.6.6-02**: la sección Overall está oculta (o en empty state) mientras haya disciplinas sin finalizar.
- **INV-5.6.6-03**: la agrupación de podios usa exactamente las 6 `Categoria` del enum; no se crean grupos dinámicamente.
- **INV-5.6.6-04**: los atletas dentro de cada panel están ordenados por puntos descendente; en empate, comparten posición (mismo número).
- **INV-5.6.6-05**: solo el organizador autenticado puede ver esta sección.

---

## Especificacion del comportamiento

### Fuente de datos

```text
Podios por disciplina:
  GET /resultados/{competencia_id}/ranking
  → entries agrupadas por Categoria, ordenadas por puntos desc

Overall:
  GET /resultados/{torneo_id}/overall
  → entries agrupadas por Categoria con puntos_overall
```

### Condiciones de visibilidad

```text
Podios disciplina:
  - visible si: disciplina.estado == "FINALIZADA" AND ranking calculado

Overall:
  - empty state si: alguna disciplina sin FINALIZADA
  - visible si: todas las disciplinas FINALIZADAS AND overall calculado
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.6.6 — UI podios por categoría/género

  Background:
    Given el organizador está autenticado
    And existe el torneo "BA Open 2026" con disciplina DNF

  Scenario: podio de disciplina muestra 6 paneles al finalizar
    Given la disciplina DNF está FINALIZADA con ranking calculado
    And hay atletas en SENIOR_MASCULINO, SENIOR_FEMENINO y JUNIOR_MASCULINO
    When el organizador selecciona DNF en ResultadosPage
    Then ve 6 paneles: SENIOR M, SENIOR F, MASTER M, MASTER F, JUNIOR M, JUNIOR F
    And los paneles sin atletas muestran "Sin participantes"

  Scenario: posiciones correctas por puntos dentro de cada categoria
    Given el ranking DNF tiene:
      - SENIOR_MASCULINO: Luis 80.00 pts, Pedro 60.00 pts
    When el organizador ve el panel SENIOR M
    Then Luis aparece en posicion 1 con badge oro
    And Pedro aparece en posicion 2 con badge plata

  Scenario: empate en puntos comparte posicion
    Given en SENIOR_FEMENINO Ana y Maria tienen 100.00 puntos cada una
    When el organizador ve el panel SENIOR F
    Then Ana y Maria aparecen ambas con posicion 1

  Scenario: overall en empty state mientras hay disciplinas pendientes
    Given el torneo tiene DNF finalizado y STA pendiente
    When el organizador ve la seccion Overall
    Then muestra el estado "Disponible al cerrar todas las disciplinas (1 de 2 cerradas)"

  Scenario: overall disponible al cerrar todas las disciplinas
    Given todas las disciplinas del torneo están FINALIZADAS
    And el overall fue calculado
    When el organizador ve la seccion Overall
    Then los 6 paneles muestran puntos_overall acumulados por categoria

  Scenario: podios no visibles con disciplina aun en ejecucion
    Given la disciplina DNF está EN EJECUCION (no finalizada)
    When el organizador selecciona DNF
    Then la sección Podios no se muestra (o muestra empty state)
```

---

## Impacto arquitectonico

- [x] Frontend — sección `PodiosSection` dentro de `ResultadosPage.tsx`
- [x] Frontend — componentes `PanelCategoria`, `FilaPodio` en `frontend/src/components/organizador/`
- [x] API client — `frontend/src/api/resultados.ts` con tipo `EntradaOverall` actualizado

### Componentes a crear / modificar

```
frontend/src/pages/organizador/
└── ResultadosPage.tsx               ← añadir sección Podios + Overall

frontend/src/components/organizador/
├── PodiosSection.tsx                ← contenedor de 6 paneles
├── PanelCategoria.tsx               ← panel por categoría (grilla o lista)
└── FilaPodio.tsx                    ← fila: posición + medalla, nombre, club, RP, puntos
```

---

## Referencias

- `docs/design/ux/wireframes-organizador.md §S-04 Resultados`
- `docs/plans/sp5/PLAN-SP5.md §Presentación de Resultados — Vista 2`
- `US-5.6.3` — `EntradaRanking.puntos` agrupado por `Categoria`
- `US-5.6.4` — `EntradaOverall.puntos_overall`
- `US-5.6.5` — `ResultadosPage` donde se integra esta sección
- `src/registro/domain/value_objects/categoria.py` — 6 valores del enum

---

*Redactado: 2026-04-26 — INC-5.6*
