# US-5.7.3: Mis Resultados — RP, tarjeta y puntos por disciplina

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.7
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/atleta/AtletaResultadosPage.tsx` (reemplazar placeholder), `frontend/src/components/atleta/`

---

## Descripcion

Como **atleta**,
quiero **ver mi resultado personal en cada disciplina en la que competí — RP, tarjeta y puntos FAAS obtenidos**,
para **conocer mi desempeño en cuanto el organizador publica los resultados de cada disciplina**.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-atleta.md §S-08 Mis Resultados`
- `docs/design/ux/flujos-por-rol.md §3 Rol: Atleta`

---

## Contexto de diseño

`AtletaResultadosPage` existe pero es un placeholder (`"Resultados aún no publicados"`). Esta US implementa el contenido real de S-08 — la sección de resultados personales por disciplina.

El ranking completo (con todos los atletas y podios) se implementa en US-5.7.4 sobre la misma página. Esta US cubre solo la sección del **resultado propio** del atleta.

### Estructura de datos disponible

- `GET /registro/atletas/me` → `atleta_id`
- `GET /registro/atletas/{atleta_id}/inscripciones` → lista de inscripciones con `torneo_id` y `disciplinas`
- `GET /competencia` → competencias del torneo (para obtener `competencia_id` por disciplina)
- `GET /resultados/{competencia_id}/ranking` → `RankingCompetenciaDto` con `rankings[].entradas[]` — cada entrada tiene `atleta_id`, `rp`, `tarjeta`, `puntos`, `es_dns`, `en_podio`

El join se realiza en el frontend: para cada disciplina inscripta, buscar en `ranking.rankings` la entrada donde `entrada.atleta_id === atletaId`.

---

## Alcance funcional

### A. Sección por disciplina — ResultHero

Por cada disciplina en la que el atleta está inscripto, mostrar un `ResultHero`:

| Campo | Fuente | Notas |
|-------|--------|-------|
| Disciplina | inscripcion.disciplina | Nombre legible (DNF → "Dinámica sin Aletas") |
| Estado visual | `tarjeta` | Blanca / Roja / DNS / Pendiente |
| RP | `entrada.rp` | en metros o mm:ss según disciplina |
| AP declarado | grilla o inscripcion | para mostrar diferencia |
| Diferencia AP-RP | calculada en frontend | `+3m` / `-2m` |
| Puntos FAAS | `entrada.puntos` | "—" si no calculado |
| Chip `EN PODIO` | `entrada.en_podio === true` | accent / badge destacado |

**Estados visuales del ResultHero:**

| Estado | Clase CSS / estilo |
|--------|--------------------|
| Tarjeta blanca | border verde, chip "BLANCA" |
| Tarjeta roja | border rojo, chip "ROJA" |
| DNS | border gris, chip "DNS", RP = "—" |
| Pendiente (sin resultado) | border slate, chip "PENDIENTE", todos los campos = "—" |

### B. Disciplina pendiente

Si el atleta está inscripto pero el ranking aún no fue calculado (`ranking.calculado === false` o la entrada no existe en el ranking), mostrar card de disciplina pendiente:

- OT programado (si existe en grilla)
- AP declarado
- andarivel
- chip "PENDIENTE"
- texto "Resultado disponible al cierre de la disciplina"

---

## Invariantes

- **INV-5.7.3-01:** Solo se muestra el resultado del atleta autenticado — no de otros atletas.
- **INV-5.7.3-02:** Si `ranking.calculado === false`, todos los campos de resultado muestran "—" y la disciplina aparece como pendiente.
- **INV-5.7.3-03:** El chip "EN PODIO" solo aparece cuando `entrada.en_podio === true`.
- **INV-5.7.3-04:** La diferencia AP-RP se muestra con signo: `+3m` si superó el AP, `-2m` si quedó por debajo; "—" si no hay RP.

---

## Especificacion del comportamiento

### Flujo de datos

```text
AtletaResultadosPage
  → GET /registro/atletas/me                         (atleta_id)
  → GET /registro/atletas/{atleta_id}/inscripciones  (torneos + disciplinas)
  → por cada torneo inscripto:
      GET /competencia?torneo_id={torneo_id}          (competencias del torneo)
  → por cada competencia:
      GET /resultados/{competencia_id}/ranking        (RankingCompetenciaDto)
  → por cada disciplina inscripta:
      miEntrada = ranking.rankings
        .flatMap(cat => cat.entradas)
        .find(e => e.atleta_id === atletaId)
  → mostrar ResultHero con miEntrada o card pendiente
```

### Agrupación

Las disciplinas se agrupan por torneo. Si el atleta está inscripto en más de un torneo, aparece una sección por torneo con su nombre como encabezado.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.7.3 — Mis resultados por disciplina

  Background:
    Given el atleta "ana@email.com" (atleta_id="aaa") está autenticado
    And Ana está inscripta en "BA Open 2026" en DNF y STA
    And la disciplina DNF está FINALIZADA con ranking calculado
    And Ana obtuvo en DNF: RP=70m, Blanca, 100.00 puntos, en_podio=true, AP=68m
    And la disciplina STA aún no tiene ranking calculado

  Scenario: resultado propio con tarjeta blanca se muestra en ResultHero
    When Ana navega a /atleta/resultados
    Then ve el ResultHero de DNF con border verde y chip "BLANCA"
    And ve RP=70m, AP=68m, diferencia="+2m", Puntos=100.00
    And ve el chip "EN PODIO"

  Scenario: disciplina pendiente muestra estado de espera
    When Ana navega a /atleta/resultados
    Then ve la card de STA con chip "PENDIENTE"
    And ve "Resultado disponible al cierre de la disciplina"
    And no ve RP ni Puntos

  Scenario: DNS muestra tarjeta gris sin RP
    Given Ana tiene DNS en STA (es_dns=true)
    When navega a resultados
    Then el ResultHero de STA muestra chip "DNS" con border gris
    And RP = "—" y Puntos = "—"

  Scenario: atleta sin inscripciones ve estado vacío
    Given el atleta no está inscripto en ningún torneo
    When navega a /atleta/resultados
    Then ve el mensaje "Aún no tenés resultados publicados."
```

---

## Impacto arquitectonico

- [x] Frontend — reemplaza placeholder en `AtletaResultadosPage.tsx`
- [x] Frontend — nuevos componentes `ResultHero` y `DisciplinaPendienteCard`

### Componentes a crear

```
frontend/src/components/atleta/
├── ResultHero.tsx              ← tarjeta de resultado propio (definida en wireframes)
└── DisciplinaPendienteCard.tsx ← disciplina sin resultado aún
```

---

## Referencias

- `docs/design/ux/wireframes-atleta.md §S-08 — result-hero, estados visuales`
- `frontend/src/api/resultados.ts` — `fetchRankingCompetencia`, tipos DTO
- `frontend/src/api/competencia.ts` — `fetchCompetenciasPorTorneo`
- `frontend/src/api/registro.ts` — `listarInscripcionesDeAtleta`, `fetchAtletaMe`
- `US-5.6.3` / `US-5.6.4` — campos `puntos` y `en_podio` en `RankingEntradaDto`

---

*Redactado: 2026-04-30 — INC-5.7*
