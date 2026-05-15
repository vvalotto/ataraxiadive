# US-ADJ-10.4: Vista post-torneo en portal del atleta — observación post-UAT SP6

**Estado**: `Implementada`
**Iteracion / Sprint**: SP-ADJ-10
**Tipo**: ajuste UX frontend
**Agregado principal afectado**: —
**Bounded Context**: frontend atleta

---

## Descripcion (lenguaje de negocio)

Como **atleta**,
quiero ver un resumen de mis resultados finales en torneos cerrados tanto desde el home
de mi portal como desde el detalle del torneo
para poder consultar mis performances y posiciones sin perder el acceso cuando el torneo
ya finalizó.

---

## Contexto del dominio

### Problema

Cuando un torneo pasa a estado `CERRADO`, desaparece completamente del home del atleta
(`AtletaHomePage` filtra solo `PREPARACION`/`EJECUCION`). No hay rastro del torneo ni
de sus resultados en la pantalla principal del portal.

`AtletaTorneoDetallePage` para estado `CERRADO` solo muestra información básica
(sede, fecha) y el badge "Ya estás inscripto" — no hay resultados finales inline.

`AtletaResultadosPage` ya muestra resultados para `CERRADO` correctamente, pero no
es el punto de entrada natural cuando el atleta busca "qué pasó en el último torneo".

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | `AtletaHomePage` | Home del portal atleta — punto de entrada principal |
| Page | `AtletaTorneoDetallePage` | Detalle de un torneo específico del atleta |
| Page | `AtletaResultadosPage` | Vista completa de resultados — ya soporta CERRADO |
| Componente | `ResultHero` | Tarjeta de resultado individual (tarjeta, RP, AP, diferencia, podio) |
| Componente | `RankingCard` | Ranking de la categoría del atleta en una disciplina |
| Componente | `OverallCard` | Puntuación y posición FAAS overall del torneo |

---

## Especificacion del comportamiento

### Precondicion

El atleta está inscripto en al menos un torneo que pasó al estado `CERRADO` y tiene
resultados registrados (al menos una performance o DNS).

### Postcondicion

- `AtletaHomePage` muestra una sección "Torneos finalizados" con los torneos CERRADO
  en los que el atleta participó, con resultado rápido por disciplina.
- `AtletaTorneoDetallePage` en estado `CERRADO` muestra los resultados finales del atleta
  para ese torneo usando los mismos componentes que `AtletaResultadosPage`.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-10.4-01 | La sección "Torneos finalizados" solo muestra torneos en estado `CERRADO` — no `PREMIACION` ni otros. |
| INV-ADJ-10.4-02 | Si el atleta no tiene resultados en un torneo cerrado (DNS en todas las disciplinas), se muestra un estado vacío adecuado, no un error. |
| INV-ADJ-10.4-03 | Los torneos en `EJECUCION` y `PREMIACION` no son afectados — siguen apareciendo en las secciones actuales del home. |
| INV-ADJ-10.4-04 | `AtletaTorneoDetallePage` en estado `CERRADO` reutiliza los componentes y APIs existentes de `AtletaResultadosPage` — sin duplicar lógica. |
| INV-ADJ-10.4-05 | La sección "Torneos finalizados" muestra como máximo los 3 torneos cerrados más recientes — el resto es accesible desde "Mis Resultados". |

---

## Criterios de aceptacion

```gherkin
Feature: Vista post-torneo en portal del atleta

  Scenario: Home muestra torneos cerrados con resultado rápido
    Given el atleta participó en el torneo "BA Open 2025" que está CERRADO
    And tiene resultado DNF: Tarjeta Blanca, RP 60m, posición 3 en su categoría
    When navega al home del portal del atleta
    Then ve una sección "Torneos finalizados"
    And la sección muestra "BA Open 2025" con una tarjeta que indica DNF, Blanca, 60m y posición 3

  Scenario: Home muestra badge de podio si el atleta quedó en podio
    Given el atleta quedó en posición 2 (medalla de plata) en STA
    When navega al home del portal del atleta
    Then la tarjeta del torneo muestra un indicador de podio para STA

  Scenario: Detalle del torneo CERRADO muestra resultados finales completos
    Given el torneo "BA Open 2025" está en estado CERRADO
    And el atleta participó en DNF y STA
    When navega al detalle del torneo desde el portal
    Then ve sus ResultHero por disciplina con tarjeta, RP, AP y diferencia
    And ve RankingCard con su posición en la categoría
    And ve OverallCard con sus puntos FAAS

  Scenario: Detalle del torneo CERRADO con DNS en todas las disciplinas
    Given el atleta registró DNS en todas sus disciplinas en un torneo CERRADO
    When navega al detalle del torneo
    Then ve un mensaje apropiado indicando que no compitió
    And no muestra error

  Scenario: Torneos en EJECUCION no aparecen en "Torneos finalizados"
    Given el atleta tiene un torneo activo en EJECUCION y otro CERRADO
    When navega al home del portal
    Then el torneo en EJECUCION aparece en "Torneos vinculados" o "Próxima salida"
    And el torneo CERRADO aparece en "Torneos finalizados"
    And no hay mezcla entre las secciones

  Scenario: Home sin torneos cerrados no muestra la sección
    Given el atleta no tiene ningún torneo en estado CERRADO
    When navega al home del portal
    Then no aparece la sección "Torneos finalizados"
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — es frontend puro. Reutiliza los mismos queries (`fetchRankingCompetencia`,
  `fetchOverall`, `fetchGrillaCompetencia`) y componentes (`ResultHero`, `RankingCard`,
  `OverallCard`) que ya usa `AtletaResultadosPage`.

**Capa(s) afectadas:**
- [x] Frontend — `AtletaHomePage` + `AtletaTorneoDetallePage`.
- [ ] Backend — sin cambios.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/pages/atleta/AtletaHomePage.tsx` | Agregar sección "Torneos finalizados" debajo de "Mis inscripciones activas". Filtra `entries` con `torneo.estado === 'CERRADO'`, agrupa por torneo, muestra tarjeta de resultado rápido por disciplina (máximo 3 torneos). |
| `frontend/src/pages/atleta/AtletaTorneoDetallePage.tsx` | Para `torneo.estado === 'CERRADO'`: cargar rankings y overall del atleta y renderizar `ResultHero` + `RankingCard` + `OverallCard` en lugar del bloque estático actual. |

---

## Notas de implementacion

1. La tarjeta de resultado rápido en el home puede ser un componente nuevo liviano
   (ej. `ResultadoRapidoCard`) que muestre: disciplina, tarjeta (color), RP, posición y badge
   de podio. No requiere el ranking completo de la categoría.
2. `AtletaTorneoDetallePage` en modo CERRADO monta queries solo cuando `torneo.estado === 'CERRADO'`
   y el atleta tiene inscripción — evita queries innecesarias en el caso general.
3. Para la sección del home, reutilizar `loadAtletaPortalSnapshot` ya disponible; los datos
   de resultado rápido pueden obtenerse de `fetchRankingCompetencia` ya cacheado por
   `AtletaResultadosPage` si el atleta navegó por ahí previamente.
4. El límite de 3 torneos en "Torneos finalizados" puede acompañarse de un link "Ver todos"
   que navega a `AtletaResultadosPage`.

---

*Spec creada: 2026-05-14 — observación post-UAT SP6*
