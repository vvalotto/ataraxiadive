# US-4.3.1: Pantalla de selección de competencia — mis disciplinas asignadas

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.3
**Bounded Context**: `frontend` (consume `torneo` + `competencia`, sin cambios en backend)
**Capas afectadas**: `frontend/src/pages/juez/`, `frontend/src/api/`, `frontend/src/stores/`

---

## Descripción

Como **juez**,
quiero **ver en mi celular la lista de disciplinas que me fueron asignadas en el torneo activo**
para **saber en cuál debo juzgar y acceder directamente a su grilla de salida**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Página | `MisDisciplinas` | Pantalla S-01 — lista de disciplinas del juez |
| Componente | `DisciplinaCard` | Card con nombre, estado (ACTIVA/PENDIENTE), tap navega a grilla |
| Store | `useCompetenciaStore` | Disciplina activa seleccionada, competencia_id activo |
| API client | `api/torneo.ts` | `GET /torneo` → torneo en ejecución |
| API client | `api/torneo.ts` | `GET /torneo/{torneo_id}/jueces/{juez_id}/disciplinas` |
| API client | `api/competencia.ts` | `GET /competencia?disciplina=X` → competencia_id de cada disciplina |

### Lenguaje ubicuo relevante

- **Disciplina asignada:** disciplina del torneo para la que el juez fue designado como responsable.
- **ACTIVA:** la competencia de esa disciplina está en estado `EnEjecucion` — el juez puede operar.
- **PENDIENTE:** la competencia no ha sido iniciada aún — acceso deshabilitado.
- **Torneo activo:** torneo en estado `EnEjecucion` — el único que le interesa al juez.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.3.1-01:** El juez solo ve las disciplinas que le fueron asignadas explícitamente (`PUT /torneo/{id}/disciplinas/{disc}/juez`). No ve disciplinas sin asignar ni de otros jueces.
- **INV-4.3.1-02:** Solo el torneo en estado `EnEjecucion` es relevante. Si no hay torneo activo, la pantalla muestra un mensaje de espera.
- **INV-4.3.1-03:** Una `DisciplinaCard` con estado PENDIENTE es visible pero no tappable — el juez no puede acceder a la grilla hasta que la competencia sea iniciada.
- **INV-4.3.1-04:** El badge de conexión (online/offline) es visible en todo momento.

### Operación principal

**Nombre**: `cargarMisDisciplinas(juezId, torneoId)`

| | Descripción |
|---|---|
| **Precondición** | Juez autenticado con JWT válido. Existe al menos un torneo en estado `EnEjecucion`. |
| **Postcondición** | Se muestran las `DisciplinaCard` de las disciplinas asignadas al juez, con su estado (ACTIVA/PENDIENTE). |
| **Excepciones** | Sin torneo activo → mensaje "No hay torneo en curso". Sin disciplinas asignadas → mensaje "Sin disciplinas asignadas". |

**Ejemplo concreto:**

```
Precondición:  juez "juez@ataraxia.com" asignado a DNF y CWTB en torneo "BA 2025"
Operación:     GET /torneo → torneo_id = T1 (EnEjecucion)
               GET /torneo/T1/jueces/{juez_id}/disciplinas → ["DNF", "CWTB"]
               GET /competencia?disciplina=DNF → { competencia_id: C1, estado: EnEjecucion }
               GET /competencia?disciplina=CWTB → { competencia_id: C2, estado: Configurada }
Postcondición: DisciplinaCard DNF → ACTIVA (tappable → /juez/grilla)
               DisciplinaCard CWTB → PENDIENTE (no tappable)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.3.1 — Mis Disciplinas asignadas al juez

  Background:
    Given el juez "juez@ataraxia.com" está autenticado con rol juez
    And existe el torneo "BA 2025" en estado EnEjecucion

  Scenario: juez ve sus disciplinas asignadas con estado correcto
    Given el juez tiene asignadas las disciplinas DNF y CWTB
    And la competencia de DNF está en estado EnEjecucion
    And la competencia de CWTB está en estado Configurada
    When accede a /juez/disciplinas
    Then ve dos DisciplinaCard: DNF (ACTIVA) y CWTB (PENDIENTE)
    And solo la card DNF es tappable

  Scenario: tap en disciplina ACTIVA navega a la grilla
    Given el juez tiene asignada la disciplina DNF en estado ACTIVA
    When toca la card de DNF
    Then navega a /juez/grilla con la competencia de DNF seleccionada
    And useCompetenciaStore.disciplinaActiva = "DNF"

  Scenario: sin torneo activo muestra mensaje de espera
    Given no existe ningún torneo en estado EnEjecucion
    When accede a /juez/disciplinas
    Then ve el mensaje "No hay torneo en curso"

  Scenario: sin disciplinas asignadas muestra mensaje informativo
    Given el juez no tiene disciplinas asignadas en el torneo activo
    When accede a /juez/disciplinas
    Then ve el mensaje "Sin disciplinas asignadas"
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes sin modificar el backend.

**Capa(s) afectadas:**
- [x] Frontend — nueva página `MisDisciplinas`, componente `DisciplinaCard`, `api/torneo.ts`
- [x] Frontend — `useCompetenciaStore` (nuevo store Zustand con disciplina activa + competencia_id)

---

## Referencias

- Wireframes: `docs/design/ux/wireframes-juez.md §S-01`
- Stack frontend: `docs/design/ux/decisiones-frontend.md §D-02 (routing), §D-03 (Zustand)`
- API backend: `GET /torneo/{torneo_id}/jueces/{juez_id}/disciplinas` (implementado en SP3, US-3.4.1)
- Plan SP4: `docs/plans/sp4/PLAN-SP4.md §INC-4.3`

---

## Notas de implementación

- **Tema:** dark mode según tokens de wireframes-juez.md. Usar clases Tailwind: `bg-slate-950` (--bg), `bg-slate-800` (--surface), `text-sky-400` (--accent). Aplicar en `JuezLayout` — las páginas del juez heredan este tema.
- **Flujo de datos:** (1) leer `juez_id` del `useAuthStore`; (2) fetch `GET /torneo` → filtrar por `estado=EnEjecucion` → obtener `torneo_id`; (3) fetch `GET /torneo/{torneo_id}/jueces/{juez_id}/disciplinas` → lista de disciplinas; (4) para cada disciplina, fetch `GET /competencia?disciplina=X` → obtener estado.
- **`useCompetenciaStore`:** guardar `{ disciplinaActiva, competenciaId, torneoId }` al seleccionar una disciplina.
- **Rutas a agregar en `App.tsx`:** `/juez/disciplinas` → `MisDisciplinas`, `/juez/grilla` → `GrillaJuez` (stub en esta US).
- **Encabezado S-01:** nombre del juez (del JWT `email`) + nombre del torneo.
- **`ConnectionBadge`:** reutiliza `useConnectionStore` de INC-4.2 (US-4.2.1).

---

*Redactado: 2026-04-11 — INC-4.3 Interfaz del Juez*
