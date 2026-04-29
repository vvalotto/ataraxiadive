# Plan SP5 — La Puesta en Marcha (MVP Demo)

| Campo | Valor |
|-------|-------|
| **Sprint** | SP5 |
| **Baseline** | BL-005 |
| **Tag git** | `v1.0.0` |
| **Fecha** | 2026-04-18 |
| **Estado** | ⏳ En progreso (INC-5.1..5.6 ✅ · SP-ADJ-09 ✅ · INC-5.7/5.8 pendientes) |

---

## Objetivo

Transformar la plataforma técnicamente completa (SP4) en un **MVP demostrable y vendible**.

El criterio de éxito es poder mostrar a un comprador potencial un torneo de apnea de punta
a punta: inscripción de atletas con roles asignados, ejecución de disciplinas, y resultados
rankeados por categoría/género con podios instantáneos al cerrar cada disciplina.

**DoD de cierre de SP5:** un flujo completo puede ejecutarse sin errores visibles ni
workarounds — crear torneo → asignar roles → inscribir atletas → registrar anuncios →
generar grilla → ejecutar disciplina → ver tabla de resultados ordenada por OT →
ver podios por categoría/género instantáneamente.

---

## Contexto

SP4 entregó la infraestructura completa: PWA offline-first, BC Notificaciones, auditoría
con hash SHA-256, exportación CSV/JSON. Lo que falta para el MVP:

1. **Gestión de roles:** los usuarios existen (Identidad JWT) pero no hay UI para asignar
   juez/organizador a usuarios específicos. El organizador no puede configurar su torneo
   desde la UI.
2. **Inscripción completa:** no hay UI de inscripción. Los atletas y sus APs se cargan
   manualmente (seed/admin). Es el flujo de entrada del torneo.
3. **Algoritmo de puntaje y rankings por categoría/género:** RF-PM-01 estaba pendiente
   de definición. Definido en esta sesión de planificación (2026-04-18). El ranking
   actual es por marca absoluta y no separa categorías/géneros.
4. **Presentación de resultados:** dos vistas requeridas para el demo — tabla de ejecución
   (ordered by OT) y podios (ranked por puntaje, agrupados por categoría/género).

---

## Algoritmo de Puntaje FAAS (definido 2026-04-18)

### Disciplinas de distancia (DNF, DYN, DBF)

$$P_i = \frac{d_i}{d_{max}} \times 100$$

- $d_{max}$ = mayor distancia entre atletas con tarjeta blanca en esa disciplina
- Múltiples atletas pueden obtener 100 puntos si empatan en el máximo
- Tarjeta roja / DNS → $P_i = 0$, excluidos del cálculo de $d_{max}$

### Disciplinas de tiempo (STA, SPE)

$$P_i = \frac{t_{max} - t_i}{t_{max} - t_{min}} \times 100$$

- $t_{min}$ = menor tiempo (más rápido) → 100 puntos
- $t_{max}$ = mayor tiempo (más lento) → 0 puntos
- Caso borde: $t_{max} = t_{min}$ (todos iguales) → todos reciben 100 puntos
- Tarjeta roja / DNS → $P_i = 0$, excluidos del cálculo

### Overall

$$P_{overall,i} = \sum_{d \in disciplinas} P_{i,d}$$

Suma algebraica simple de puntos obtenidos en cada disciplina. El ranking Overall
ordena por $P_{overall}$ descendente.

### Extensibilidad (Strategy Pattern)

El algoritmo se modela como puerto en el dominio — extensible para CMAS y AIDA sin
modificar el dominio existente:

```
resultados/domain/ports/
└── algoritmo_puntaje.py       ← interfaz AlgoritmoPuntaje

resultados/domain/services/
├── algoritmo_faas.py          ← implementación actual (FAAS)
├── algoritmo_cmas.py          ← futura
└── algoritmo_aida.py          ← futura
```

El `Torneo` tendrá un atributo `reglamento: TipoReglamento` (VO: `FAAS`, `CMAS`, `AIDA`).
El caso de uso `CalcularRanking` recibe el algoritmo por DI — nunca sabe cuál es.

---

## Presentación de Resultados

### Vista 1 — Tabla de disciplina (ejecución)

Todos los atletas que participaron, ordenados por OT (orden de ejecución).

**Columnas:** Nombre | Género | Categoría | Club | AP | OT | Línea | RP | Tarjeta | Puntos

> **Cambio de dominio:** el género no aparecía en la grilla original (PDF BA 2025).
> Se agrega como columna requerida para el MVP.

### Vista 2 — Podios

Atletas ordenados por puntaje descendente, agrupados en 6 divisiones:

| Categoría | M | F |
|-----------|---|---|
| SENIOR | ✅ | ✅ |
| MASTER | ✅ | ✅ |
| JUNIOR | ✅ | ✅ |

**Columnas:** Posición | Nombre | Club | Puntos | RP

Los resultados son **instantáneos** al cerrar la disciplina — no requieren acción manual
del organizador.

---

## BCs activos en SP5

| BC | Tipo | Novedad en SP5 |
|----|------|----------------|
| **Competencia** | Core / ES | Corrección BUG-SP4-003 — nuevo comando dominio |
| **Torneo** | Supporting / CRUD | UI ciclo de vida completo del organizador |
| **Resultados** | Supporting / CRUD | Algoritmo de puntaje (Strategy) + ranking por categoría/género |
| **Registro** | Supporting / CRUD | Inscripción completa: apto médico, constancia pago, flujo UI |
| **Identidad** | Generic / CRUD | Asignación de roles desde UI |
| **Frontend** | React PWA | Nuevas pantallas: panel organizador, inscripción, roles, resultados/podios |

---

## SP-ADJ-07 — Deuda SP4 (pre-SP5)

Resuelve integridad antes de entrar al trabajo nuevo. 3 US pequeñas.

**Branch base:** `develop`

| US | Descripción | Área |
|----|-------------|------|
| **US-ADJ-7.1** | BUG-SP4-003 — comando `CorregirResultadoTrasDNS`: permitir registrar RP y tarjeta para una performance que quedó en DNS por error del juez | `competencia/domain/` |
| **US-ADJ-7.2** | BUG-SP4-004 — exponer `tarjeta_asignada` en endpoint `/grilla` para mostrar colores por tarjeta en UI de auditoría | `competencia/api/` |
| **US-ADJ-7.3** | SCOPE-SP4-001 — wiring P-11: `CompetenciaFinalizada` → email organizador con resultados | `src/app.py`, `notificaciones/` |

---

## Incrementos y US

### INC-5.1 — Panel del Organizador (ciclo de vida del torneo)

**DoD:** el organizador puede gestionar el ciclo de vida completo del torneo desde la UI:
crear torneo, transicionar fases, ver inscriptos, generar y ajustar grillas, asignar jueces,
monitorear ejecución, ver podios y exportar resultados. Las transiciones de estado respetan
las restricciones del dominio (incluido retroceso Ejecución → Preparación y Cancelado desde
cualquier estado).

| US | Descripción | Área |
|----|-------------|------|
| US-5.1.1 | Crear/editar torneo — formulario con nombre, sede, fechas, disciplinas; estado inicial Creado | `frontend/`, `torneo/api/` |
| US-5.1.2 | Gestión de fases — botones de transición por fase con validaciones del dominio | `frontend/`, `torneo/api/` |
| US-5.1.3 | Vista de inscriptos en Preparación — lista de atletas con AP registrado / sin AP | `frontend/`, `registro/api/` |
| US-5.1.4 | Generación y ajuste de grilla — generar automáticamente y reordenar manualmente | `frontend/`, `competencia/api/` |
| US-5.1.5 | Asignación de jueces a disciplinas desde UI | `frontend/`, `torneo/api/` |
| US-5.1.6 | Monitor de ejecución — vista del organizador durante la ejecución: progreso por disciplina | `frontend/` |

---

### INC-5.1-ADJ — Ajuste post-UAT INC-5.1

**Plan detallado:** `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md`

4 US de ajuste frontend (US-5.1.7..5.1.10) — bugs de navegación por fase y composición
de datos identificados en UAT funcional del panel organizador (2026-04-21).

---

### INC-5.2 — Ejecución por Disciplina

**Origen:** gaps funcionales UAT-5.1-06 y UAT-5.1-07 — el flujo de ejecución del
organizador carece de la vista maestro-detalle que permite habilitar cada disciplina
individualmente y del cierre manual de prueba.

**DoD:** el organizador puede seleccionar una disciplina del torneo en ejecución, habilitarla
(disparar `POST /competencia/{id}/iniciar`), monitorear su progreso en detalle y finalizarla
manualmente cuando corresponda. El cierre automático por P-08 coexiste con el cierre manual.

| US | Descripción | Hallazgo origen | Área |
|----|-------------|-----------------|------|
| US-5.2.1 | Vista maestro-detalle de disciplinas en ejecución — listar todas las disciplinas del torneo con estado, juez, grilla y progreso; al seleccionar una, abrir detalle con acción `Habilitar disciplina` | UAT-5.1-06 | `frontend/`, `competencia/api/` |
| US-5.2.2 | Finalización manual de prueba — acción `Finalizar prueba` por disciplina; permitir solo si no hay performances pendientes; registrar en auditoría si cierre fue manual o automático | UAT-5.1-07 | `competencia/api/`, `competencia/application/`, `frontend/` |

---

### INC-5.3 — Gestión de usuarios y roles ✅ Cerrado 2026-04-23

**DoD:** el organizador puede crear usuarios y asignarles rol desde la UI. Los atletas
acceden a su perfil e inscripción básica. Los roles se respetan en toda la UI.

| US | Descripción | Estado |
|----|-------------|--------|
| US-5.3.1 | UI de gestión de usuarios — organizador crea usuarios y asigna roles | ✅ PR #110 |
| US-5.3.2 | Vista del atleta — perfil + torneos en inscripción + `InscripcionPanel` básico | ✅ PR #111 |

---

### INC-5.4 — Identidad Extendida

**DoD:** cualquier persona puede auto-registrarse con nombre, apellido, email, password
y rol. El usuario autenticado puede cambiar su contraseña. Un usuario sin acceso puede
recuperar su contraseña vía email (Resend + JWT temporal con expiración 1h).

> **Nota:** extiende el modelo `Usuario` con `nombre` y `apellido` — impacta todas las
> capas de BC Identidad y los formularios de frontend que muestran usuarios.

| US | Descripción | Área |
|----|-------------|------|
| US-5.4.1 | Auto-registro — extender `Usuario` (nombre, apellido) + validar `rol ≠ ADMIN` en backend + página `/registro` con todos los campos + link "Nuevo usuario" en `LoginPage` | `identidad/`, `frontend/` |
| US-5.4.2 | Cambiar contraseña — `POST /auth/cambiar-password` (JWT requerido, verifica bcrypt actual, setea nueva ≥8 chars) + pantalla frontend accesible desde el perfil | `identidad/api/`, `frontend/` |
| US-5.4.3 | Olvidé contraseña — `POST /auth/solicitar-reset` (genera JWT `{sub, type:"password_reset", exp:+1h}`, envía email Resend con link) + `POST /auth/reset-password` (valida token, setea nueva password) + 2 pantallas frontend | `identidad/api/`, `notificaciones/`, `frontend/` |

---

### INC-5.5 — Inscripción completa ✅ Cerrado 2026-04-26

> Scope redefinido post-reversión 2026-04-25: portal atleta completo (shell dark, tab bar, wizard inscripción, declarar AP) + vista organizador con inscriptos y estado AP.
> DesignReviewer: 0 CRITICAL · 227 WARNING (`quality/reports/designreviewer/INC-5.5-report.txt`).

| US | Descripción | Estado |
|----|-------------|--------|
| US-5.5.1 | Portal atleta completo: shell dark + bottom tab bar + wizard inscripción 3 pasos + S-05 Mis inscripciones + S-06 Declarar/Modificar AP | ✅ PR #120 |
| US-5.5.2 | Vista del organizador — inscriptos con datos completos (nombre, disciplinas, estado AP) integrada en navegación UX aprobada | ✅ PR #121 |

---

### INC-5.6 — Algoritmo de puntaje y rankings por categoría/género ✅ Cerrado 2026-04-28

> DesignReviewer INC-5.6 + SP-ADJ-09: **0 CRITICAL · 252 WARNING** (+25 vs INC-5.5) — `quality/reports/designreviewer/INC-5.6-report.txt`.

| US | Descripción | Estado |
|----|-------------|--------|
| US-5.6.1 | Puerto `AlgoritmoPuntaje` + `AlgoritmoPuntajeFAAS` — fórmulas distancia y tiempo | ✅ PR #123 |
| US-5.6.2 | `TipoReglamento` en `Torneo` — VO extensible (FAAS/CMAS/AIDA); DI en `CalcularRanking` | ✅ PR #124 |
| US-5.6.3 | Ranking por categoría/género — `RankingCompetencia` con puntaje, agrupado por `Categoria` | ✅ PR #125 |
| US-5.6.4 | `RankingOverall` por categoría/género — `puntos_overall = Σ puntos_disciplina` | ✅ PR #126 |
| US-5.6.5 | UI `ResultadosPage` — tabla de ejecución ordenada por OT con género, categoría, AP, RP, tarjeta y puntos | ✅ PR #127 |
| US-5.6.6 | UI podios — 6 divisiones fijas (SENIOR M/F, MASTER M/F, JUNIOR M/F); overall bloqueado hasta cerrar todas las disciplinas | ✅ PR #128 |

---

### SP-ADJ-09 — Refactoring UX Organizador ✅ Cerrado 2026-04-29

> Resuelve gaps de navegación y consistencia visual del portal organizador identificados post-INC-5.6.
> DesignReviewer SP-ADJ-09: incluido en INC-5.6-report.txt (misma ejecución).

| US | Descripción | Estado |
|----|-------------|--------|
| US-ADJ-9.1 | Shell dark del organizador — layout base con sidebar y header consistente | ✅ PR #129 |
| US-ADJ-9.2 | Routing organizador reestructurado — rutas anidadas y navegación coherente | ✅ PR #130 |
| US-ADJ-9.3 | Home del organizador formalizado — vista de entrada con torneos activos | ✅ PR #131 |
| US-ADJ-9.4 | Dashboard operativo — resumen de estado del torneo en ejecución | ✅ PR #132 |
| US-ADJ-9.5 | Resultados y shell organizador reencuadrados — integración de `ResultadosPage` en el panel | ✅ PR #133 |
| US-ADJ-9.6 | Arquitectura UX organizador formalizada — separación de shell, layout y páginas | ✅ develop |
| US-ADJ-9.7 | Declarar AP en inscripción — atleta puede declarar/modificar AP desde el wizard | ✅ PR #136 |

---

### INC-5.7 — Portal del Atleta

**DoD:** el atleta tiene una vista completa de su participación en el torneo: sus torneos
inscriptos, su posición en la grilla por disciplina, sus resultados al cierre de cada
disciplina, y los rankings/podios de las disciplinas en las que compitió.

| US | Descripción | Área |
|----|-------------|------|
| US-5.7.1 | Mis torneos — lista de torneos inscriptos con estado actual del torneo | `frontend/`, `torneo/api/` |
| US-5.7.2 | Mi grilla — posición del atleta (OT + línea) por disciplina inscripta | `frontend/`, `competencia/api/` |
| US-5.7.3 | Mis resultados — RP, tarjeta y puntos obtenidos por disciplina | `frontend/`, `resultados/api/` |
| US-5.7.4 | Rankings y podios — tabla de ejecución + podio de cada disciplina en la que participó | `frontend/`, `resultados/api/` |

---

### INC-5.8 — Polish y demo-readiness

**DoD:** el flujo completo puede ejecutarse con los datos del torneo BA 2025 sin errores
visibles, workarounds, ni datos hardcodeados. La UI es presentable a un comprador.
Los resultados del torneo BA 2025 (STA, DNF, DYN, DBF, SPE) calculados por el sistema
coinciden con los resultados oficiales del PDF.

| US | Descripción | Área |
|----|-------------|------|
| US-5.8.1 | Seed del torneo BA 2025 completo — datos reales como caso de demostración | `data/`, `scripts/` |
| US-5.8.2 | Verificación de resultados BA 2025 — comparar salida del sistema contra PDFs oficiales | `tests/` |
| US-5.8.3 | UX fixes del flujo completo — correcciones identificadas al ejecutar el demo end-to-end | `frontend/` |

---

## Dependencias entre incrementos

```
SP-ADJ-07 (deuda SP4)                         ✅
  └── INC-5.1 (Panel Organizador)             ✅
        └── INC-5.1-ADJ (Ajuste post-UAT)    ✅
              └── INC-5.2 (Ejecución)         ✅
                    └── INC-5.3 (Usuarios)    ✅
                          └── INC-5.4 (Identidad Extendida)  ✅
                                └── INC-5.5 (Inscripción completa — APs + vista organizador)  ✅
                                      └── INC-5.6 (Puntaje + Rankings)  ✅
                                            ├── SP-ADJ-09 (Refactoring UX Organizador)  ✅
                                            └── INC-5.7 (Portal del Atleta)  ⏳
                                                  └── INC-5.8 (Polish + BA 2025)  ⏳
```

---

## Fuera de scope SP5 → mejoras futuras

| Item | Motivo |
|------|--------|
| Panel de configuración sin código (disciplinas, categorías) | No bloqueante para MVP demo |
| Integración FAAS / importación CSV | Formulario manual suficiente para demo |
| Simulacro con usuarios reales de la federación | Post-MVP |
| Primer torneo real en producción | Post-MVP |
| Notificaciones push (FCM) | Email cubre el caso base |
| Algoritmos CMAS / AIDA | Arquitectura lista (Strategy Pattern); implementación cuando se necesite |

---

## DoD de Cierre (BL-005)

- [ ] `pytest tests/` — 100% pass
- [ ] Flujo E2E: crear torneo → asignar juez → inscribir atleta → registrar AP → generar grilla → ejecutar disciplina → cerrar → ver tabla OT + podios
- [ ] Resultados BA 2025 calculados por el sistema coinciden con PDFs oficiales
- [ ] Rankings instantáneos al cerrar disciplina — sin acción manual
- [ ] 6 divisiones de podio correctas (SENIOR M/F, MASTER M/F, JUNIOR M/F)
- [ ] `designreviewer src/` — cero CRITICAL
- [ ] `CLAUDE.md §14` actualizado con SP5 completo

---

*2026-04-29 — INC-5.5 ✅, INC-5.6 ✅, SP-ADJ-09 ✅ · árbol dependencias actualizado · INC-5.7/5.8 ⏳ pendientes*
*2026-04-23 — INC-5.3 marcado ✅ · INC-5.4 redefinido como "Identidad Extendida" (auto-registro, cambiar/olvidé pw, modelo nombre/apellido) · INC-5.5..5.8 renumerados desde INC-5.4..5.7 original*
*Redactado: 2026-04-18 — SP5 La Puesta en Marcha (MVP Demo)*
*Algoritmo de puntaje FAAS definido en sesión de planificación 2026-04-18*
