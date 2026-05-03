# WBS — AtaraxiaDive
## Estructura de Desglose del Proyecto con Ciclos de Vida, Fases, Hitos e Iteraciones

> **Propósito de este documento:** presentar la estructura completa del proyecto AtaraxiaDive
> como caso de estudio para estudiantes de Ingeniería de Software y Gestión de Proyectos.
> Muestra cómo se organiza un proyecto real conducido con IA aplicando los marcos
> IEDD (Ingeniería de Especificaciones Dirigida por el Dominio) y DDD (Domain-Driven Design).
>
> **Audiencia:** estudiantes de ingeniería con conocimientos básicos de ciclos de vida ágiles.

---

## 0. Antes del desglose: el modelo de trabajo

Antes de presentar la jerarquía de trabajo, conviene entender el modelo que la sostiene.
AtaraxiaDive no sigue un ciclo de vida puramente ágil ni puramente incremental: combina
los dos según el nivel de la jerarquía.

### Los cinco niveles del modelo

```
Nivel 0 — PROYECTO         → AtaraxiaDive (el sistema completo)
  │
Nivel 1 — HORIZONTE        → Agrupación estratégica (Validar / Construir / Producir)
  │                           Cada horizonte responde a una pregunta del experimento.
  │
Nivel 2 — SUBPROYECTO (SP) → Unidad de valor completa con nombre propio y entregable.
  │                           Análogo al Release en Scrum o a la Fase en cascada.
  │                           Cierra con una Baseline (BL) y un tag de git.
  │
Nivel 3 — INCREMENTO       → Unidad de ritmo. Porción de trabajo con DoD (Definición
  │                           de Terminado) concreta y observable. Análogo al Sprint,
  │                           pero sin timebox fijo: termina cuando la DoD se cumple.
  │                           Cierra con un Pull Request a `develop`.
  │
Nivel 4 — US-IEDD          → Historia de Usuario con precondición, postcondición e
  │                           invariantes formales. Unidad del Dev Kit. Produce tests,
  │                           código de dominio, y un reporte de calidad.
  │
Nivel 5 — /implement-us    → 10 fases de implementación (proceso genérico, no visible
                              en el desglose de WBS pero presente en cada US-IEDD).
```

### Las 10 fases de /implement-us (Nivel 5 — proceso por US)

Cada US-IEDD se implementa siguiendo este ciclo, conducido por el Dev Kit:

| Fase | Nombre | Descripción |
|------|--------|-------------|
| 1 | Análisis de invariantes | Revisar precondición, postcondición e invariantes de la US-IEDD |
| 2 | Diseño del dominio | Identificar aggregate, value objects, domain events y ports |
| 3 | Tests primero (TDD) | Escribir tests unitarios que fallen antes del código |
| 4 | Implementación dominio | Aggregate + value objects + events + reglas de negocio |
| 5 | Capa de aplicación | Comandos o queries que orquestan el dominio |
| 6 | Infraestructura | Repositorios, event store, adaptadores |
| 7 | API REST | Router FastAPI + schemas + dependency injection |
| 8 | Quality gate | CodeGuard → Pylint ≥ 8.0 + mypy strict + Ruff |
| 9 | Tests de integración y BDD | Scenarios Gherkin que verifican la DoD de la US |
| 10 | Commit y cierre | Conventional Commit + actualizar traceability matrix |

### Las iteraciones de ajuste (SP-ADJ)

Entre subproyectos, el proyecto ejecuta **sprints de ajuste técnico (SP-ADJ)** cuando
la revisión de cierre detecta deuda técnica, gaps arquitectónicos o inconsistencias de dominio.
No agregan funcionalidad nueva: mejoran la calidad del código existente antes de avanzar.
Son análogos a las *hardening iterations* de SAFe o a los *refactoring sprints* de XP.

### Los quality gates

| Momento | Herramienta | Modo | Bloquea |
|---------|-------------|------|---------|
| Cada commit | CodeGuard | Automático | No (advierte) |
| Cada PR a develop | DesignReviewer | Automático (hook) | Sí, si hay CRITICAL |
| Cierre de Incremento | DesignReviewer | Manual | Sí, confirmar 0 CRITICAL |
| Cierre de SP | ArchitectAnalyst | Manual | No (informa tendencias) |
| UAT post-SP | Tests funcionales | Manual (datos reales) | Sí (todos los checks deben pasar) |

---

## 1. El Ciclo de Vida del Proyecto

AtaraxiaDive se organiza en **tres horizontes** que responden a las tres preguntas
del experimento, seguidos por la **Fase 0** de inicialización:

```
Fase 0 — Inicialización            ──► Baseline BL-000 / tag v0.1.0
    │
    ▼
Horizonte 1 — Validar              ──► "¿El entorno funciona integrado?"
    ├── SP1 — La Performance        ──► Baseline BL-001 / tag v0.2.0
    └── SP2 — La Competencia        ──► Baseline BL-002 / tag v0.3.0
    │
    ▼
Horizonte 2 — Construir            ──► "¿IEDD sobrevive al dominio real?"
    ├── SP3 — El Torneo             ──► Baseline BL-003 / tag v0.4.0
    └── SP4 — La Plataforma         ──► Baseline BL-004 / tag v0.5.0
    │
    ▼
Horizonte 3 — Producir             ──► "¿El conocimiento fluye al producto intelectual?"
    ├── SP5 — La Puesta en Marcha   ──► Baseline BL-005 / tag v0.6.0  ✅
    └── SP6 — Validación, Ajustes y Despliegue  ──► Baseline BL-006 / tag v1.0.0  ⏳
```

---

## 2. WBS Completo — Jerarquía de Niveles

### ═══════════════════════════════════════════════
### NIVEL 0: AtaraxiaDive
**Plataforma web para gestión de torneos de apnea. Experimento empírico sobre
desarrollo de software con IA usando IEDD + DDD + arquitectura hexagonal.**
Stack: FastAPI (Python) + React PWA + SQLite por Bounded Context.

---

### ═══════════════════════════════════════════════
### FASE 0 — Inicialización  ✅  `v0.1.0`  `2026-03-19`

> **Propósito:** crear toda la infraestructura del experimento antes de escribir
> una sola línea de código de producto. La Fase 0 produce los artefactos de diseño,
> dominio y configuración que harán posible el trabajo en SP1–SP5.

**Entregables:**
- Repositorio git con estructura BC-first (ADR-006)
- 12 ADRs documentados (stack, arquitectura, Event Sourcing, SQLite, offline-first...)
- Context Map con 6 Bounded Contexts identificados por Event Storming
- Domain Model del Core Domain (BC Competencia)
- Event Storming Big Picture (dominio completo) y Process Modeling (BC Competencia)
- Visión del producto (`docs/requirements/vision.md`)
- Template US-IEDD y marco metodológico IEDD
- Configuración de quality gates (CodeGuard, DesignReviewer, ArchitectAnalyst)
- BL-000 registrada (baseline pre-código)

**Hito:** `BL-000-pre-codigo.md` · tag `v0.1.0`

---

### ═══════════════════════════════════════════════
### HORIZONTE 1 — Validar  ✅

> **Pregunta que responde:** ¿el ecosistema CM + Dev Kit + Software Limpio
> funciona como sistema integrado, o cada herramienta genera fricción?
>
> **Criterio de éxito:** BL-002 con métricas reales, 15+ US-IEDD trazadas,
> primera retrospectiva del entorno documentada.

---

#### ───────────────────────────────────────────
#### SP1 — La Performance  ✅  `v0.2.0`  `2026-03-24`

> **Objetivo:** walking skeleton. Una performance registrada de punta a punta
> por un juez en el celular. Valida la arquitectura completa con el caso más simple posible.
>
> **Demo del SP:** abrir la app en el celular, registrar 5 performances,
> mostrar la traza de eventos de cada una.

##### INC-1.1 — Fundación técnica  ✅
**DoD:** estructura de capas visible en el repo, entorno levanta con `uv run uvicorn`,
health-check responde 200.

| US | Descripción |
|----|-------------|
| US-1.1.1 | Crear estructura del proyecto con las 4 capas y entorno de desarrollo funcional |

##### INC-1.2 — El dominio habla  ✅
**DoD:** test automatizado que recorre el flujo completo crear → marcar → asignar tarjeta → verificar estado en Event Store.

| US | Descripción |
|----|-------------|
| US-1.2.1 | Modelar aggregate Performance con invariantes y estado (Event Sourcing) |
| US-1.2.2 | Implementar RegistrarPerformance con Event Store |
| US-1.2.3 | Asignar tarjeta blanca/roja y cerrar performance |
| US-1.2.4 | Manejar DNS (Did Not Start) como caso alternativo |
| US-1.2.5 | Corregir resultado post-cierre con registro de motivo |
| US-1.2.6 | Consultar audit log (secuencia de eventos de una performance) |

##### INC-1.3 — El juez ve y toca  ✅
**DoD:** interfaz visible en celular real con los 6 botones del flujo, sin conexión al backend.

| US | Descripción |
|----|-------------|
| US-1.3.1 | Pantalla del juez: flujo de 6 pasos con estados visuales en pantalla |

##### INC-1.4 — Todo conectado  ✅
**DoD:** juez ejecuta los 6 pasos en el celular, eventos persisten, flujo repetible para 3–5 atletas.

| US | Descripción |
|----|-------------|
| US-1.4.1 | Conectar interfaz del juez al backend (API calls reales) |
| US-1.4.2 | Verificar persistencia end-to-end con datos de prueba |

**Hito SP1:** `BL-001` · tag `v0.2.0` · 207 tests (unit + integration + BDD) · cobertura 98%

---

#### ───────────────────────────────────────────
#### SP2 — La Competencia  ✅  `v0.3.0`  `2026-03-28`

> **Objetivo:** disciplina completa con grilla, secuencia de atletas, andariveles y ranking.
> Es el primer producto que alguien del mundo de la apnea reconoce como flujo real de competencia.
>
> **Demo del SP:** ejecutar una competencia de STA y una de DNF con 10 atletas cada una,
> incluyendo DNS y black-outs. Mostrar el ranking final de cada una.

##### INC-2.0 — Planificación y diseño  ✅
**Actividad Cowork:** Event Storming Process Modeling del BC Competencia.
Produce: US candidatas SP2, grilla de aggregates, candidatos a invariantes.

##### INC-2.1 — La grilla de salida  ✅
**DoD:** juez avanza por la grilla atleta a atleta; al terminar una performance avanza automáticamente.

| US | Descripción |
|----|-------------|
| US-2.1.1 | Aggregate Competencia: crear y configurar (disciplina + atletas + orden) |
| US-2.1.2 | Generar grilla de salida con 10 atletas |
| US-2.1.3 | Avanzar secuencia al siguiente atleta al cerrar performance |
| US-2.1.4 | Ajuste manual del orden de grilla por el organizador |

##### INC-2.2 — Dos mecánicas, un modelo  ✅
**DoD:** STA (tiempo) y DNF (distancia) funcionando; juez ve el campo correcto según disciplina.

| US | Descripción |
|----|-------------|
| US-2.2.1 | Descriptor de disciplina: tipo de medición, unidad, regla de ranking |
| US-2.2.2 | Validar RP según tipo de disciplina (tiempo vs distancia) |

##### INC-2.3 — Andariveles simultáneos  ✅
**DoD:** 2–3 andariveles activos sin conflicto; performances en andariveles distintos registradas sin interferencia.

| US | Descripción |
|----|-------------|
| US-2.3.1 | Modelo de andariveles: grilla distribuye atletas y garantiza aislamiento |

##### INC-2.4 — El ranking  ✅
**DoD:** ranking con podio generado automáticamente al cerrar disciplina; visible en pantalla.

| US | Descripción |
|----|-------------|
| US-2.4.1 | Aggregate RankingCompetencia: calcular posiciones (empates, descalificados, DNS al final) |
| US-2.4.2 | API GET ranking por disciplina con podio destacado |

##### SP-ADJ-01 — Deuda técnica SOLID post-SP2  ✅
**Propósito:** 8 issues de refactoring detectados en revisión de cierre. Cero regresiones.

| US | Descripción |
|----|-------------|
| US-ADJ-1.1 | Domain cleanup: `ot_programado` property + OCP Competencia + snake_case |
| US-ADJ-1.2 | Refactor `ajustar_grilla`: extraer helpers OT y swap (OCP) |
| US-ADJ-1.3 | Consolidar `_build_stream_id` en módulo único (DRY) |
| US-ADJ-1.4 | Router DIP: `EventStorePort` + mover cross-BC a `app.py` |
| US-ADJ-1.5 | Router SRP: separar `schemas.py` y `dependencies.py` |

##### SP-ADJ-02 — Ajuste documental y arquitectónico  ✅

**Sub-sprint doc:** gaps en CLAUDE.md, baselines, traceability matrix, domain-model, HITOs.

**Sub-sprint code (US):**

| US | Descripción |
|----|-------------|
| US-ADJ-2.6 | Extraer `Disciplina` a `shared/domain/` (reutilización cross-BC) |
| US-ADJ-2.7 | DIP en router: inversión de dependencias en composition root |
| US-ADJ-2.8 | Composition root en `app.py`: wiring de todos los BCs |

**Hito SP2:** `BL-002` · tag `v0.3.0` · 481 tests totales (100% pasando)

---

### ═══════════════════════════════════════════════
### HORIZONTE 2 — Construir  ✅

> **Pregunta que responde:** ¿IEDD mejora la calidad de las especificaciones
> o es teoría que no sobrevive el contacto con un proyecto real?
>
> **Criterio de éxito:** simulación de torneo completo de principio a fin,
> material suficiente para un paper sobre IEDD con evidencia empírica.

---

#### ───────────────────────────────────────────
#### SP3 — El Torneo  ✅  `v0.4.0`  `2026-04-04`

> **Objetivo:** ciclo de vida completo del torneo. Inscripción, anuncios, grillas automáticas,
> múltiples disciplinas, autenticación multi-rol, publicación de resultados.
>
> **Demo del SP:** simular un torneo completo con 5 disciplinas, 20 atletas y 3 roles
> (organizador, juez, atleta) desde la creación hasta la premiación.

##### INC-3.1 — El torneo como máquina de estados  ✅
**DoD:** torneo transiciona por las 6 fases (Creado → Inscripción → Preparación → Ejecución → Premiación → Cerrado); autenticación básica con rol de organizador.

| US | Descripción |
|----|-------------|
| US-3.1.1 | Aggregate Torneo: ciclo de vida con 6 estados y transiciones con restricciones |
| US-3.1.2 | Autenticación JWT: registro, login y rol organizador |

##### INC-3.2 — La inscripción  ✅
**DoD:** atleta se auto-registra, ve disciplinas disponibles y se inscribe; organizador ve la lista de inscriptos; cierre de inscripción al transicionar.

| US | Descripción |
|----|-------------|
| US-3.2.1 | Aggregate Atleta en BC Registro: datos personales, categoría, club |
| US-3.2.2 | Inscripción: atleta se inscribe en disciplinas del torneo |
| US-3.2.3 | Rol atleta: login propio + vista de disciplinas y estado de inscripción |

##### INC-3.3 — Anuncios y grillas automáticas  ✅
**DoD:** atleta ingresa AP; organizador genera grilla automáticamente; ajuste manual disponible.

| US | Descripción |
|----|-------------|
| US-3.3.1 | Anuncio (AP): atleta registra marca anunciada por disciplina |
| US-3.3.2 | Generación automática de grilla desde APs (orden AIDA/CMAS por disciplina) |

##### INC-3.4 — Multi-disciplina y jueces asignados  ✅
**DoD:** torneo con 5 disciplinas (STA, DNF, DBF, DYN, SPE); juez asignado a cada disciplina y operación aislada por asignación.

| US | Descripción |
|----|-------------|
| US-3.4.1 | Asignación de jueces a disciplinas del torneo |
| US-3.4.2 | Rol juez: login + vista filtrada por disciplinas asignadas |

##### INC-3.5 — Premiación y Overall  ✅
**DoD:** rankings por disciplina calculados automáticamente; Ranking Overall combinado; resultados publicados y visibles para atletas.

| US | Descripción |
|----|-------------|
| US-3.5.1 | Aggregate RankingOverall: combinar resultados de todas las disciplinas |
| US-3.5.2 | Política P-09: reglas de empate en ranking overall |
| US-3.5.3 | API GET resultados públicos (solo resultados finales, no parciales) |

##### SP-ADJ-03 — Refactoring SOLID/DDD post-SP3  ✅
**Propósito:** deuda detectada por DesignReviewer + análisis manual de BCs nuevos. 8 USs de refactoring.

| US | Descripción |
|----|-------------|
| US-ADJ-3.1 | Extraer `GrillaDeSalida` como Value Object + eliminar constante `_DISCIPLINAS_SP3` |
| US-ADJ-3.2 | Refactor BC Torneo: SRP en command handlers |
| US-ADJ-3.3 | Refactor BC Registro: DIP en repositorios |
| US-ADJ-3.4 | Extraer `TarjetaAsignacion` como Value Object en BC Competencia |
| US-ADJ-3.5 | Consolidar schemas duplicados entre BCs (DRY) |
| US-ADJ-3.6 | Refactor BC Identidad: extraer token service (SRP) |
| US-ADJ-3.7 | Mover validaciones de formato a Value Objects (OCP) |
| US-ADJ-3.8 | Refactor BC Resultados: separar cálculo de ranking y persistencia |

##### SP-ADJ-04 — Correcciones de dominio real  ✅
**Propósito:** dataset real del torneo Buenos Aires 2025 reveló inconsistencias con el deporte real (acrónimos AIDA/CMAS, orden STA, categorías, club, ranking por género).

6 US de corrección aplicadas y validadas contra datos reales.

**UAT SP3:** 28/28 checks con datos reales BA 2025 · 6 RPs correctos verificados.

**Hito SP3:** `BL-003` · tag `v0.4.0` · ArchitectAnalyst: `should_block=false` · HITO-17 (dataset real como oráculo del dominio)

---

#### ───────────────────────────────────────────
#### SP4 — La Plataforma  ✅  `v0.5.0`  `2026-04-18`

> **Objetivo:** transformar el sistema de "demo funcional" a "plataforma operativa".
> Ataca los atributos de calidad más exigentes: offline-first, notificaciones,
> auditoría criptográfica, y frontend PWA completo.
>
> **Demo del SP:** ejecutar una disciplina completa en modo avión; verificar audit trail;
> recibir emails reales en transiciones clave del torneo.

##### INC-4.0 — UX Design  ✅  `2026-04-08`
**Propósito:** artefactos de diseño como actividad formal del SP (HITO-18).
Produce: flujos de usuario, wireframes, prototipos navegables (juez / organizador / atleta),
decisiones de diseño frontend, ADRs de UX. PR #64.

##### INC-4.1 — Correcciones de dominio CMAS/FAAS  ✅  `2026-04-08`
**DoD:** motivos DQ formalizados como catálogo, tarjeta blanca con penalizaciones acumulables,
subdisciplinas SPE (SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50), orden de grilla corregido.

| US | Descripción |
|----|-------------|
| US-4.1.1 | Catálogo formal de `MotivoDQ` (BKO_SUPERFICIE, BKO_SUBACUATICO, NO_PROTOCOLO, etc.) |
| US-4.1.2 | Tarjeta blanca con penalizaciones: RP final = RP medido − Σ deducciones |
| US-4.1.3 | Variantes SPE: grilla y ranking independientes por variante |
| US-4.1.4 | Orden de grilla SPE: AP descendente (mayor AP primero) |
| US-4.1.5–4.1.8 | 4 US técnicas detectadas por DesignReviewer (refactoring de calidad) |

##### INC-4.2 — Fundación Frontend  ✅  `2026-04-11`
**DoD:** Vite 6 + React 19 + TypeScript strict + Tailwind v4 + PWA instalable;
autenticación JWT con rutas protegidas por rol. DesignReviewer: 0 CRITICAL, 142 WARNING.

| US | Descripción |
|----|-------------|
| US-4.2.1 | Setup frontend: Vite + React + TypeScript + Tailwind + PWA manifest |
| US-4.2.2 | Autenticación JWT frontend: login, tokens, rutas por rol |

##### INC-4.3 — Interfaz del Juez  ✅  `2026-04-12`
**DoD:** flujo de 6 pasos completo en frontend; casos alternativos (DNS, black-out, tarjeta amarilla);
adaptación a disciplina STA; UAT con datos reales BA 2025. DesignReviewer: 0 CRITICAL, 158 WARNING.

| US | Descripción |
|----|-------------|
| US-4.3.1 | Grilla de disciplinas: vista del juez con atletas y estado |
| US-4.3.2 | Flujo de 6 pasos: Llamar → Confirmar OT → Iniciar → Finalizar → RP → Tarjeta |
| US-4.3.3 | Casos alternativos: DNS, black-out, corrección post-registro |
| US-4.3.4 | Tarjeta amarilla con selección de penalizaciones |
| US-4.3.5 | Adaptación del flujo para disciplina STA (temporizador de tiempo) |

##### INC-4.4 — Offline-first  ✅  `2026-04-18`
**DoD:** Service Worker + IndexedDB (Dexie.js) + Background Sync; juez registra performances
en modo avión y sincroniza al reconectar; UAT en iPhone. DesignReviewer: 0 CRITICAL, 158 WARNING.

| US | Descripción |
|----|-------------|
| US-4.4.1 | Service Worker: cache de assets y pre-carga de grilla |
| US-4.4.2 | IndexedDB con Dexie.js: persistencia local de eventos de performance |
| US-4.4.3 | Background Sync: cola de sincronización y resolución de conflictos |

##### INC-4.5 — BC Notificaciones  ✅  `2026-04-18`
**DoD:** Aggregate Notificacion + event store propio; email real via Resend; políticas P-10/P-11
(idempotencia exactly-once); UAT con email real recibido. DesignReviewer: 0 CRITICAL, 174 WARNING.

| US | Descripción |
|----|-------------|
| US-4.5.1 | Aggregate Notificacion con Event Sourcing e idempotencia |
| US-4.5.2 | Adaptador Resend: envío de email real con template |
| US-4.5.3 | Política P-10: notificación al confirmar inscripción |
| US-4.5.4 | Política P-11: notificación al publicar resultados |
| US-4.5.5 | API de estado de notificaciones para el organizador |

##### INC-4.6 — Auditoría y Exportación  ✅  `2026-04-18`
**DoD:** audit log UI con traza completa; hash SHA-256 del event store al cerrar disciplina;
exportación CSV/JSON; inmutabilidad post-cierre. UAT en iPad.

| US | Descripción |
|----|-------------|
| US-4.6.1 | UI de audit log: traza completa de eventos por performance |
| US-4.6.2 | Hash SHA-256 del event store al cerrar disciplina (integridad criptográfica) |
| US-4.6.3 | Exportación de resultados en CSV |
| US-4.6.4 | Exportación de resultados en JSON |

##### SP-ADJ-06 — Ajuste post-SP4  ✅
**Propósito:** renombrar FAZ→FAAS en todo el sistema (código + docs + tests); bugs BUG-SP4-001/002;
correcciones UX detectadas en UAT. 5 USs implementadas.

| US | Descripción |
|----|-------------|
| US-ADJ-6.1 | Renombrar FAZ→FAAS: backend (domain + application + infra + tests) |
| US-ADJ-6.2 | Renombrar FAZ→FAAS: frontend + documentación |
| US-ADJ-6.3 | BUG-SP4-001: fix en cálculo de penalizaciones acumuladas |
| US-ADJ-6.4 | BUG-SP4-002: fix en sincronización offline de tarjeta amarilla |
| US-ADJ-6.5 | Correcciones UX del flujo del juez detectadas en UAT iPad |

**Hito SP4:** `BL-004` · tag `v0.5.0` · ArchitectAnalyst: `competencia` D=0.62 estable
(no superó umbral crítico 0.70) · HITOs 18–25

---

### ═══════════════════════════════════════════════
### HORIZONTE 3 — Producir  ⏳

> **Pregunta que responde:** ¿cuánto del conocimiento producido durante el desarrollo
> se puede capitalizar directamente en material académico sin reescritura?
>
> **Criterio de éxito:** torneo real completado con AtaraxiaDive como herramienta oficial;
> 3 capítulos del libro DDD con ejemplos de producción; 1 paper sobre IEDD + IA.

---

#### ───────────────────────────────────────────
#### SP5 — La Puesta en Marcha  ✅  `v0.6.0`  2026-05-01

> **Nota:** El alcance real de SP5 divergió de la planificación original de esta WBS
> (que preveía integración FAAS y torneo real). El SP5 ejecutado priorizó la capa
> de presentación completa (portal organizador + portal atleta + algoritmo FAAS).
> El torneo real y el despliegue se desplazaron a SP6. Ver `docs/plans/sp5/PLAN-SP5.md`.

**Incrementos implementados (real):**

| Incremento | Descripción | Estado |
|-----------|-------------|--------|
| INC-5.1 + ADJ | Panel del Organizador — ciclo de vida del torneo completo | ✅ |
| INC-5.2 + SP-ADJ-08 | Ejecución por Disciplina + ajuste post-UAT | ✅ |
| INC-5.3 | Gestión de Usuarios y Roles | ✅ |
| INC-5.4 | Identidad Extendida — auto-registro, cambiar/recuperar contraseña | ✅ |
| INC-5.5 | Inscripción Completa — portal atleta + declarar AP | ✅ |
| INC-5.6 | Algoritmo FAAS + rankings por categoría/género + UI podios | ✅ |
| INC-5.7 | Portal del Atleta — mis torneos, grilla, resultados, rankings | ✅ |
| SP-ADJ-07/09 | Deuda técnica SP4 + refactoring UX organizador | ✅ |
| INC-5.8 | Desestimado — absorbido en SP6 | — |

**Hito SP5:** `BL-005` · tag `v0.6.0` · ✅ 2026-05-01

---

#### ───────────────────────────────────────────
#### SP6 — Validación, Ajustes y Despliegue  ⏳  `v1.0.0`

> **Objetivo:** cerrar el ciclo v1.0. Corregir defectos y mejoras UX identificados en validación SP5,
> resolver deuda técnica crítica, ejecutar UAT completo con los tres roles y desplegar en producción.
>
> **Demo del SP:** torneo completo con los 3 roles (organizador, juez, atleta) sin bloqueos;
> `v1.0.0` publicado y accesible en producción.

##### INC-6.1 — Ajustes Juez  ⏳
**DoD:** BUG MUX-04 corregido y verificado en móvil; flujo de 6 pasos con secuencia correcta tarjeta→marca;
colores de tarjeta, grilla ordenada por estado y todos los ajustes UX del juez aplicados.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.1.1 | Fix BUG canSubmitBko + corrección secuencia tarjeta→marca | MUX-04 + UI-JUE-02 |
| US-6.1.2 | Colores tarjeta + pantalla completada según resultado | MUX-02 + MUX-05 |
| US-6.1.3 | Grilla ordenada por estado + keypad visible en móvil | MUX-03 + MUX-01 |
| US-6.1.4 | Rediseño inicio juez + STA mm:ss + tarjeta amarilla | UI-JUE-01 + MUX-08 + MUX-07 |
| US-6.1.5 | AtletaCard compacta en paso 5 | MUX-06 |

##### INC-6.2 — Ajustes Organizador  ⏳
**DoD:** portal organizador con torneos ordenados por fecha, columnas renombradas, nueva página de Podios
separada de Resultados, y formulario de nuevo torneo con categorías.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.2.1 | Inicio: ordenar torneos por fecha + mostrar fecha | UI-ORG-01 |
| US-6.2.2 | Inscriptos + Grilla: renombrar columnas AP→Anuncios + categoría legible | UI-ORG-03 + UI-ORG-04 |
| US-6.2.3 | Resultados: reordenar contenido + quitar PTS FAAS + andarivel | UI-ORG-05 |
| US-6.2.4 | Panel torneo: alertas sin "Resolver" + jueces sin texto nombre | UI-ORG-02 + UI-ORG-06 |
| US-6.2.5 | Nuevo torneo: selección categorías JUNIOR/SENIOR/MASTER | UI-ORG-07 |
| US-6.2.6 | Crear página de Podios | UI-ORG-08 |

##### INC-6.3 — Ajustes Atleta  ⏳
**DoD:** portal atleta con UX corregida; inscripción incluye declaración de AP; backend persiste
apto médico y constancia de pago.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.3.1 | Inicio atleta: en línea en header + sin "Hola" + torneos en curso ordenados | UI-ATL-01 |
| US-6.3.2 | Inscripción: declarar AP en formulario | UI-ATL-02 |
| US-6.3.3 | Backend inscripción: persistir apto médico | RF-IN-05 |
| US-6.3.4 | Backend inscripción: persistir constancia de pago | RF-IN-06 |

##### INC-6.4 — Deuda Técnica Sistema  ⏳
**DoD:** ciclo ADP en `competencia/domain/aggregates` eliminado; proyección `competencias_por_torneo`
materializada; violación D-05 corregida en routers; refactoring FAAS e Inscripción aplicados.

| US | Descripción | Hallazgos |
|----|-------------|-----------|
| US-6.4.1 | Romper ciclo ADP en `competencia/domain/aggregates` | AA-01 |
| US-6.4.2 | Materializar proyección `competencias_por_torneo` (O(n) → O(1)) | ARCH-01 |
| US-6.4.3 | Corregir violación hexagonal D-05 (routers → composition root) + reducir `registro` D↑ | ARCH-02 + AA-03 |
| US-6.4.4 | Refactoring `AlgoritmoPuntajeFAAS` dispatch por TipoDisciplina + black/lint | DR-02 + CG-01/03/04/05 |
| US-6.4.5 | Refactoring `DeclararAPInscripcionHandler` + `SQLiteInscripcionRepository` | DR-06 + DR-07 |
| US-6.4.6 | Decisión formal ARCH-03 + SRP `RankingCompetencia` + monitoreo `identidad`/`shared` | ARCH-03 + DR-01 + AA-02 + AA-04 |

##### INC-6.5 — Validación E2E + Despliegue  ⏳
**DoD:** UAT completo con los 3 roles sin bloqueos críticos; entorno productivo configurado y accesible;
`v1.0.0` tageado en `main` con ArchitectAnalyst BL-006 `should_block=false`.

| US | Descripción |
|----|-------------|
| US-6.5.1 | UAT E2E rol Juez — flujo completo de competencia con datos reales |
| US-6.5.2 | UAT E2E rol Organizador — ciclo completo torneo → grilla → resultados |
| US-6.5.3 | UAT E2E rol Atleta — inscripción → AP → consulta resultados |
| US-6.5.4 | Configuración entorno productivo (servidor, SSL, dominio, backup) |
| US-6.5.5 | Despliegue `v1.0.0` + tag BL-006 + ArchitectAnalyst final |

**Hito SP6:** `BL-006` · tag `v1.0.0` · ⏳ pendiente

---

## 3. Tabla de Hitos y Baselines

| Hito | Descripción | Tag git | Fecha | Estado |
|------|-------------|---------|-------|--------|
| BL-000 | Baseline pre-código (Fase 0 completa) | `v0.1.0` | 2026-03-19 | ✅ |
| BL-001 | SP1 La Performance | `v0.2.0` | 2026-03-24 | ✅ |
| BL-002 | SP2 La Competencia + SP-ADJ-01 + SP-ADJ-02 | `v0.3.0` | 2026-03-28 | ✅ |
| BL-003 | SP3 El Torneo + SP-ADJ-03 + SP-ADJ-04 | `v0.4.0` | 2026-04-04 | ✅ |
| BL-004 | SP4 La Plataforma + SP-ADJ-06 | `v0.5.0` | 2026-04-18 | ✅ |
| BL-005 | SP5 La Puesta en Marcha + SP-ADJ-07/08/09 | `v0.6.0` | 2026-05-01 | ✅ |
| BL-006 | SP6 Validación, Ajustes y Despliegue | `v1.0.0` | — | ⏳ |

---

## 4. Tabla de Entregables por Subproyecto

| SP | Nombre | Entregable de software | Entregable de conocimiento |
|----|--------|------------------------|----------------------------|
| Fase 0 | Inicialización | Repo + ADRs + Context Map + Domain Model | HITO-1, HITO-2 (adherencia IEDD, stack técnico) |
| SP1 | La Performance | BC Competencia (aggregate Performance) + API juez + frontend básico | HITO-3 a HITO-9 (walking skeleton, Event Sourcing, BDD) |
| SP2 | La Competencia | BC Competencia (aggregate Competencia) + BC Resultados + API grilla | HITO-10 a HITO-13 (CQRS, quality gates, deuda técnica formal) |
| SP3 | El Torneo | BC Torneo + BC Registro + BC Identidad + extensiones + UAT BA 2025 | HITO-14 a HITO-17 (secuencialidad IEDD, CQRS/ES, oráculo real) |
| SP4 | La Plataforma | Frontend PWA completo + offline-first + BC Notificaciones + auditoría | HITO-18 a HITO-25 (UX formal, Event Sourcing criptográfico, offline) |
| SP5 | La Puesta en Marcha | Portal organizador + portal atleta + algoritmo FAAS + rankings por categoría/género | HITO-26+ (UX formal, FAAS, portales completos) |
| SP6 | Validación, Ajustes y Despliegue | Sistema corregido y desplegado en producción (`v1.0.0`) | Paper IEDD + capítulos libro DDD + caso estudio IS |

---

## 5. Resumen Cuantitativo

| Métrica | Valor |
|---------|-------|
| Subproyectos | 6 + Fase 0 |
| Incrementos planificados | 27 (22 SP1–SP5 + 5 SP6) |
| Incrementos completados | 22 de 22 SP1–SP5 (100%) + 0 de 5 SP6 |
| US-IEDD completadas | ~87 (SP1–SP5) + 26 planificadas SP6 |
| Sprints de ajuste (SP-ADJ) | 6 completados (ADJ-01 a ADJ-09, numeración no correlativa) |
| Hitos (Baselines) | 6 cerrados (BL-000 a BL-005) + BL-006 pendiente |
| Bounded Contexts | 6 (Competencia, Torneo, Registro, Resultados, Identidad, Notificaciones) |
| ADRs documentados | 14 |
| HITOs de aprendizaje | 25+ |
| Tests totales (al cerrar SP5) | 500+ |
| Cobertura dominio/aplicación | ≥ 90% en todos los BCs |

---

## 6. El Ciclo de Vida de un Incremento (diagrama)

```
┌─────────────────────────────────────────────────────────────┐
│                  CICLO DE VIDA DE UN INCREMENTO             │
└─────────────────────────────────────────────────────────────┘

  COWORK (estratégico)              CODE (táctico)
  ─────────────────────             ─────────────────────
  1. Descomponer en US-IEDD
     · Identificar aggregates
     · Redactar invariantes
     · Escribir scenarios BDD
                                    2. /implement-us US-X.Y.Z
                                       (10 fases, una US por vez)
                                       · TDD → dominio → API → tests
  3. Revisar reporte                  · CodeGuard automático
     · ¿La DoD se cumple?
     · ¿Hay deuda visible?
                                    4. PR a develop
                                       · DesignReviewer (hook)
                                       · Bloquea si hay CRITICAL
  5. Verificar DoD de integración
     · Test de integración
     · UAT si cierra SP
                                    6. Merge + Conventional Commit
                                       · Actualizar traceability matrix
  7. Mini-retrospectiva
     · ¿Qué ajustar?
     · ¿Abrir SP-ADJ?
     · Registrar HITO si aplica

  Si cierra SP → ArchitectAnalyst → BL-NNN.md → tag vX.Y.0
```

---

## 7. Mapa de Conocimiento: de AtaraxiaDive al producto intelectual

Cada incremento produce no solo código sino conocimiento formalizable.
La regla del proyecto es: **no reescribir**. Los ADRs, retrospectivas y reportes
son materia prima directa para los productos intelectuales.

| Qué se aprende en AtaraxiaDive | Libro DDD | Curso IS | Paper IEDD |
|-------------------------------|-----------|----------|------------|
| Performance aggregate + invariantes | Cap. "Aggregates con invariantes reales" | Caso práctico semana 4 | Ejemplo RF→invariante→BDD |
| Event Sourcing para auditoría | Cap. "Domain Events como memoria" | Caso práctico semana 8 | — |
| Máquina de estados del Torneo | Cap. "State machines en el lenguaje ubicuo" | Caso práctico semana 6 | — |
| Offline-first + sync | Cap. "Arquitectura como consecuencia del dominio" | — | — |
| Métricas ArchitectAnalyst BL-001 a BL-004 | — | Lab: medir deuda técnica | Evidencia empírica IEDD |
| SP-ADJ como etapa formal (HITO-13) | — | Gestión de deuda técnica | Friction analysis en entornos IA |
| UAT con datos reales (HITO-17) | Cap. "El dominio como oráculo" | Validación con stakeholders | — |

---

*Versión 1.1 — 2026-05-03*
*Generado a partir de: PLAN-EXPERIMENTO.md · 04-estrategia_desarrollo.md · docs/plans/ · quality/reports/*
*Para uso académico — Ingeniería de Software · Gestión de Proyectos — FIUNER*
