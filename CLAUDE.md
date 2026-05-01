# CLAUDE.md — AtaraxiaDive

> Este archivo es la memoria del proyecto. Es leído automáticamente por Claude Code
> al iniciar una sesión, y por Claude Cowork como punto de entrada de contexto.
> **No empezar a trabajar sin leerlo.**

---

## 1. Propósito Real del Proyecto

**AtaraxiaDive no es solo un gestor de torneos de apnea.**

Es el vehículo de un experimento para generar **evidencia empírica propia** sobre
la aplicabilidad de dos marcos en desarrollo de software con IA:

- **IEDD** — Ingeniería de Especificaciones Dirigida por el Dominio
- **Software Limpio** — La Trilogía Limpia (Código + Diseño + Arquitectura Limpia)

El experimento busca responder tres preguntas concretas:

1. ¿El ecosistema CM + Dev Kit + Software Limpio funciona integrado, o cada herramienta
   genera fricción de coordinación?
2. ¿IEDD mejora la calidad de las especificaciones, o es teoría que no sobrevive el
   contacto con un proyecto real?
3. ¿Cuánto del conocimiento producido durante el desarrollo se capitaliza directamente
   en material académico (libro DDD, curso IS, paper IEDD) sin reescritura?

**Documento de referencia:** `docs/contexto/PLAN-EXPERIMENTO.md`

---

## 2. El Marco IEDD: Cómo Pensar Este Proyecto

Todo el trabajo sigue la cadena de 5 capas de IEDD. El orden no es opcional.

```
Capa 1 — DOMINIO         → docs/dominio/01-dominio_torneos_apnea.md     ✅
                            docs/requirements/vision.md                  ✅
         ↓
    [ Event Storming Nivel 1 — Big Picture ]
      docs/design/event-storming-big-picture.md              ✅
      (Dominio completo — descubre candidatos a BC)
      Produce: domain events del dominio completo, hot spots globales, fronteras de BC
         ↓
Capa 2 — MODELO (DDD)    → docs/design/context-map.md                   ✅
                            docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md ✅
                            docs/design/domain-model.md                  ✅
         ↑
    [ Event Storming Nivel 2 — Process Modeling ]
      docs/design/event-storming-competencia.md              ✅
      (BC Competencia — profundiza el Core Domain)
      Produce: comandos, políticas, invariantes, candidatos a US-IEDD
         ↓
Capa 3 — ESPECIFICACIÓN  → docs/iedd/US-IEDD-template.md                ✅
                            Una US-IEDD por cada historia (pre/post/invariantes)
         ↓
    [ IA como traductor conceptual — Claude Dev Kit /implement-us ]
         ↓
Capa 4 — ARQUITECTURA    → docs/design/architecture.md                  ✅
                            docs/adr/ADR-001 a ADR-012                   ✅
         ↓
Capa 5 — IMPLEMENTACIÓN  → src/  (empieza en SP1, luego de completar Semana 0)
```

> **Event Storming en este proyecto:** opera en dos niveles entre Capa 1 y Capa 2.
> No es una capa nueva de IEDD — es el método concreto para producir el modelo DDD
> a partir del dominio ya explorado. El Nivel 1 (Big Picture) descubre los BCs desde
> el comportamiento del dominio. El Nivel 2 (Process Modeling) profundiza el Core Domain
> ya formalizado. La hipótesis experimental es que esta secuencia produce invariantes más
> completos y BCs más coherentes que el análisis directo de los RFs.
> Ver: `docs/contexto/DECISION-EVENT-STORMING.md`

**Documentos de referencia:** `docs/iedd/` (3 archivos del marco conceptual)
**Análisis completo de IEDD:** `docs/contexto/ANALISIS-IEDD.md`

---

## 3. El Ecosistema de Herramientas

El proyecto opera con cuatro herramientas complementarias, cada una con un rol preciso:

```
IEDD (metodología)
  │
  ├── CM Framework (entorno-ia-dev)  → Cowork gestiona la memoria del producto
  │   docs/ · .cm/ · ADRs · baselines · trazabilidad
  │
  ├── Claude Dev Kit                 → Code implementa US a US (10 fases)
  │   /implement-us US-NNN
  │
  └── software_limpio                → Code mide la calidad en cada momento
      codeguard    (pre-commit, ~5s, solo advierte)
      designreviewer  (antes de merge, bloquea si CRITICAL)
      architectanalyst  (al cerrar baseline, persiste tendencias)
```

**Documentos de referencia:**
- `docs/contexto/ANALISIS-INTEGRACION-CLAUDE-DEV-KIT.md`
- `docs/contexto/ANALISIS-SOFTWARE-LIMPIO.md`
- `docs/contexto/ANALISIS-ATARAXIADIVE.md` — mapa de integración completo

---

## 4. Identidad del Producto

**AtaraxiaDive** es una plataforma web para gestión de torneos de apnea (freediving).

- **Stack:** FastAPI (backend Python) + React PWA (frontend) + SQLite (un archivo por BC — ADR-007)
- **Arquitectura:** Hexagonal + Event Sourcing (BCs Competencia y Notificaciones)
- **Desarrollador:** Victor Valotto
- **Horizonte:** 2026, sin fecha fija — avance por incrementos con DoD binaria

**Documentos de referencia:**
- `docs/dominio/01-dominio_torneos_apnea.md` — descripción del dominio
- `docs/dominio/02-arquitectura_referencia.md` — decisiones técnicas iniciales
- `docs/dominio/03-atributos_calidad.md` — criterios de calidad con IDs (AC-XX-NN)
- `docs/dominio/04-estrategia_desarrollo.md` — 5 subproyectos, 22 incrementos, DoD
- `docs/dominio/05-requerimientos_funcionales.md` — 48 RFs (~60% definidos)

---

## 5. Estructura del Repositorio

Estructura **BC-first** (ADR-006). Cada Bounded Context es un paquete Python independiente.

```
src/
├── competencia/         ← Core Domain (Event Sourcing)
│   ├── domain/{aggregates, value_objects, events, ports}
│   ├── application/{commands, queries}
│   ├── infrastructure/{event_store, repositories}
│   └── api/             ← router FastAPI del BC
├── torneo/              ← Supporting (CRUD)
│   ├── domain/{aggregates, value_objects, events, ports}
│   ├── application/{commands, queries}
│   ├── infrastructure/repositories
│   └── api/
├── registro/            (igual que torneo)
├── resultados/          (igual que torneo)
├── identidad/           (igual que torneo)
├── notificaciones/      ← Generic (Event Sourcing)
│   ├── domain/{aggregates, value_objects, events, ports}
│   ├── application/{commands, queries}
│   ├── infrastructure/{event_store, repositories}
│   └── api/
├── shared/
│   └── domain/{value_objects, base}   ← tipos cross-BC
└── app.py               ← ensamble central de routers FastAPI

frontend/            ← React PWA (se crea en SP4 con Vite)

tests/
├── unit/
│   └── <bc>/        ← árbol espejo de src/<bc>/
├── integration/
│   └── <bc>/        ← stack completo por BC
└── features/
    ├── steps/
    └── US-X.Y.Z.feature  ← organizados por US-IEDD

docs/
├── adr/             ← ADR-001 a ADR-013 ✅
├── contexto/        ← Documentos fundacionales del experimento + HITO-N-*.md ✅
├── design/          ← Context Map ✅ · ES Big Picture ✅ · Domain Model ✅ · Architecture ✅
├── dominio/         ← Descripción del dominio y RFs ✅
├── iedd/            ← Marco metodológico IEDD ✅
├── plans/           ← planes técnicos de implementación + candidatas por SP (dividido en sp1/, sp2/, …)
├── reports/         ← Reportes /implement-us (genera el Dev Kit)
├── requirements/    ← vision.md ✅
├── specs/           ← US-IEDD por SP — Capa 3 IEDD (dividido en sp1/, sp2/, …)
└── traceability/    ← matrix.md ✅

.cm/
├── baselines/       ← BL-000 ✅ · BL-NNN...
└── changes/         ← RFC-NNN.md

quality/
└── reports/
    ├── codeguard/        ← por US (genera /implement-us)
    ├── designreviewer/   ← por Incremento (genera PR)
    └── architectanalyst/ ← por Baseline (genera cierre SP)
```

---

## 6. Regla de Oro: Arquitectura Hexagonal (por BC)

**El dominio no importa nada de infraestructura.** Esta regla es absoluta dentro de cada BC.

```
<bc>/domain/         → no importa nada fuera de su propio domain/
<bc>/application/    → importa <bc>/domain/, nunca infrastructure/
<bc>/infrastructure/ → implementa puertos definidos en <bc>/domain/ports/
<bc>/api/            → importa <bc>/application/, nunca domain/ directamente
```

**Única excepción permitida:** cualquier capa puede importar desde `shared/domain/`.

**Comunicación entre BCs:** exclusivamente a través de puertos (`domain/ports/`).
Nunca imports directos entre BCs. Los ACLs viven en `infrastructure/` del BC consumidor.

DesignReviewer detecta automáticamente las violaciones en cada merge.

---

## 7. Bounded Contexts (diseño estratégico — formalizado en ADR-005)

Context Map completo: `docs/design/context-map.md` ✅
Decisión formal: `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` ✅

**6 Bounded Contexts definitivos** — emergieron del Event Storming Big Picture:

| Bounded Context | Tipo | Impl. | Madurez | Contenido principal |
|----------------|------|:-----:|:-------:|---------------------|
| **Competencia** | Core Domain | ES | operativo | AP, grilla, ejecución, tarjetas — lógica no trivial del deporte |
| **Torneo** | Supporting | CRUD | operativo | Ciclo de vida del torneo, disciplinas, `EntidadOrganizadora`, `Sede` |
| **Registro** | Supporting | CRUD | operativo | Atleta como persona, inscripción, anuncios, cancelaciones |
| **Resultados** | Supporting | CRUD | operativo | Rankings por disciplina/género, Overall, publicación incremental |
| **Identidad** | Generic | CRUD | operativo | Usuarios, roles (organizador/juez/atleta), autenticación JWT |
| **Notificaciones** | Generic | ES | modelado | Ciclo de vida de notificación, idempotencia exactly-once, Email/Push |

> **ES** = Event Sourcing · **CRUD** = persistencia relacional estándar
> **Madurez:** `operativo` = aggregate + API + tests completos · `modelado` = diseño DDD completo, implementación mínima

**`Configuración` fue eliminado:** sus conceptos (disciplinas → Torneo; reglas de tarjetas → Competencia)
son atributos de los BCs que los usan. No emergió como frontera natural en el ES Big Picture.

**`Notificaciones` usa Event Sourcing** para garantizar idempotencia estructural:
antes de enviar, verifica si `NotificacionEnviada` ya existe en el store para ese evento fuente.
Ver ADR-005 para justificación y trade-offs.

**Competencia es el Core Domain.** Es donde vive la lógica no trivial, los invariantes
duros y el Event Sourcing principal. Todo lo demás sirve a Competencia.

---

## 8. Lenguaje Ubicuo

| Término | Significado |
|---------|-------------|
| AP | Announced Performance — marca declarada antes de competir |
| RP | Realized Performance — marca efectivamente lograda |
| OT | Official Top — momento de inicio de la performance |
| DNS | Did Not Start — atleta no se presentó al OT |
| Tarjeta blanca | Performance válida sin infracciones |
| Tarjeta Blanca con Penalizaciones | Performance válida con infracciones técnicas; RP final = RP medido − Σ deducciones (N × 3m); penalizaciones acumulables (ADR-014) |
| Tarjeta amarilla | Estado de revisión pendiente → se cierra como Blanca, Blanca con Penalizaciones o Roja |
| Tarjeta roja | Descalificación — requiere `MotivoDQ` obligatorio (INV-P-11) |
| MotivoDQ | Catálogo formal de causas de descalificación: BKO_SUPERFICIE, BKO_SUBACUATICO, NO_PROTOCOLO, INFRACCION_TECNICA, NO_INICIO_VENTANA, SALIDA_FALSO |
| Black-out | Pérdida de conciencia → tarjeta roja automática con `MotivoDQ.BKO_SUPERFICIE` o `BKO_SUBACUATICO` |
| Variante SPE | Una de las cuatro variantes de sincronizado: SPE_2X50, SPE_4X50, SPE_8X50, SPE_16X50 — cada una genera grilla y ranking independientes; orden de grilla: AP descendente (mayor primero) |
| DoD | Definition of Done — criterio binario de cierre de incremento |
| US-IEDD | User Story con precondición, postcondición e invariantes formales |

---

## 9. Jerarquía de Trabajo

```
Subproyecto (SP1–SP5)              → genera Baseline (BL-NNN)
  └── Incremento (ej: 1.2)         → DoD de integración verificable
        └── US-IEDD (ej: US-1.2.1) → /implement-us → 10 fases

SP-ADJ (ajuste entre SPs)          → opcional, antes de cerrar la Baseline
  └── US-ADJ-N.M                   → refactor técnico o documental formal
```

| Subproyecto | Nombre | Baseline | Tag git | Estado |
|-------------|--------|----------|---------|--------|
| SP1 | La Performance | BL-001 | `v0.2.0` | ✅ Cerrado 2026-03-24 |
| SP2 | La Competencia | BL-002 | `v0.3.0` | ✅ Cerrado 2026-03-28 |
| SP3 | El Torneo | BL-003 | `v0.4.0` | ✅ Cerrado 2026-04-04 |
| SP4 | La Plataforma | BL-004 | `v0.5.0` | ✅ Cerrado 2026-04-18 |
| SP5 | La Puesta en Marcha | BL-005 | `v0.6.0` | ✅ Cerrado 2026-05-01 |
| SP6 | Validación, Ajustes y Despliegue | BL-006 | `v1.0.0` | ⏳ Pendiente |

> **SP-ADJ:** sub-sprint de ajuste técnico o documental entre SPs. Se ejecuta antes de
> cerrar la baseline cuando hay deuda acumulada que no conviene arrastrar al siguiente SP.
> SP-ADJ-01 (post-SP2) resolvió deuda SOLID. SP-ADJ-02 (post-SP2) resuelve deuda documental
> y arquitectónica cross-BC. Ver `docs/contexto/HITO-13-SP-ADJ-DEUDA-TECNICA-COMO-ETAPA-FORMAL.md`.

**Documento de referencia:** `docs/dominio/04-estrategia_desarrollo.md`

---

## 10. Convenciones de Código

### Python (backend)
- **Formato:** Black, line-length 100
- **Imports:** isort, perfil Black
- **Linting:** Ruff + Pylint ≥ 8.0
- **Tipos:** mypy en modo estricto — todos los métodos públicos tipados
- **Cobertura mínima:** 90% en `domain/` y `application/`

### Commits (Conventional Commits)
```
feat(domain): agregar aggregate Performance con invariantes [US-1.2.1]
test(domain): tests unitarios de Performance.asignar_tarjeta
docs(adr): ADR-002 decisión FastAPI como backend
chore(cm): registrar BL-001 cierre SP1

# Types: feat | fix | refactor | test | docs | chore
# Scopes: domain | application | infra | api | frontend | cm | tests | design
```

### Branching
```
main          ← baselines etiquetadas (v0.1.0, v0.2.0...)
  └── develop ← integración continua — recibe PRs individuales por US
        ├── feature/US-X.Y.Z-descripcion-corta   ← una branch por US-IEDD
        ├── feature/inc-X.Y-descripcion-corta    ← incrementos técnicos sin US
        └── fix/descripcion-corta
```

---

## 11. Quality Gates (software_limpio)

| Momento | Herramienta | Modo |
|---------|-------------|------|
| Cada commit | CodeGuard | Automático — advierte, no bloquea |
| Cada push (PR) | DesignReviewer | Automático — bloquea si CRITICAL |
| Cierre de Incremento | DesignReviewer | Manual — confirmar cero CRITICAL |
| UAT post-SP | Tests funcionales | Manual — Capa 1 + Capa 2 aprobadas |
| Cierre de Subproyecto | ArchitectAnalyst | Manual — informa tendencias |

---

## 12. Gestión de la Configuración (CM)

> **Fuente autoritativa del workflow:** `docs/plans/WORKFLOW-DESARROLLO.md`
> Define el ciclo completo por US, por Incremento y por Subproyecto — incluyendo orden
> de arranque, artefactos obligatorios por fase, quality gates y procedimiento de UAT.
> **Ante cualquier duda sobre cómo proceder, ese documento manda.**

Resumen operativo (ver WORKFLOW-DESARROLLO.md para el detalle completo):

- **Por US:** branch → tracker → Fase 0 → 10 fases → PR `--base develop` → merge
- **Por Incremento:** ajustar umbrales CBO/WMC al inicio · DesignReviewer manual al cierre · registrar en BL activa
- **Por SP:** ArchitectAnalyst → métricas BL → UAT post-SP → merge develop→main → tag · retrospectiva

---

## 13. Comandos Útiles

```bash
# Setup inicial del repositorio (una vez al clonar)
git config core.hooksPath .githooks   # activa el pre-push hook de DesignReviewer

# Entorno de desarrollo (sin Docker — ADR-010)
uv run uvicorn src.app:app --reload --env-file .env

# Tests
pytest tests/unit/
pytest tests/integration/
pytest tests/features/

# Calidad
codeguard src/                                           # análisis estático (Fase 7 /implement-us)
designreviewer src/ --config pyproject.toml              # diseño — bloquea si CRITICAL (pre-push a develop)
architectanalyst src/ --sprint-id BL-NNN --format json  # arquitectura — manual al cerrar SP

# Formato
black src/ tests/
isort src/ tests/
```

---

## 14. Estado Actual del Proyecto

**Fase 0 — ✅ COMPLETA (2026-03-19) — tag `v0.1.0`**

Todos los artefactos de diseño, dominio e infraestructura del experimento.
Ver `.cm/baselines/BL-000-pre-codigo.md` para el inventario completo.

---

**SP1 — La Performance — ✅ COMPLETO (2026-03-24) — tag `v0.2.0`**

| Artefacto | Estado | Detalle |
|-----------|--------|---------|
| BC Competencia — aggregate Performance | ✅ | Event Sourcing completo, 6 comandos, 6 eventos |
| API REST juez | ✅ | Endpoints AP, resultado, tarjeta, DNS, corrección, audit log |
| Tests SP1 | ✅ | 207 tests (unit + integration + BDD), cobertura 98% |
| ADR-013 exception management | ✅ | `docs/adr/ADR-013-exception-management.md` |
| HITOs 1–9 | ✅ | `docs/contexto/HITO-N-*.md` |
| BL-001 | ✅ | `.cm/baselines/BL-001-sp1-la-performance.md` |

---

**SP2 — La Competencia — ✅ COMPLETO (2026-03-28) — tag `v0.3.0`**

| Artefacto | Estado | Detalle |
|-----------|--------|---------|
| BC Competencia — aggregate Competencia | ✅ | Grilla, andariveles, ejecución multi-andarivel |
| BC Resultados — aggregate RankingCompetencia | ✅ | Ranking por disciplina, empates, podio |
| API REST grilla + ranking | ✅ | Endpoints configurar, generar, ajustar, confirmar, iniciar, ranking |
| Tests SP2 | ✅ | 481 tests totales (100% pasando) |
| HITOs 10–13 | ✅ | `docs/contexto/HITO-N-*.md` |
| BL-002 | ✅ | `.cm/baselines/BL-002.md` |

**SP-ADJ-01 — Ajuste Técnico Post-SP2 — ✅ COMPLETO (2026-03-28)**

5 US de refactoring SOLID (DRY, OCP, DIP, SRP) integradas en BL-002.
Ver `docs/plans/sp-adj-01/PLAN-SP-ADJ-01.md`.

---

**SP-ADJ-02 — Ajuste Post-Revisión de Hito — ✅ COMPLETO (2026-03-28)**

| Sub-sprint | Descripción | Estado |
|------------|-------------|--------|
| SP-ADJ-02-doc | Gaps documentales (CLAUDE.md, baselines, matrix, domain-model, HITOs) | ✅ Completo |
| SP-ADJ-02-code | Gaps arquitectónicos cross-BC (`Disciplina` → `shared/`, DIP router, composition root) | ✅ Completo |

3 US de refactoring arquitectónico cross-BC (US-ADJ-2.6, US-ADJ-2.7, US-ADJ-2.8).
Ver `docs/plans/sp-adj-02-code/PLAN-SP-ADJ-02-code.md` y `.work/revision-consistencia.md`.

---

**SP3 — El Torneo — ✅ COMPLETO (2026-04-04) — tag `v0.4.0`**

| Artefacto | Estado | Detalle |
|-----------|--------|---------|
| BC Torneo | ✅ | Aggregate + API REST + disciplinas y jueces |
| BC Registro | ✅ | Atleta + inscripción/cancelación + consultas |
| BC Identidad | ✅ | Registro/login JWT + dependencias por rol |
| Extensión BC Competencia | ✅ | `torneo_id` + creación de competencias asociadas |
| Extensión BC Resultados | ✅ | `RankingOverall` + política P-09 + API GET overall |
| Tests SP3 focalizados | ✅ | US-3.1.1 .. US-3.5.3 implementadas y validadas |
| HITO-16 | ✅ | Secuencialidad prescriptiva del pipeline documentada |
| SP-ADJ-03 | ✅ | 8 US de refactoring SOLID/DDD (GrillaDeSalida, TarjetaAsignacion, DIP Identidad…) |
| SP-ADJ-04 | ✅ | 6 US de correcciones dominio real (BA 2025: acrónimos AIDA, orden STA, categorías, club, ranking) |
| UAT SP3 | ✅ | 28/28 checks — datos reales BA 2025, 6 RPs correctos |
| DesignReviewer SP-ADJ-04 | ✅ | 0 CRITICAL, 119 WARNING — `quality/reports/designreviewer/SP-ADJ-04-report.txt` |
| ArchitectAnalyst BL-003 | ✅ | should_block=false · 4 CRITICAL DistanceAnalyzer (Zone of Pain — BCs CRUD, esperado) |
| HITO-17 | ✅ | Dataset real como oráculo empírico del dominio |

**ArchitectAnalyst BL-003 — hallazgos a monitorear en BL-004:**
- `competencia` D=0.62 ↑ (tendencia degradante): si supera 0.70 en BL-004, evaluar nuevas abstracciones en Core Domain
- `identidad`/`shared` D↓ (mejorando): esperado, BCs CRUD estables por diseño
- `registro` D=0.56 — (estable): sin cambios previstos en SP4

**SP-ADJ-05 — Ajuste Documental/Metodológico Post-BL-003 — ⏳ Diferido**

Plan: `docs/plans/sp-adj-05/PLAN-SP-ADJ-05.md` — 5 US de poda metodológica (HITO-14).
Diferido: SP4 se inició directamente después del tag `v0.4.0`. Absorbido parcialmente en SP-ADJ-06.

---

**SP4 — La Plataforma — ✅ COMPLETO (2026-04-18) — tag `v0.5.0`**

| Incremento | Descripción | Estado |
|-----------|-------------|--------|
| INC-4.0 — UX Design | Artefactos de diseño — flujos, wireframes, prototipos (juez, organizador, atleta), decisiones frontend | ✅ 2026-04-08 — PR #64 |
| INC-4.1 — Correcciones dominio CMAS/FAAS | 8 US: motivos DQ, tarjeta blanca con penalizaciones, subdisciplinas SPE, orden grilla + 4 US técnicas (DesignReviewer) | ✅ 2026-04-08 — PR #65 |
| INC-4.2 — Fundación Frontend | Vite 6 + React 19 + TypeScript strict + Tailwind v4 + PWA · autenticación JWT + rutas por rol | ✅ 2026-04-11 — PRs #67, #68 · DesignReviewer 0 CRITICAL, 142 WARNING |
| INC-4.3 — Interfaz del Juez | 5 US: grilla de disciplinas, flujo 6 pasos, casos alternativos, tarjeta amarilla, adaptación STA · UAT con datos reales BA 2025 | ✅ 2026-04-12 — PRs #69–#75 · DesignReviewer 0 CRITICAL, 158 WARNING |
| INC-4.4 — Offline-first | Service Worker + IndexedDB (Dexie.js) + Background Sync · UAT iPhone | ✅ 2026-04-18 — PR #77 · DesignReviewer 0 CRITICAL, 158 WARNING |
| INC-4.5 — BC Notificaciones | Aggregate Notificacion + event store + email real Resend + políticas P-10/P-11 · UAT email real | ✅ 2026-04-18 — PRs #79–#83 · DesignReviewer 0 CRITICAL, 174 WARNING |
| INC-4.6 — Auditoría y Exportación | Audit log UI + hash SHA-256 + exportación CSV/JSON · UAT iPad | ✅ 2026-04-18 — PRs #84–#89 |

| SP-ADJ | Descripción | Estado |
|--------|-------------|--------|
| SP-ADJ-06 | 7 US: FAZ→FAAS (código+docs+tests), refactoring técnico, UAT SP4 + bugs BUG-SP4-001/002 + UX fixes | ✅ 2026-04-18 — PRs #90, #91 |

| HITO | Descripción | Estado |
|------|-------------|--------|
| HITO-18 | UX design como incremento formal del SP — INC-4.0 | ✅ `docs/contexto/HITO-18-*.md` |
| HITO-19 | Ajustes técnicos del DesignReviewer como US-IEDD dentro del INC (no como SP-ADJ) | ✅ `docs/contexto/HITO-19-*.md` |
| HITO-20 | Invariantes de dominio que no cubren todas las variantes del deporte (STA, SPE) | ✅ `docs/contexto/HITO-20-*.md` |

**ArchitectAnalyst BL-004:** `competencia` D=0.62 estable (no superó umbral 0.70) · `should_block=false`

---

**SP5 — La Puesta en Marcha — ✅ COMPLETO (2026-05-01) — tag `v0.6.0`**

| Incremento | Descripción | Estado |
|-----------|-------------|--------|
| INC-5.1 — Panel del Organizador | Ciclo de vida del torneo, fases, inscriptos, grilla, jueces, monitor de ejecución | ✅ PRs #92–#103 |
| INC-5.1-ADJ — Ajuste post-UAT | Correcciones post-UAT INC-5.1 | ✅ PRs #104 |
| INC-5.2 — Ejecución por Disciplina | Vista maestro-detalle, habilitar disciplina, cierre manual | ✅ PRs #105, #106 |
| INC-5.3 — Gestión de Usuarios y Roles | Crear usuarios, asignar roles, vista atleta con inscripción básica | ✅ PRs #110, #111 |
| INC-5.4 — Identidad Extendida | Auto-registro público, cambiar/recuperar contraseña JWT+Resend | ✅ PRs #112–#114 |
| INC-5.5 — Inscripción Completa | Portal atleta (shell dark, wizard, declarar AP) + vista organizador inscriptos | ✅ PRs #120–#122 |
| INC-5.6 — Algoritmo FAAS | Puerto AlgoritmoPuntaje + implementación FAAS + ranking por categoría/género + UI podios | ✅ PRs #123–#128 |
| INC-5.7 — Portal del Atleta | Mis torneos, mi grilla, mis resultados, rankings/podios + fix resultados provisionales | ✅ PRs #137–#140 |
| INC-5.8 | Desestimado — contenido absorbido en SP6 | — |
| SP-ADJ-07 | Deuda técnica post-SP4 | ✅ |
| SP-ADJ-08 | Ajuste post-UAT INC-5.2 | ✅ |
| SP-ADJ-09 | Refactoring UX organizador + declarar AP en inscripción | ✅ PRs #129–#136 |
| DesignReviewer INC-5.7 | 0 CRITICAL · 256 WARNING | ✅ |
| ArchitectAnalyst BL-005 | should_block=false · `competencia` D=0.46 ↓ (mejora vs 0.62 BL-004) | ✅ |
| UAT SP5 | Aprobado — flujo E2E completo funcional | ✅ |
| BL-005 | `.cm/baselines/BL-005-draft.md` | ✅ |

**ArchitectAnalyst BL-005 — hallazgos a monitorear en BL-006:**
- `registro` D=0.59 ↑ (leve degradación vs 0.56 BL-004): monitorear en SP6
- `identidad` D=0.67 / `shared` D=0.64: Zone of Pain esperada en BCs CRUD — sin cambio previsto
- DependencyCycle en `competencia/domain/aggregates`: ciclo interno conocido, estable

---

## 15. Los Tres Horizontes del Experimento

| Horizonte | Duración estimada | SPs | Criterio de éxito |
|-----------|------------------|-----|-------------------|
| **1 — Validar** | 2-3 meses | SP1 + SP2 | BL-002 con métricas reales, primera retrospectiva del entorno |
| **2 — Construir** | 4-6 meses | SP3 + SP4 | Simulación de torneo completo, material para paper IEDD |
| **3 — Producir** | 6-12 meses | SP5 + capitalización | Torneo real, capítulos del libro, curso, ponencia |

---

## 16. Gestión de Sesión (OBLIGATORIO)

Este proyecto usa un sistema de memoria de sesión. **Seguir estas reglas sin excepción.**

### Al iniciar una sesión
- Si el hook SessionStart muestra una alerta de flag pendiente → ejecutar `/resume` **antes** de cualquier otra acción.
- Si no hay alerta, igualmente verificar si hay trabajo en curso leyendo `session-current.md`.

### Durante la sesión — uso proactivo de `/checkpoint`
**Ejecutar `/checkpoint` automáticamente** (sin esperar que el usuario lo pida) en estos momentos:
- Al completar una tarea o subtarea significativa
- Después de tomar una decisión de diseño o arquitectura
- Antes de una operación riesgosa (refactor grande, cambio de enfoque)
- Al terminar cualquier fase de una US-IEDD
- Cuando el usuario da señales de cierre ("listo", "ok seguimos", "después continuamos")
- Cada ~30 minutos de trabajo continuo

El checkpoint escribe en `session-current.md` el estado exacto: qué se completó, decisiones tomadas, y cuál es el próximo paso concreto.

### Al cerrar la sesión
El hook SessionEnd captura automáticamente los commits y crea el flag. No requiere acción manual.

### Archivos de sesión
```
~/.claude/projects/-Users-victor-PycharmProjects-ataraxiadive/memory/
├── session-metadata.json      ← timestamp, branch, razón de salida
├── session-current.md         ← estado de la sesión en curso (checkpoints)
├── session-history.md         ← historial de sesiones anteriores
└── session-needs-summary.flag ← indica que /resume debe ejecutarse
```

### Comandos disponibles
```
/resume      → restaurar contexto completo de sesión anterior
/checkpoint  → guardar estado actual (usar proactivamente durante la sesión)
```

### Dónde guardar cada tipo de conocimiento

Esta distinción es importante y aplica a cualquier proyecto IEDD:

| Artefacto | Alcance | Cuándo usarlo |
|-----------|---------|---------------|
| **HITO / BL** | Aprendizajes del experimento — valen para el paper, el libro, futuros proyectos con IEDD | Cuando el aprendizaje ilumina una hipótesis experimental, un patrón metodológico o una decisión de diseño que otros proyectos deberían conocer |
| **memory/** | Conocimiento operativo para futuras sesiones **en este proyecto** | Políticas, convenciones, datos de trabajo que Claude necesita recordar para operar bien — no tienen valor académico externo |

**Regla práctica:**
- *¿Querés capitalizar este aprendizaje en el paper o en un futuro proyecto?* → HITO o BL
- *¿Es una convención o dato que Claude necesita recordar para trabajar bien la próxima sesión?* → `memory/`

Los dos no son excluyentes: un aprendizaje puede vivir en ambos si tiene valor académico Y operativo.

---

*Última actualización: 2026-05-01 — §14 actualizado: SP5 ✅ cerrado v0.6.0 (INC-5.1..5.7 + SP-ADJ-07/08/09 · UAT PASS · BL-005 · ArchitectAnalyst); §9 SP5 marcado ✅ · SP6 agregado*
*2026-04-18 — §14 actualizado: SP4 ✅ cerrado v0.5.0 (INC-4.0..4.6 + SP-ADJ-06 · UAT PASS · BL-004); §9 SP4 marcado ✅*
*2026-04-13 — §14 actualizado: SP3 ✅ cerrado v0.4.0; SP-ADJ-05 diferido; SP4 en progreso (INC-4.0..4.3 ✅, HITOs 18–20)*
*2026-03-29 — §12 WORKFLOW-DESARROLLO.md como fuente autoritativa del workflow; §11 UAT post-SP agregado a quality gates*
*2026-03-28 — SP-ADJ-02-doc: §14 actualizado (SP1+SP2+ADJ), §9 patrón SP-ADJ, §5 HITOs*
*Mantenido por: Claude Cowork (decisiones estratégicas) + Claude Code (implementación)*
