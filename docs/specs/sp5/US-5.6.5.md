# US-5.6.5: UI tabla de ejecución — resultados por disciplina ordenados por OT

**Estado**: `Done`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.6
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/organizador/ResultadosPage.tsx`, `frontend/src/components/organizador/`, `frontend/src/api/resultados.ts`

---

## Descripcion

Como **organizador**,
quiero **ver una tabla de resultados de cada disciplina ordenada por orden de ejecución (OT), con género, categoría, AP, RP, tarjeta y puntos FAAS**,
para **monitorear los resultados en tiempo real al cierre de cada disciplina y verificar que el cálculo de puntos sea correcto antes de publicar**.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md §S-04 Resultados`
- `docs/design/ux/decisiones-frontend.md §D-02` — ruta `/organizador/resultados` → `ResultadosPage`
- `docs/plans/sp5/PLAN-SP5.md §Presentación de Resultados — Vista 1`
- `docs/design/ux/prototipos/prototipo-organizador.html`

---

## Contexto de diseño

La pantalla S-04 "Resultados" ya existe en la navbar del organizador (`[🏆 Resultados]`). Esta US implementa la página `ResultadosPage` que se activa en esa ruta. La pantalla sigue el mismo patrón visual del panel:

- Tema dark, navbar sticky superior, desktop-first
- Tokens de color del sistema: `--bg`, `--surface`, `--accent`, `--blanca`, `--roja`, `--dns`
- React + TanStack Query para fetching; sin estado global adicional

---

## Alcance funcional

### A. Selector de disciplina

La página muestra un selector (tabs o dropdown) con todas las disciplinas del torneo. Al seleccionar una disciplina, carga los resultados de esa competencia.

### B. Tabla de ejecución (ordenada por OT)

La tabla muestra **todos los atletas de la disciplina, ordenados por OT ascendente** (orden de ejecución).

**Columnas:**

| Columna | Fuente | Descripción |
|---------|--------|-------------|
| `#` OT | grilla | Posición en grilla (orden de ejecución) |
| Nombre | registro + identidad | Apellido, Nombre |
| Género | registro (derivado de Categoria) | M / F — derivado de `Categoria.value.split("_")[1]` |
| Categoría | registro | SENIOR / MASTER / JUNIOR |
| Club | registro | Nombre del club |
| AP | grilla/competencia | Announced Performance |
| OT | grilla | Hora del OT |
| Línea | grilla | Andarivel A / B |
| RP | ranking | Resultado realizado |
| Tarjeta | ranking | Chip: BLANCA / ROJA / DNS |
| Puntos | ranking | Puntos FAAS — `--accent` bold; "—" si no calculado aún |

### C. Estado visual de tarjeta

Reusar los chips definidos en `wireframes-organizador.md`:

| Tarjeta | Chip | Color |
|---------|------|-------|
| Blanca | `chip-blanca` | `--blanca` (#22c55e) |
| Roja | `chip-roja` | `--roja` (#ef4444) |
| DNS | `chip-dns` | `--dns` (#64748b) |
| Sin resultado aún | "PENDIENTE" | muted |

### D. Datos disponibles antes del cierre

La tabla debe mostrarse con datos parciales mientras la disciplina está en ejecución. Las filas de atletas que aún no ejecutaron muestran `RP = "—"`, `Tarjeta = PENDIENTE`, `Puntos = "—"`.

---

## Invariantes

- **INV-5.6.5-01**: el orden de filas es por OT ascendente, no por posición de ranking.
- **INV-5.6.5-02**: solo usuarios con rol ORGANIZADOR pueden acceder a esta pantalla.
- **INV-5.6.5-03**: la columna Género se deriva de `Categoria` — no se consulta un campo independiente.
- **INV-5.6.5-04**: la columna Puntos muestra "—" si la disciplina no está FINALIZADA o el ranking aún no fue calculado.
- **INV-5.6.5-05**: la pantalla respeta la navegación desktop del organizador con navbar superior persistente.

---

## Especificacion del comportamiento

### Flujo de datos

```text
ResultadosPage
  → GET /competencia/{torneo_id}/competencias   (lista disciplinas del torneo)
  → selector: usuario elige disciplina D
  → GET /competencia/{competencia_id}/grilla    (OT, línea, AP, nombre)
  → GET /resultados/{competencia_id}/ranking    (RP, tarjeta, puntos por atleta)
  → combinar en el frontend por atleta_id
  → mostrar tabla ordenada por OT
```

El join se realiza en el frontend por `atleta_id`. Si el ranking no existe aún (disciplina sin finalizar), las columnas RP/Tarjeta/Puntos muestran "—".

### Actualización en tiempo real

La tabla se refresca automáticamente cuando el organizador está en la pantalla S-04 (polling con TanStack Query, intervalo razonable durante ejecución activa, o invalidación manual).

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.6.5 — UI tabla de ejecución de resultados

  Background:
    Given el organizador está autenticado
    And existe el torneo "BA Open 2026" con disciplina DNF

  Scenario: tabla muestra atletas en orden OT con datos completos (disciplina finalizada)
    Given la disciplina DNF está FINALIZADA con ranking calculado
    And Ana tiene OT=14:00, RP=70m, Blanca, 100.00 puntos
    And Luis tiene OT=14:09, RP=56m, Blanca, 80.00 puntos
    When el organizador abre Resultados → selecciona DNF
    Then ve la tabla con Ana en primera fila y Luis en segunda
    And Ana muestra: Género=F, Categoría=SENIOR, RP=70m, chip BLANCA, Puntos=100.00
    And Luis muestra: Género=M, Categoría=SENIOR, RP=56m, chip BLANCA, Puntos=80.00

  Scenario: tabla parcial durante ejecucion
    Given la disciplina DNF esta EN EJECUCION (no FINALIZADA)
    And Ana completó su performance, Pedro no ejecutó aún
    When el organizador abre la vista
    Then Ana muestra RP y tarjeta con "—" en Puntos
    And Pedro muestra "—" en RP, Tarjeta y Puntos

  Scenario: selector de disciplina cambia los datos mostrados
    Given el torneo tiene DNF y STA como disciplinas
    When el organizador selecciona STA
    Then la tabla muestra los resultados de STA con tiempos en RP

  Scenario: acceso con rol incorrecto es bloqueado
    Given un usuario autenticado con rol JUEZ o ATLETA
    When intenta acceder a /organizador/resultados
    Then el sistema redirige a la pantalla de su rol correspondiente
```

---

## Impacto arquitectonico

- [x] Frontend — nueva página `ResultadosPage.tsx` en `frontend/src/pages/organizador/`
- [x] Frontend — componentes `TablaDisciplinaResultados` y `FilaResultado` en `frontend/src/components/organizador/`
- [x] API client — `frontend/src/api/resultados.ts` extendido con tipo actualizado (incluye `puntos`)

### Componentes a crear

```
frontend/src/pages/organizador/
└── ResultadosPage.tsx               ← página principal S-04

frontend/src/components/organizador/
├── TablaDisciplinaResultados.tsx    ← tabla ordenada por OT
└── FilaResultado.tsx                ← fila con todos los campos + chips
```

### Ruta (ya definida en D-02)

```
/organizador/resultados  →  ResultadosPage
```

---

## Referencias

- `docs/design/ux/wireframes-organizador.md §S-04 Resultados`
- `docs/design/ux/decisiones-frontend.md §D-02, §D-04, §D-05`
- `US-5.6.3` — `EntradaRanking.puntos` disponible en `GET /{competencia_id}/ranking`
- `src/resultados/api/router.py` — endpoints existentes de resultados

---

*Redactado: 2026-04-26 — INC-5.6*
