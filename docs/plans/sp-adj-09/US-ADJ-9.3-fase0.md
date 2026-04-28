# US-ADJ-9.3 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Sprint:** `SP-ADJ-09`
**Spec canonica:** `docs/specs/sp-adj-09/US-ADJ-9.3.md`

---

## Historia

**US:** US-ADJ-9.3 - Home del organizador

Como **organizador**, quiero una pagina inicial que liste los torneos bajo mi
responsabilidad, priorizando los torneos vigentes y permitiendo acceder al historico
para entrar rapidamente al torneo que estoy operando y consultar anteriores cuando haga falta.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp-adj-09/US-ADJ-9.3.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/decisiones-frontend.md`
- `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`
- `frontend/src/pages/organizador/DashboardPage.tsx`
- `frontend/src/App.tsx`

---

## Contexto Relevante

### Estado actual de la home del organizador

- La ruta principal del organizador ya aterriza en `/organizador/torneo`.
- `DashboardPage.tsx` hoy funciona como listado de torneos, no como dashboard operativo.
- El título ya fue movido a `Torneos`, pero el comportamiento todavía usa filtros heredados:
  - `todos`
  - `abiertos`
  - `cerrados`
  - `cancelados`

### Gap funcional respecto de la spec

- La spec define dos agrupaciones de negocio:
  - `vigentes`
  - `historico`
- La vista actual mezcla ambos conceptos con filtros más técnicos y menos intencionales.
- También sigue incluyendo `CREADO` dentro del universo "abierto", cuando la spec de `9.3`
  formaliza vigencia a partir de:
  - `INSCRIPCION_ABIERTA`
  - `PREPARACION`
  - `EJECUCION`
  - `PREMIACION`

### Separacion conceptual confirmada

- Esta pantalla ya no debe llamarse ni comportarse como dashboard operativo.
- El dashboard operativo con KPIs y disciplina activa queda diferido explícitamente a `US-ADJ-9.4`.

---

## Gaps Detectados

1. La home no usa todavía la clasificación formal `vigentes` vs `historico`.
2. El filtro por defecto sigue expresado como `abiertos`, no como torneos vigentes.
3. La clasificación actual puede incluir estados fuera de la definición formal de vigencia.
4. Falta explicitar mejor en copy/UI que esta pantalla es un acceso a torneos y no un panel operativo.

---

## Riesgos Detectados

- Cambiar la clasificación puede alterar qué torneos aparecen por defecto.
- Si se mezcla esta US con `9.4`, vuelve a confundirse home con dashboard operativo.
- Un cambio de copy/títulos debe ser consistente con las rutas ya estabilizadas en `9.2`.

---

## Quality Gates Esperables

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- validacion UI/manual del filtro `vigentes` / `historico`

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. Espera de aprobacion explicita antes de Fase 3
