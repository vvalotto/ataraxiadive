# US-5.5.1: Registro de APs

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.5
**Bounded Context**: `competencia` (endpoint) + `frontend`
**Capas afectadas**: `competencia/api/router.py`, `frontend/src/api/competencia.ts`, `frontend/src/pages/atleta/AtletaDashboardPage.tsx`

---

## Descripcion

Como **atleta inscripto en un torneo**,
quiero **registrar mi Announced Performance (AP) por cada disciplina que declaré**
para **aparecer en la grilla de salida con mi marca declarada**.

---

## Contexto del dominio

El ciclo de vida del aggregate Performance en BC Competencia arranca con `registrar_ap`:

```
(nuevo) → AnunciadaAP → Llamada → ResultadoRegistrado / DNS → Ejecutada / Revision / DQ
```

El `RegistrarAPHandler` ya existe en `competencia/application/commands/registrar_ap.py` con todas las validaciones de dominio. Esta US lo expone mediante un endpoint REST y construye la UI de registro desde el portal del atleta.

### Modelo involucrado

| Elemento | Nombre | Descripcion |
|---|---|---|
| Command existente | `RegistrarAPCommand` | `competencia_id`, `participante_id`, `disciplina`, `valor_ap`, `unidad` |
| Handler existente | `RegistrarAPHandler` | Valida INV-P-01..04, crea Performance, emite `APRegistrado` en event store |
| Endpoint nuevo | `POST /competencia/{id}/registrar-ap` | AtletaDep; `participante_id` extraído del JWT `sub` |
| Función frontend nueva | `registrarAP(params)` | En `api/competencia.ts` |
| UI nueva | Sección "Mis APs" | En `AtletaDashboardPage`, por disciplina inscripta |

### Lenguaje ubicuo relevante

- **AP (Announced Performance):** marca declarada por el atleta antes de la competencia; es el dato de entrada para generar la grilla de salida.
- **participante_id:** en BC Competencia el atleta es identificado por el UUID del JWT `sub`, que por convención coincide con su `atleta_id` en BC Registro.
- **AnunciadaAP:** estado del aggregate Performance tras registrar el AP — el atleta está listo para ser ubicado en la grilla.

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.5.1-01:** El valor del AP debe ser mayor que cero (INV-P-01); rechaza con 422.
- **INV-5.5.1-02:** Un atleta solo puede registrar AP una vez por (competencia, disciplina); un segundo intento rechaza con 409 (INV-P-02).
- **INV-5.5.1-03:** No se puede registrar AP si la grilla de esa competencia ya fue confirmada (INV-P-04); rechaza con 409.
- **INV-5.5.1-04:** La unidad debe ser compatible con la disciplina: `Metros` para DNF/DYN/DBF; `Segundos` para STA y SPE_*; rechaza con 422.
- **INV-5.5.1-05:** El `participante_id` se extrae del JWT `sub` — el atleta no puede registrar AP a nombre de otro.

### Operacion principal — registrar AP

**Endpoint nuevo:**

```
POST /competencia/{competencia_id}/registrar-ap
Auth: AtletaDep
Body: { disciplina, valor_ap, unidad }
participante_id: user["sub"] del JWT (no en body)

201 Created      → { performance_id: UUID }
409 Conflict     → { detail: "INV-P-02: ya existe un AP para..." }
409 Conflict     → { detail: "INV-P-04: grilla confirmada para..." }
409 Conflict     → { detail: "INV-P-03: plazo de AP vencido..." }
422 Unprocessable → { detail: "Unidad incompatible..." | "Valor AP inválido..." }
```

**Flujo en frontend:**

```
SECCIÓN "Mis APs" en AtletaDashboardPage:
1. Para cada torneo donde el atleta está inscripto:
   a. GET /competencia?torneo_id={torneoId}  →  competencias por disciplina
   b. GET /competencia/{comp_id}/grilla       →  AP actual por atleta_id
2. Por cada disciplina inscripta, mostrar:
   - AP registrado: badge "AP registrado: X m" / "AP registrado: X s"
   - Sin AP: formulario con campo numérico + selector de unidad + botón "Registrar AP"
3. Al confirmar:
   POST /competencia/{competencia_id}/registrar-ap { disciplina, valor_ap, unidad }
   201 → refrescar vista; disciplina muestra "AP registrado"
   409 → error inline
   422 → error inline con mensaje de backend
```

**Ejemplo concreto:**

```
Atleta "ana@email.com" (JWT sub="uuid-ana") inscripta en "BA Open 2026":
  Disciplinas: [DNF, STA]
  Competencia DNF → competencia_id="uuid-comp-dnf"
  Competencia STA → competencia_id="uuid-comp-sta"

Ana navega a /atleta/dashboard
Ve sección "Mis APs":
  DNF: Sin AP  (formulario visible)
  STA: Sin AP  (formulario visible)

Registra DNF:
  Valor=70, Unidad=Metros
  POST /competencia/uuid-comp-dnf/registrar-ap { disciplina:"DNF", valor_ap:70, unidad:"Metros" }
  201 → DNF muestra "AP registrado: 70 m"

Registra STA:
  Valor=300, Unidad=Segundos
  POST /competencia/uuid-comp-sta/registrar-ap { disciplina:"STA", valor_ap:300, unidad:"Segundos" }
  201 → STA muestra "AP registrado: 300 s"

Intento duplicado:
  POST /competencia/uuid-comp-dnf/registrar-ap → 409 "AP ya registrado"
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.5.1 — Registro de APs del atleta

  Background:
    Given existe el torneo "BA Open 2026" con disciplinas [DNF, STA]
    And existen competencias creadas para DNF y STA
    And la atleta "ana@email.com" esta inscripta en [DNF, STA]
    And la grilla de DNF y STA no está confirmada

  Scenario: atleta registra AP exitosamente
    Given "ana@email.com" esta autenticada con rol ATLETA
    When POST /competencia/{comp_dnf}/registrar-ap con disciplina=DNF, valor_ap=70, unidad=Metros
    Then el sistema responde 201
    And existe un aggregate Performance en estado AnunciadaAP para (ana, DNF)
    And la UI muestra "AP registrado: 70 m" para DNF

  Scenario: segundo AP para la misma disciplina es rechazado
    Given "ana@email.com" ya registró AP=70 para DNF
    When POST /competencia/{comp_dnf}/registrar-ap con disciplina=DNF, valor_ap=65, unidad=Metros
    Then el sistema responde 409
    And el mensaje contiene "ya existe un AP"

  Scenario: valor AP cero es rechazado
    Given "ana@email.com" esta autenticada con rol ATLETA
    When POST /competencia/{comp_dnf}/registrar-ap con disciplina=DNF, valor_ap=0, unidad=Metros
    Then el sistema responde 422

  Scenario: unidad incompatible con disciplina es rechazada
    Given "ana@email.com" esta autenticada con rol ATLETA
    When POST /competencia/{comp_dnf}/registrar-ap con disciplina=DNF, valor_ap=70, unidad=Segundos
    Then el sistema responde 422

  Scenario: AP bloqueado si grilla ya fue confirmada
    Given la grilla de DNF esta confirmada
    When POST /competencia/{comp_dnf}/registrar-ap con disciplina=DNF, valor_ap=70, unidad=Metros
    Then el sistema responde 409

  Scenario: UI muestra disciplinas con y sin AP
    Given "ana@email.com" registró AP=70 para DNF pero no para STA
    When "ana@email.com" accede a /atleta/dashboard
    Then ve "AP registrado: 70 m" para DNF
    And ve formulario de ingreso de AP para STA
```

---

## Impacto arquitectonico

- [x] No — extiende el router con un endpoint que usa el handler ya implementado.

**Capas afectadas:**

- `competencia/api/router.py` — endpoint `POST /{competencia_id}/registrar-ap` (AtletaDep; `participante_id` = `user["sub"]`)
- `frontend/src/api/competencia.ts` — función `registrarAP({ competenciaId, disciplina, valorAp, unidad })`; retorna `{ performance_id: string }`
- `frontend/src/pages/atleta/AtletaDashboardPage.tsx` — sección "Mis APs" debajo de cada torneo inscripto

**Dependencias del handler en el router:**

`RegistrarAPHandler` necesita `EventStorePort`, `CompetenciaEstadoPort` y `DisciplinaDescriptorPort`. Los tres ya están disponibles como `Depends(...)` en el router.

**Nota de seguridad:** el `participante_id` del command se obtiene de `user["sub"]` (el UUID del usuario autenticado), no del body de la request. Esto previene que un atleta registre AP a nombre de otro.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.5`
- Command/Handler: `src/competencia/application/commands/registrar_ap.py`
- Router competencia: `src/competencia/api/router.py`
- API frontend: `frontend/src/api/competencia.ts`
- Dashboard atleta: `frontend/src/pages/atleta/AtletaDashboardPage.tsx`
- Dependencias del router: buscar `EventStoreDep`, `CompetenciaEstadoDep`, `DisciplinaDescriptorDep`

---

*Redactado: 2026-04-24 — INC-5.5 Inscripcion completa*
