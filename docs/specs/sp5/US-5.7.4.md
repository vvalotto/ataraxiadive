# US-5.7.4: Rankings y podios de las disciplinas del atleta

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.7
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/atleta/AtletaResultadosPage.tsx`, `frontend/src/components/atleta/`

---

## Descripcion

Como **atleta**,
quiero **ver el ranking completo y el podio de cada disciplina en la que participé, con mi posición resaltada**,
para **conocer cómo quedé posicionado respecto al resto de los competidores en mi categoría y en el ranking general**.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-atleta.md §S-08 Mis Resultados — Ranking de disciplina + Ranking general`
- `docs/design/ux/flujos-por-rol.md §3 Rol: Atleta`

---

## Contexto de diseño

Esta US extiende `AtletaResultadosPage` (ya implementada en US-5.7.3) agregando:
1. El ranking completo por categoría de cada disciplina inscripta, con el atleta resaltado
2. El ranking overall (si está disponible)

El endpoint `GET /resultados/{competencia_id}/ranking` devuelve `RankingCompetenciaDto` con `rankings: RankingCategoriaDto[]`, donde cada categoría tiene `entradas: RankingEntradaDto[]` (con `posicion`, `atleta_id`, `rp`, `puntos`, `en_podio`). No incluye `nombre_atleta` — se necesita cruzar con la grilla para obtener nombres.

---

## Alcance funcional

### A. Ranking por disciplina — dentro de cada sección de torneo

Debajo del `ResultHero` de cada disciplina (US-5.7.3), agregar una card de ranking:

- **Título:** `Ranking [CATEGORIA]` (ej. "Ranking SENIOR F")
- **Filas:** `RankingRow` por cada entrada de la categoría del atleta
- **Distinción top 3:** íconos 🥇🥈🥉 o badges de posición
- **Resalte del atleta:** fila propia con fondo accent tenue + texto "Vos" al lado del nombre
- **Pie:** "Ranking parcial" si `calculado === false`, "Ranking final" si `calculado === true`

**Columnas por fila:**

| Columna | Fuente |
|---------|--------|
| Posición | `entrada.posicion` |
| Nombre | cruzado con grilla por `atleta_id` |
| RP | `entrada.rp` + unidad |
| Puntos | `entrada.puntos` |
| Estado | chip Blanca / Roja / DNS |

### B. Filtro por categoría propia del atleta

El ranking muestra solo la categoría del atleta (la que coincide con la categoría de su inscripción). No se muestran todas las categorías — solo la propia.

### C. Ranking Overall

Al pie de la página (después de todas las disciplinas), mostrar la sección Overall:

- **Visible solo cuando** `GET /resultados/{torneo_id}/overall` devuelve datos (`rankings` no vacíos)
- **Estado vacío:** ícono trofeo + "Disponible al finalizar todas las disciplinas del torneo" (INV-ATL-06)
- **Contenido cuando disponible:**
  - `OverallCategoriaDto[]` con `entradas[]` (`posicion`, `atleta_id`, `puntos_overall`)
  - Solo muestra la categoría propia del atleta
  - Fila propia resaltada

### D. Obtención de nombres de atletas

`RankingEntradaDto` no incluye `nombre_atleta`. Para mostrar nombres en el ranking:

```text
Opción: cruzar con GrillaAtletaDto[]
  → GET /competencia/{competenciaId}/grilla
  → construir mapa atleta_id → nombre_atleta
  → usar para renderizar filas del ranking
```

Si la grilla no está disponible (competencia sin grilla confirmada), mostrar `atleta_id` truncado como fallback.

---

## Invariantes

- **INV-5.7.4-01:** El ranking solo muestra la categoría del atleta — no todas las categorías de la disciplina.
- **INV-5.7.4-02:** La fila propia siempre está resaltada visualmente (fondo accent tenue), independientemente de la posición.
- **INV-5.7.4-03:** El ranking Overall permanece oculto o en estado vacío hasta que el endpoint devuelva datos (INV-ATL-06).
- **INV-5.7.4-04:** Si `ranking.calculado === false`, el pie muestra "Ranking parcial"; si `true`, "Ranking final".
- **INV-5.7.4-05:** Si el atleta tiene DNS (`es_dns === true`), aparece en el ranking en última posición con Puntos = 0.

---

## Especificacion del comportamiento

### Flujo de datos extendido (sobre US-5.7.3)

```text
Por cada competencia con ranking calculado:
  GET /resultados/{competencia_id}/ranking    (ya cargado en US-5.7.3)
  GET /competencia/{competencia_id}/grilla    (para nombres)
  → construir Map<atleta_id, nombre_atleta>
  → filtrar RankingCategoriaDto donde categoría === categoriaAtleta
  → renderizar RankingCard con filas y resalte propio

Al finalizar todas las disciplinas:
  GET /resultados/{torneo_id}/overall
  → si rankings vacíos → mostrar estado vacío
  → si rankings con datos → mostrar OverallCard con categoría propia
```

### Determinación de categoría propia

La categoría del atleta se obtiene de la inscripción (`Inscripcion.categoria`) — ya disponible en el snapshot cargado en US-5.7.3.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.7.4 — Rankings y podios del atleta

  Background:
    Given el atleta "ana@email.com" (atleta_id="aaa", categoría="SENIOR_F") está autenticado
    And existe la competencia DNF con ranking calculado
    And el ranking SENIOR_F de DNF tiene: Ana pos=1 100pts, Laura pos=2 85pts, María pos=3 72pts
    And el torneo NO tiene overall aún

  Scenario: atleta ve el ranking de su categoría con su fila resaltada
    When Ana navega a /atleta/resultados
    Then ve la card "Ranking SENIOR F" bajo el ResultHero de DNF
    And la fila de Ana tiene fondo accent tenue y texto "Vos"
    And las primeras 3 posiciones muestran distinción visual (top 3)
    And al pie muestra "Ranking final"

  Scenario: overall no disponible muestra estado vacío
    When Ana navega a la sección Overall
    Then ve el ícono trofeo y el texto "Disponible al finalizar todas las disciplinas del torneo"
    And no muestra filas de ranking

  Scenario: overall disponible muestra categoría propia con resalte
    Given el overall fue calculado con Ana pos=2 en SENIOR_F con 185 pts
    When Ana navega a resultados
    Then ve la sección "Ranking Overall SENIOR F"
    And la fila de Ana tiene fondo accent tenue y posición 2

  Scenario: ranking parcial muestra pie con advertencia
    Given el ranking de STA tiene calculado=false
    When Ana ve el ranking de STA
    Then el pie de la card dice "Ranking parcial"

  Scenario: atleta con DNS aparece en el ranking en ultima posicion
    Given Ana tiene DNS en DNF (es_dns=true)
    When Ana ve el ranking de DNF
    Then la fila de Ana aparece al final con Puntos=0 y chip "DNS"
```

---

## Impacto arquitectonico

- [x] Frontend — extiende `AtletaResultadosPage.tsx` (ya modificada en US-5.7.3)
- [x] Frontend — nuevos componentes `RankingCard` y `RankingRow`

### Componentes a crear

```
frontend/src/components/atleta/
├── RankingCard.tsx             ← card de ranking por categoría (definida en wireframes)
├── RankingRow.tsx              ← fila con pos, nombre, RP, puntos, chip + isSelf (definida en wireframes)
└── OverallCard.tsx             ← sección overall con estado vacío o datos
```

### Datos adicionales a cargar en AtletaResultadosPage

Por cada competencia con ranking, agregar llamada a `GET /competencia/{competenciaId}/grilla` para construir el mapa `atleta_id → nombre`.

---

## Referencias

- `docs/design/ux/wireframes-atleta.md §S-08 — rank-row, ranking-card, overall-empty`
- `frontend/src/api/resultados.ts` — `fetchRankingCompetencia`, `fetchOverallRanking`, tipos
- `frontend/src/api/competencia.ts` — `fetchGrillaCompetencia` (para nombres)
- `US-5.7.3` — infraestructura de carga de datos ya establecida

---

*Redactado: 2026-04-30 — INC-5.7*
