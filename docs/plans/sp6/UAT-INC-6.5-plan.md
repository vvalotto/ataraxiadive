# Plan de UAT — INC-6.5 Validación E2E
## Apnea Indoor Buenos Aires 2025

> Estado: ✅ Completado — F-01..F-10 PASS · 0 bloqueantes  
> Última actualización: 2026-05-14  
> Precondición: INC-6.1 ✅ · INC-6.2 ✅ · INC-6.3 ✅ · INC-6.4 ✅ · INC-6.6 ✅

---

## 1. Estrategia

El UAT valida el **ciclo de vida completo del torneo**, no los flujos por rol en forma aislada.
Los roles participan en cada fase donde corresponde naturalmente — igual que en una competencia real.

**Principios:**
- El portal público es visible en todo momento, desde antes de crear el torneo.
- El registro de usuarios es parte del flujo de prueba, no un prerrequisito silencioso.
- Los datos se cargan en dos etapas: usuarios antes del torneo, inscripciones y APs después de crearlo.
- Cada acción significativa se verifica desde los demás roles (verificación cruzada).
- Los flujos de excepción (DNS, BKO, tarjeta amarilla) se ejecutan dentro de la fase de ejecución.
- Las transiciones de estado del torneo se verifican en portal, organizador, juez y atleta.

---

## 2. Dataset: Buenos Aires 2025

| Dato | Valor |
|------|-------|
| Competencia | "Apnea Indoor Buenos Aires 2025" |
| Fecha | Junio 2025 |
| Disciplinas | DBF · DNF · DYN · SPE · STA |
| Categorías | JUNIOR · SENIOR · MASTER |
| Atletas | 31 participantes reales |
| Sede | Buenos Aires, Argentina |

**Credenciales predefinidas para UAT:**

| Rol | Email | Password | Alcance |
|-----|-------|----------|---------|
| Organizador | `organizador@ba2025.uat` | `Ba2025uat!` | — |
| Juez 1 | `juez1@ba2025.uat` | `Ba2025uat!` | DBF/DNF/DYN/SPE andarivel 1 · STA andarivel 1 |
| Juez 2 | `juez2@ba2025.uat` | `Ba2025uat!` | DBF/DNF/DYN/SPE andarivel 2 · STA andarivel 2 |
| Juez 3 | `juez3@ba2025.uat` | `Ba2025uat!` | STA andarivel 3 (solo STA) |
| Atleta (Víctor Valotto) | `victor.valotto@ba2025.uat` | `Ba2025uat!` | — |
| Atleta (Guadalupe Fardi) | `guadalupe.fardi@ba2025.uat` | `Ba2025uat!` | — |
| Atleta (patrón general) | `nombre.apellido@ba2025.uat` | `Ba2025uat!` | — |

**Asignación de jueces por disciplina:**

| Disciplina | Andariveles | Juez andarivel 1 | Juez andarivel 2 | Juez andarivel 3 |
|-----------|:-----------:|-----------------|-----------------|-----------------|
| DBF | 2 | Juez 1 | Juez 2 | — |
| DNF | 2 | Juez 1 | Juez 2 | — |
| DYN | 2 | Juez 1 | Juez 2 | — |
| SPE | 2 | Juez 1 | Juez 2 | — |
| STA | 3 | Juez 1 | Juez 2 | Juez 3 |

> La asignación es por performance individual en la grilla (`PUT /competencia/{id}/grilla/{perf_id}/juez`).
> El organizador asigna cada juez a las performances de su andarivel durante la preparación.

---

## 3. Criterio de Bloqueo

| Severidad | Definición | Acción |
|-----------|-----------|--------|
| 🔴 **Bloqueante** | Impide continuar con la siguiente fase · Pérdida de datos · Flujo roto | Detener UAT — registrar hallazgo — no avanzar |
| 🟡 **Observación** | Comportamiento incorrecto pero el flujo puede continuar | Registrar hallazgo — continuar UAT |
| ⚪ **Estético** | Texto, color, alineación — no afecta la función | Registrar para corrección posterior |

**Bloqueos conocidos que deben estar resueltos antes del UAT:**
- MUX-04 (canSubmitBko) — resuelto en US-6.1.1 ✅
- UI-JUE-02 (secuencia tarjeta→marca) — resuelto en US-6.1.1 ✅
- MUX-03 (grilla ordenada) — resuelto en US-6.1.3 ✅

---

## 4. Dispositivos por Rol

| Rol | Dispositivo | Justificación |
|-----|-------------|---------------|
| Organizador | Desktop / laptop | Gestión de torneo, inscriptos, resultados |
| Juez | Móvil (iPhone / Android) | Contexto real de uso en pileta |
| Atleta | Móvil o tablet | Consulta de resultados en sitio |
| Portal público | Cualquier dispositivo | Sin autenticación |

---

## 5. Estructura de Seeds

### Seed-A — Usuarios (correr antes de F-01)
Crea organizador, 3 jueces (juez1, juez2, juez3) y 31 atletas con credenciales predefinidas.
No crea torneo — los usuarios existen pero el sistema empieza "vacío" de torneo.

```bash
uv run python tests/uat/sp6/seed_ba2025_usuarios.py
```

### Seed-B — Inscripciones y APs (correr al inicio de F-04, con torneo_id de F-02)
Toma el torneo_id creado por el organizador en F-02 y carga inscripciones + APs
de los 31 atletas según `data/datasets/buenos_aires_2025/schedules.json`.

```bash
uv run python tests/uat/sp6/seed_ba2025_inscripciones.py --torneo-id <id>
```

### Seed-C — Resultados restantes (correr al inicio de F-09, opcional)
Carga los resultados de los atletas que no se ingresaron manualmente en F-07/F-08,
según `data/datasets/buenos_aires_2025/results.json`. Permite validar rankings y podios
con el dataset completo sin requerir ingreso manual de 130+ performances.

```bash
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id>
```

> **Nota:** los tres scripts de seed son parte del alcance de INC-6.5 —
> deben crearse como primera tarea antes de ejecutar el UAT.

---

## 6. Fases del UAT

---

### F-01 — Setup: Usuarios y Portal Público

**Objetivo:** verificar que el portal público funciona sin autenticación y que el registro de usuarios opera correctamente para los tres roles.

**Estado inicial:** base de datos vacía o limpia de datos BA 2025. Seed-A ejecutado.

**Dispositivos:** visitante anónimo (cualquier browser) · organizador (desktop) · juez (móvil)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F01-S01 | Visitante | Acceder a `/portalapnea` sin login | Portal carga · lista de torneos visible (puede estar vacía) · sin error | INC-6.6 | 🔴 |
| F01-S02 | Visitante | Explorar portal sin autenticación | Ningún redirect a login · ningún error 401 | INC-6.6 | 🔴 |
| F01-S03 | Organizador | Login con `organizador@ba2025.uat` | Redirige a portal organizador · header "En línea" | — | 🔴 |
| F01-S04 | Juez 1 | Login con `juez1@ba2025.uat` desde móvil | Redirige a portal juez · sección "Mis asignaciones" visible | UI-JUE-01 | 🔴 |
| F01-S04b | Juez 3 | Login con `juez3@ba2025.uat` desde móvil | Redirige a portal juez correctamente | — | 🟡 |
| F01-S05 | Atleta | Login con `victor.valotto@ba2025.uat` | Redirige a portal atleta · sin cartel "Hola" | UI-ATL-01 | 🟡 |
| F01-S06 | Visitante | Intentar acción que requiere auth (ej. inscribirse) | Redirige a login · post-login regresa al destino correcto | US-6.6.3 | 🔴 |

**Verificación cruzada:** N/A — fase de setup.

**Estado al cierre:** usuarios autenticables · portal público accesible · no existe torneo BA 2025.

---

### F-02 — Creación del Torneo

**Objetivo:** el organizador crea el torneo con todos sus datos desde la UI. Verificar que el portal refleja el nuevo torneo y que las transiciones de estado son correctas.

**Datos a generar en esta fase (a través de escenarios):** torneo "Apnea Indoor Buenos Aires 2025" con 5 disciplinas y 3 categorías.

**Dispositivo:** organizador (desktop)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F02-S01 | Organizador | Crear torneo "Apnea Indoor Buenos Aires 2025" · sede Buenos Aires · fechas de competencia | Torneo creado · `torneo_id` disponible | UI-ORG-01 | 🔴 |
| F02-S02 | Organizador | Configurar disciplinas: DBF, DNF, DYN, SPE, STA | 5 disciplinas asociadas al torneo | — | 🔴 |
| F02-S03 | Organizador | Configurar categorías: JUNIOR, SENIOR, MASTER | Categorías guardadas | UI-ORG-07 | 🔴 |
| F02-S04 | Visitante | Refrescar `/portalapnea` | Torneo aparece en la lista (o no, según política de visibilidad por estado CREADO) | INC-6.6 | 🟡 |
| F02-S05 | Organizador | Verificar lista de torneos en portal organizador | Torneo aparece ordenado por fecha | UI-ORG-01 | 🟡 |

**Registro requerido:** anotar el `torneo_id` generado → necesario para Seed-B.

**Estado al cierre de fase:** torneo en estado `CREADO`.

---

### F-03 — Volcado de Datos Post-Creación

**Objetivo:** cargar el dataset completo de Buenos Aires 2025 en el torneo creado en F-02.

**Datos precargados via Seed-B:**
- 31 atletas con sus disciplinas y APs según `schedules.json`
- Inscripciones vinculadas al `torneo_id` de F-02

```bash
uv run python tests/uat/sp6/seed_ba2025_inscripciones.py --torneo-id <torneo_id_de_F02>
```

**Verificación:**

| ID | Actor | Acción | Resultado esperado | Severidad |
|----|-------|--------|--------------------|-----------|
| F03-S01 | Organizador | Ver lista de inscriptos en DBF | 31 atletas (o los inscriptos en DBF) con categoría legible y columna "ANUNCIO" con AP | 🔴 |
| F03-S02 | Organizador | Verificar atleta Víctor Valotto en STA | AP = 03:15 (formato mm:ss en columna ANUNCIO) | 🟡 |
| F03-S03 | Atleta (Víctor Valotto) | Login y ver inscripciones propias | DBF · DNF · STA con AP declarada | 🟡 |

**Estado al cierre de fase:** torneo en estado `CREADO` con 31 atletas inscriptos y APs registradas.

---

### F-04 — Inscripción Abierta

**Objetivo:** verificar el flujo de inscripción desde el rol atleta, incluyendo la navegación desde el portal público. El seed ya cargó los 31 atletas; esta fase valida el flujo manual de inscripción para 2 atletas y verifica la visibilidad del torneo con estado `INSCRIPCION_ABIERTA`.

**Datos a generar (escenarios manuales):** 2 inscripciones adicionales o validación del flujo end-to-end.

**Dispositivos:** organizador (desktop) · atleta (móvil)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F04-S01 | Organizador | Abrir inscripciones del torneo | Estado pasa a `INSCRIPCION_ABIERTA` | — | 🔴 |
| F04-S02 | Portal (visitante) | Refrescar `/portalapnea` | Torneo muestra estado "Inscripción abierta" · botón "Inscribirse" visible | INC-6.6 | 🔴 |
| F04-S03 | Visitante | Clic en "Inscribirse" sin estar logueado | Redirige a login · post-login regresa al formulario de inscripción del torneo | US-6.6.3 | 🔴 |
| F04-S04 | Atleta (Guadalupe Fardi) | Login y completar inscripción en DYN con AP inline | AP queda registrada en el formulario · inscripción confirmada | UI-ATL-02 | 🔴 |
| F04-S05 | Organizador | Ver inscriptos · verificar columna "ANUNCIO" y categoría | Categoría: "JUNIOR" (no clave técnica) · AP: valor en metros | UI-ORG-03 | 🟡 |

**Verificación cruzada:** organizador ve inscripción de Guadalupe Fardi inmediatamente después de F04-S04.

**Estado al cierre de fase:** torneo `INSCRIPCION_ABIERTA` · 31+ atletas inscriptos.

---

### F-05 — Preparación: Grilla y Asignación de Jueces

**Objetivo:** el organizador cierra inscripciones, genera grilla y asigna el juez a cada disciplina. Verificar que la UI muestra la información correctamente (columnas, andarivel, estado de tabs).

**Dispositivo:** organizador (desktop)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F05-S01 | Organizador | Cerrar inscripciones | Estado pasa a `PREPARACION` · tabs de grilla y jueces habilitadas | — | 🔴 |
| F05-S02 | Organizador | Generar grilla para DBF | Atletas ordenados por AP desc · andarivel numérico · columna "Anuncios" | UI-ORG-04 | 🔴 |
| F05-S03 | Organizador | Generar grilla para STA | Marcas de AP en formato mm:ss | MUX-08 | 🔴 |
| F05-S04 | Organizador | Generar grilla para SPE | Marcas de AP en formato mm:ss | MUX-08 | 🟡 |
| F05-S05 | Organizador | Asignar jueces por andarivel en cada disciplina: Juez 1 → andarivel 1, Juez 2 → andarivel 2 (DBF/DNF/DYN/SPE), + Juez 3 → andarivel 3 (solo STA) | Selector sin texto nombre redundante · sin "Cobertura Operativa" | UI-ORG-06 | 🟡 |
| F05-S06 | Organizador | Verificar panel del torneo → alertas activas | Sin botón "Resolver" en alertas | UI-ORG-02 | 🟡 |
| F05-S07 | Portal (visitante) | Ver estado del torneo en `/portalapnea` | Estado actualizado (según política de visibilidad para PREPARACION) | INC-6.6 | 🟡 |
| F05-S08 | Juez 1 (móvil) | Login y ver "Mis asignaciones" | Disciplinas donde tiene performances asignadas · datos del torneo primero | UI-JUE-01 | 🟡 |
| F05-S09 | Juez 3 (móvil) | Login y ver "Mis asignaciones" | Solo STA en sus asignaciones (no aparecen DBF/DNF/DYN/SPE) | UI-JUE-01 | 🟡 |

**Estado al cierre de fase:** torneo `PREPARACION` · grilla generada para las 5 disciplinas · juez asignado.

---

### F-06 — Inicio de Ejecución

**Objetivo:** transición al estado `EJECUCION`. Verificar que el portal público muestra el torneo como "En ejecución" y que la página pública del torneo está disponible con la grilla.

**Dispositivos:** organizador (desktop) · visitante (cualquier dispositivo)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F06-S01 | Organizador | Iniciar ejecución del torneo | Estado pasa a `EJECUCION` | — | 🔴 |
| F06-S02 | Portal (visitante) | Refrescar `/portalapnea` | Torneo muestra "En ejecución" · botón/link "Ver en vivo" o equivalente | INC-6.6 | 🔴 |
| F06-S03 | Portal (visitante) | Acceder a página pública del torneo | Grilla con tabs por disciplina · podios (vacíos al inicio) | US-6.6.4 | 🔴 |
| F06-S04 | Juez (móvil) | Ver grilla de DBF | Primer atleta de la grilla aparece primero (mayor prioridad de estado) | MUX-03 | 🔴 |
| F06-S05 | Atleta | Login y ver inicio | Disciplinas en curso ordenadas (próxima → posteriores → realizadas) | UI-ATL-01 | 🟡 |

**Estado al cierre de fase:** torneo `EJECUCION` · portal público activo · grilla visible públicamente.

---

### F-07 — Ejecución: Flujo Normal de Performances

**Objetivo:** el juez registra performances reales del dataset BA 2025. Verificar el flujo completo de ingreso, los formatos de marca, y la propagación en tiempo real a organizador, atleta y portal público.

**Datos a generar (escenarios manuales):** performances seleccionadas — representativas de todos los tipos de resultado y disciplina.

**Dispositivo:** juez (móvil) · organizador (desktop) para verificación cruzada · portal (cualquier dispositivo)

**Atletas del escenario manual y juez responsable:**

| Atleta | Disciplina | Andarivel | Juez | AP | RP real | Tarjeta | Verifica |
|--------|-----------|:---------:|------|-----|---------|---------|----------|
| Ezequiel Cuchiarelli | DBF | 1 | Juez 1 | 50m | DNS | — | flujo DNS |
| Víctor Valotto | DBF | 2 | Juez 2 | (schedules) | 52.40m | Blanca (RP < AP, válido) | flujo normal |
| Guadalupe Fardi | DNF | 1 | Juez 1 | (schedules) | 41.05m | Blanca | JUNIOR FEM |
| Alejandro Alperin | SPE | 2 | Juez 2 | (schedules) | 00:59.00 | Blanca (mm:ss) | MUX-08 SPE |
| Víctor Valotto | STA | 2 | Juez 2 | 03:15 | 04:32.98 | Blanca (mm:ss) | MUX-08 |
| José Enjuto | STA | 3 | Juez 3 | (schedules) | 06:33.05 | Blanca (RP > AP) | flujo normal |

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F07-S01 | Juez 1 (móvil) | Abrir grilla DBF · ver atletas asignados a andarivel 1 | Primer atleta = mayor prioridad de estado · sin scroll horizontal | MUX-03 · MUX-01 | 🔴 |
| F07-S02 | Juez 1 (móvil) | Seleccionar Ezequiel Cuchiarelli DBF · marcar DNS | Performance queda como DNS · atleta no aparece en ranking DBF | flujo DNS | 🔴 |
| F07-S03 | Juez 2 (móvil) | Seleccionar Víctor Valotto DBF (andarivel 2) · ingresar RP=52.40 · asignar tarjeta blanca | Secuencia correcta: performance → tarjeta → confirmar · pantalla completada en **verde** | UI-JUE-02 · MUX-02 · MUX-05 | 🔴 |
| F07-S04 | Juez 2 (móvil) | Verificar botones de tarjeta antes de seleccionar | Tarjetas sin color cuando no están seleccionadas (blanca/roja diferenciadas al seleccionar) | MUX-02 | 🟡 |
| F07-S05 | Juez 1 (móvil) | Seleccionar Guadalupe Fardi DNF (andarivel 1) · ingresar RP=41.05 | Tarjeta blanca · JUNIOR FEM rank 1 DNF | flujo JUNIOR | 🟡 |
| F07-S06 | Juez 2 (móvil) | Seleccionar Alejandro Alperin SPE (andarivel 2) · ingresar RP=00:59.00 | Marca en mm:ss · tarjeta blanca | MUX-08 SPE | 🟡 |
| F07-S07 | Juez 2 (móvil) | Seleccionar Víctor Valotto STA (andarivel 2) · ingresar RP=04:32.98 | Marca en formato mm:ss · tarjeta blanca | MUX-08 | 🔴 |
| F07-S08 | Juez 3 (móvil) | Seleccionar José Enjuto STA (andarivel 3) · ingresar RP=06:33.05 | Tarjeta blanca · pantalla completada en verde | MUX-05 | 🔴 |
| F07-S09 | Juez 3 (móvil) | Ver "Mis asignaciones" · verificar que solo aparece STA | Solo STA en su lista · no ve DBF/DNF/DYN/SPE | UI-JUE-01 | 🟡 |
| F07-S10 | Juez 1 (móvil) | Verificar keypad RpSelector en pantalla de ingreso de RP | Keypad completamente visible sin scroll horizontal en móvil | MUX-01 | 🟡 |

**Verificación cruzada (después de cada performance):**

| Punto de verificación | Actor | Qué verificar |
|----------------------|-------|---------------|
| Post F07-S03 | Organizador | Resultado de Víctor Valotto visible en grilla DBF con RP y tarjeta |
| Post F07-S06 | Portal (visitante) | Página pública muestra resultado de José Enjuto en STA (polling 30s) |
| Post F07-S07 | Atleta (Guadalupe Fardi) | Login → ver resultado propio · RP=41.05 · rank 1 JUNIOR FEM DNF |

**Estado al cierre de fase:** torneo `EJECUCION` · 6 performances manuales registradas.

---

### F-08 — Ejecución: Flujos de Excepción

**Objetivo:** validar los flujos que no son el camino feliz — BKO, tarjeta amarilla con revisión — que son los más propensos a errores y los más críticos para la integridad del ranking.

**Dispositivo:** juez (móvil) · organizador (desktop)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F08-S01 | Juez (móvil) | Registrar performance con BKO · verificar botón "Confirmar BKO" | Botón "Confirmar BKO" **habilitado** (MUX-04 resuelto) · al confirmar: tarjeta roja automática · MotivoDQ = BKO_SUPERFICIE | MUX-04 | 🔴 |
| F08-S02 | Juez (móvil) | Verificar pantalla completada post-BKO | Pantalla muestra color **rojo** (no verde) | MUX-05 | 🔴 |
| F08-S03 | Organizador | Ver performance BKO en grilla | Tarjeta roja · DQ visible con motivo | — | 🟡 |
| F08-S04 | Juez (móvil) | Registrar performance · asignar tarjeta **amarilla** | Performance queda en estado "revisión" · UI de revisión manejable | MUX-07 | 🟡 |
| F08-S05 | Juez (móvil) | Cerrar revisión tarjeta amarilla como **blanca con penalización** | Performance válida con deducción aplicada · RP final = RP − deducción | tarjeta amarilla cierre | 🔴 |
| F08-S06 | Organizador | Verificar resultado post-penalización | RP ajustado visible en resultados · ranking actualizado | — | 🟡 |

**Verificación cruzada (post F08-S01):** portal público refleja que la disciplina/atleta tiene tarjeta roja (si la UI pública lo muestra).

**Estado al cierre de fase:** torneo `EJECUCION` · flujos de excepción validados.

---

### F-09 — Resultados Completos y Premiación

**Objetivo:** cargar el dataset completo de resultados y validar rankings, podios y overall desde el organizador y el atleta.

**Datos precargados:** Seed-C carga los resultados restantes de los 31 atletas.

```bash
uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <id>
```

**Dispositivos:** organizador (desktop) · atleta (móvil)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F09-S01 | Organizador | Ver resultados STA · verificar formato de marcas | Marcas en mm:ss · sin columna "PTS FAAS" · andarivel numérico | UI-ORG-05 · MUX-08 | 🔴 |
| F09-S02 | Organizador | Ver podios STA SENIOR MASC | 1° José Enjuto 06:33 · 2° Mauro Almada 05:42 · 3° Pablo Sale 05:19 (verificar con results.json) | UI-ORG-08 | 🔴 |
| F09-S03 | Organizador | Ver página de Podios (separada de Resultados) | Podios en página propia · contenido correcto por categoría/disciplina | UI-ORG-08 | 🔴 |
| F09-S04 | Organizador | Ver Overall SENIOR MASC | Ranking overall correcto según sistema FAAS | ranking overall | 🔴 |
| F09-S05 | Organizador | Iniciar premiación | Estado pasa a `PREMIACION` | — | 🔴 |
| F09-S06 | Portal (visitante) | Ver página pública del torneo post-Seed-C | Podios actualizados · grilla con resultados completos | US-6.6.4 | 🟡 |
| F09-S07 | Atleta (Víctor Valotto) | Ver resultado propio STA | RP=04:32.98 en mm:ss · rank 1 MASTER MASC STA | MUX-08 + consulta | 🟡 |
| F09-S08 | Atleta (Víctor Valotto) | Ver resultado propio DBF | RP=52.40m · rank correcto MASTER MASC DBF | consulta atleta | 🟡 |
| F09-S09 | Atleta (Guadalupe Fardi) | Ver resultado propio DNF | RP=41.05m · rank 1 JUNIOR FEM DNF | consulta JUNIOR | 🟡 |
| F09-S10 | Atleta (Guadalupe Fardi) | Ver overall propio | Rank 1 JUNIOR FEM overall | overall atleta | 🟡 |

**Estado al cierre de fase:** torneo `PREMIACION` · resultados completos · podios verificados.

---

### F-10 — Cierre y Estado Final

**Objetivo:** cerrar el torneo y verificar que el portal público y los portales de atleta muestran el estado final correcto.

**Dispositivos:** organizador (desktop) · atleta (móvil) · visitante (cualquier)

| ID | Actor | Acción | Resultado esperado | Verifica | Severidad |
|----|-------|--------|--------------------|----------|-----------|
| F10-S01 | Organizador | Cerrar torneo | Estado pasa a `CERRADO` | — | 🔴 |
| F10-S02 | Portal (visitante) | Ver estado en `/portalapnea` | Torneo marcado como "Cerrado" o "Finalizado" · resultados accesibles | INC-6.6 | 🟡 |
| F10-S03 | Portal (visitante) | Acceder a página pública del torneo cerrado | Resultados finales visibles · sin acciones de ejecución | US-6.6.4 | 🟡 |
| F10-S04 | Atleta | Login y ver resultados propios post-cierre | Resultados finales correctos | — | 🟡 |

**Estado al cierre de fase:** torneo `CERRADO` · UAT completado.

---

## 7. Registro de Hallazgos

Usar la siguiente tabla durante la ejecución. Un hallazgo por fila.

| ID | Fase | Escenario | Descripción | Severidad | Estado |
|----|------|-----------|-------------|-----------|--------|
| H-001 | — | — | — | — | — |

---

## 8. Checklist de Cierre INC-6.5

- [x] F-01: portal público accesible sin login · login de 3 jueces y organizador funcional
- [x] F-02: torneo creado con 5 disciplinas y 3 categorías desde UI
- [x] F-03: Seed-B ejecutado sin errores · 31 atletas visibles en inscriptos
- [x] F-04: flujo inscripción atleta → portal → login → formulario con AP inline
- [x] F-05: grilla generada · marcas STA/SPE en mm:ss · Juez 1+2 asignados a dinámicas · Juez 1+2+3 a STA · sin componentes eliminados · Juez 3 solo ve STA en sus asignaciones
- [x] F-06: torneo en EJECUCION · portal muestra "En ejecución" · página pública con grilla
- [x] F-07: 6 performances manuales ingresadas por juez correcto según andarivel · secuencia correcta · formatos correctos · verificación cruzada positiva
- [x] F-08: BKO confirmar habilitado (MUX-04) · tarjeta roja en rojo (MUX-05) · tarjeta amarilla con cierre como blanca+penalización
- [x] F-09: Seed-C ejecutado · podios correctos · resultados en mm:ss · sin PTS FAAS · overall correcto · 13/19 PASS + 5 hallazgos H-09-01..05 resueltos
- [x] F-10: torneo CERRADO · portal y atleta muestran estado final · 13/13 PASS
- [x] 0 hallazgos bloqueantes sin resolver

---

*Plan diseñado: 2026-05-11 — estrategia por ciclo de vida del torneo (no por rol)*  
*Dataset: Apnea Indoor Buenos Aires 2025 · 31 atletas reales*  
*Fuente: PLAN-SP6.md · `data/datasets/buenos_aires_2025/`*
