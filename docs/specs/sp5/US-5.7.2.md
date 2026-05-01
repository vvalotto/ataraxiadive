# US-5.7.2: Mi Grilla — posición, OT y orden de salida por disciplina

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.7
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/atleta/AtletaMiGrillaPage.tsx` (nueva), `frontend/src/App.tsx`

---

## Descripcion

Como **atleta**,
quiero **ver mi OT, andarivel, AP declarado y el orden completo de salida de la disciplina**,
para **saber exactamente cuándo me toca competir y poder organizar mi preparación**.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-atleta.md §S-07 Mi Grilla`
- `docs/design/ux/flujos-por-rol.md §3 Rol: Atleta`

---

## Contexto de diseño

La pantalla S-07 "Mi Grilla" está definida en los wireframes y referenciada desde:
- `AtletaHomePage` (card "Tu próximo OT" → "Ver grilla completa →")
- `AtletaMisInscripcionesPage` (botón "Ver grilla" en cada fila de disciplina)

No existe aún una página React para esta ruta. El cliente API `fetchGrillaCompetencia` ya existe en `frontend/src/api/competencia.ts` y devuelve `GrillaAtletaDto[]`.

La ruta será: `/atleta/grilla/:competenciaId?disciplina=<DISCIPLINA>`

---

## Alcance funcional

### A. OT Hero (hero card del atleta)

Card superior destacada con la información del atleta actual:

- label "Tu Tiempo Oficial"
- hora OT en tipografía grande (≥ 36 px, accent)
- andarivel + posición en grilla
- AP declarado (o "Sin AP declarado" si no existe)
- nombre del torneo y disciplina

### B. Lista de grilla completa

Lista de todas las entradas de la grilla, ordenadas por `posicion` ascendente (orden de salida):

| Campo | Fuente |
|-------|--------|
| Posición | `GrillaAtletaDto.posicion` |
| Nombre atleta | `GrillaAtletaDto.nombre_atleta` |
| OT programado | `GrillaAtletaDto.ot_programado` |
| Andarivel | `GrillaAtletaDto.andarivel` |
| Chip `TÚ` | cuando `atleta_id === atletaIdActual` |

**Estados visuales:**
- fila propia: fondo accent tenue + borde izquierdo accent + chip `TÚ`
- fila normal: estilo base

### C. Botón de navegación a resultados

Al pie de la página: `Ver mis resultados →` → `/atleta/resultados?competenciaId=<ID>&disciplina=<DISC>`

---

## Invariantes

- **INV-5.7.2-01:** La lista se ordena por `posicion` ascendente — no por OT, ya que OT es el campo publicado externamente.
- **INV-5.7.2-02:** La fila del atleta actual siempre se identifica visualmente con chip `TÚ` independientemente de su posición.
- **INV-5.7.2-03:** Si la grilla no está confirmada (`grilla_confirmada = false`), la página muestra un aviso "Grilla provisional — puede cambiar antes del inicio".
- **INV-5.7.2-04:** Si no hay grilla disponible (competencia sin generar), la página muestra estado vacío "La grilla aún no está disponible para esta disciplina."

---

## Especificacion del comportamiento

### Flujo de datos

```text
AtletaMiGrillaPage
  → params: competenciaId (ruta), disciplina (query param)
  → GET /competencia/{competenciaId}/grilla?disciplina={disciplina}
      → GrillaAtletaDto[]
  → atletaId = useAuthStore().userId
  → miEntrada = grilla.find(entry => entry.atleta_id === atletaId)
  → mostrar OtHero con miEntrada
  → mostrar lista completa ordenada por posicion
```

### Rutas a registrar en App.tsx

```
/atleta/grilla/:competenciaId   →   AtletaMiGrillaPage
```

La disciplina se pasa como query param: `?disciplina=DNF`.

### Navegación de entrada

Los links existentes que apuntan a esta pantalla deberán usar:
- `AtletaHomePage` — card próximo OT: `Ver grilla completa →` → `/atleta/grilla/:competenciaId?disciplina=...`
- `AtletaMisInscripcionesPage` — botón "Ver grilla": misma URL

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.7.2 — Mi Grilla del atleta por disciplina

  Background:
    Given el atleta "ana@email.com" (atleta_id="aaa") está autenticado
    And existe la competencia DNF con grilla confirmada
    And la grilla tiene: Ana pos=3 OT=14:27 Andarivel=1, Luis pos=1 OT=14:09, Pedro pos=2 OT=14:18

  Scenario: atleta ve su OT hero destacado
    When Ana navega a /atleta/grilla/{competenciaId}?disciplina=DNF
    Then ve el hero card con "14:27" en tipografía grande
    And ve "Andarivel 1 · Posición 3"
    And ve su AP declarado

  Scenario: lista completa ordenada por posicion con fila propia resaltada
    When Ana navega a Mi Grilla de DNF
    Then la lista muestra: Luis (pos 1), Pedro (pos 2), Ana (pos 3)
    And la fila de Ana tiene el chip "TÚ" y fondo accent tenue

  Scenario: grilla provisional muestra aviso
    Given la grilla no está confirmada
    When Ana navega a Mi Grilla de DNF
    Then ve el aviso "Grilla provisional — puede cambiar antes del inicio"

  Scenario: grilla no disponible muestra estado vacío
    Given la competencia aún no tiene grilla generada
    When Ana navega a Mi Grilla de DNF
    Then ve el mensaje "La grilla aún no está disponible para esta disciplina."

  Scenario: navegación a resultados desde la grilla
    When Ana presiona "Ver mis resultados →"
    Then navega a /atleta/resultados con competenciaId y disciplina en params
```

---

## Impacto arquitectonico

- [x] Frontend — nueva página `AtletaMiGrillaPage.tsx`
- [x] Frontend — nueva ruta en `App.tsx`
- [ ] Sin cambios de backend — `GET /competencia/{id}/grilla` ya existe

### Componentes a crear

```
frontend/src/pages/atleta/
└── AtletaMiGrillaPage.tsx      ← S-07: OtHero + lista grilla

frontend/src/components/atleta/
├── OtHero.tsx                  ← card hero con OT del atleta (definida en wireframes)
└── GrillaRow.tsx               ← fila de grilla con chip TÚ (definida en wireframes)
```

### Actualización de links existentes

- `AtletaHomePage.tsx`: link "Ver grilla completa →" debe apuntar a `/atleta/grilla/:competenciaId?disciplina=...`
- `AtletaMisInscripcionesPage.tsx`: botón "Ver grilla" debe apuntar a la misma ruta

---

## Referencias

- `docs/design/ux/wireframes-atleta.md §S-07`
- `frontend/src/api/competencia.ts` — `fetchGrillaCompetencia`, `GrillaAtletaDto`
- `frontend/src/pages/atleta/portalData.ts` — patrón de uso de `fetchGrillaCompetencia`
- `frontend/src/pages/atleta/AtletaHomePage.tsx` — link de entrada a actualizar

---

*Redactado: 2026-04-30 — INC-5.7*
