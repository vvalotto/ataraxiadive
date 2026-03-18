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
                            docs/design/domain-model.md                  ⏳ pendiente
         ↑
    [ Event Storming Nivel 2 — Process Modeling ]
      docs/design/event-storming-competencia.md              ⏳ pendiente
      (BC Competencia — profundiza el Core Domain)
      Produce: comandos, políticas, invariantes, candidatos a US-IEDD
         ↓
Capa 3 — ESPECIFICACIÓN  → docs/iedd/US-IEDD-template.md                ✅
                            Una US-IEDD por cada historia (pre/post/invariantes)
         ↓
    [ IA como traductor conceptual — Claude Dev Kit /implement-us ]
         ↓
Capa 4 — ARQUITECTURA    → docs/design/architecture.md                  ⏳ pendiente
                            docs/adr/ADR-001 a ADR-005                   ✅
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

- **Stack:** FastAPI (backend Python) + React PWA (frontend) + PostgreSQL
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

```
src/
├── domain/          ← aggregates, value objects, domain events, invariantes
├── application/     ← use cases, command/query handlers
├── infrastructure/  ← event store, read model, PostgreSQL, repos
└── api/             ← FastAPI routes, schemas Pydantic, dependencias

frontend/            ← React PWA (package.json propio)

tests/
├── unit/            ← tests de aggregates y value objects
├── integration/     ← tests de use cases + infraestructura
└── features/        ← .feature files BDD (Gherkin)

docs/
├── adr/             ← Architecture Decision Records (ADR-001 a ADR-005 ✅)
├── contexto/        ← Documentos fundacionales del experimento (5 archivos ✅)
├── design/          ← Context Map ✅ · Event Storming Big Picture ✅ · Domain Model, Architecture (⏳ pendientes)
├── dominio/         ← Descripción del dominio y RFs (5 archivos ✅)
├── iedd/            ← Marco metodológico IEDD (4 archivos ✅)
├── plans/           ← US-IEDD por incremento (genera el Dev Kit)
├── reports/         ← Reportes /implement-us (genera el Dev Kit)
├── requirements/    ← vision.md ✅
└── traceability/    ← matrix.md

.cm/
├── baselines/       ← BL-000 ✅ · BL-NNN...
└── changes/         ← RFC-NNN.md

skills/              ← claude-dev-kit
quality/
└── reports/         ← quality gates por US (genera el Dev Kit)
```

---

## 6. Regla de Oro: Arquitectura Hexagonal

**El dominio no importa nada de infraestructura.** Esta regla es absoluta.

```
domain/         → no importa nada externo al propio dominio
application/    → importa domain/, nunca infrastructure/ directamente
infrastructure/ → implementa interfaces definidas en domain/
api/            → importa application/, nunca domain/ directamente
```

DesignReviewer detecta automáticamente las violaciones en cada merge.

---

## 7. Bounded Contexts (diseño estratégico — formalizado en ADR-005)

Context Map completo: `docs/design/context-map.md` ✅
Decisión formal: `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` ✅

**6 Bounded Contexts definitivos** — emergieron del Event Storming Big Picture:

| Bounded Context | Tipo | Impl. | Contenido principal |
|----------------|------|:-----:|---------------------|
| **Competencia** | Core Domain | ES | AP, grilla, ejecución, tarjetas — lógica no trivial del deporte |
| **Torneo** | Supporting | CRUD | Ciclo de vida del torneo, disciplinas, `EntidadOrganizadora`, `Sede` |
| **Registro** | Supporting | CRUD | Atleta como persona, inscripción, anuncios, cancelaciones |
| **Resultados** | Supporting | CRUD | Rankings por disciplina/género, Overall, publicación incremental |
| **Identidad** | Generic | CRUD | Usuarios, roles (organizador/juez/atleta), autenticación JWT |
| **Notificaciones** | Generic | ES | Ciclo de vida de notificación, idempotencia exactly-once, Email/Push |

> **ES** = Event Sourcing · **CRUD** = persistencia relacional estándar

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
| Tarjeta blanca | Performance válida |
| Tarjeta amarilla | Penalización parcial (con deducción) |
| Tarjeta roja | Descalificación |
| Black-out | Pérdida de conciencia → tarjeta roja automática |
| DoD | Definition of Done — criterio binario de cierre de incremento |
| US-IEDD | User Story con precondición, postcondición e invariantes formales |

---

## 9. Jerarquía de Trabajo

```
Subproyecto (SP1–SP5)              → genera Baseline (BL-NNN)
  └── Incremento (ej: 1.2)         → DoD de integración verificable
        └── US-IEDD (ej: US-1.2.1) → /implement-us → 10 fases
```

| Subproyecto | Nombre | Baseline |
|-------------|--------|----------|
| SP1 | La Performance | BL-001 |
| SP2 | La Competencia | BL-002 |
| SP3 | El Torneo | BL-003 |
| SP4 | La Plataforma | BL-004 |
| SP5 | La Puesta en Marcha | BL-005 |

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
  └── develop ← integración continua
        ├── feature/US-X.Y.Z-descripcion
        └── fix/descripcion-corta
```

---

## 11. Quality Gates (software_limpio)

```bash
# Pre-commit (automático, ~5s, nunca bloquea)
codeguard src/

# Antes de merge a develop (obligatorio, bloquea si CRITICAL)
designreviewer src/

# Al cerrar un Subproyecto / Baseline
architectanalyst src/ --sprint-id BL-NNN --format json
# Guardar output en .cm/baselines/BL-NNN-arquitectura.json
```

Umbrales mínimos para SP1:
- Pylint ≥ 8.0 en `domain/`
- Cobertura ≥ 85% en `domain/` + `application/`
- Cero imports de infraestructura en `domain/`

---

## 12. Gestión de la Configuración (CM)

### Al implementar una US
1. La US-IEDD debe estar en `docs/plans/US-X.Y.Z.md` antes de empezar
2. Usar `/implement-us US-X.Y.Z` con las 10 fases
3. Commit con referencia a la US: `feat(domain): ... [US-1.2.1]`
4. Actualizar `docs/traceability/matrix.md` al cerrar

### Al cerrar un Incremento
1. Verificar DoD de integración (test end-to-end observable)
2. Correr `designreviewer src/` — cero violations CRITICAL
3. Merge a `develop` con PR

### Al cerrar un Subproyecto (Baseline)
1. Correr `architectanalyst src/ --sprint-id BL-NNN --format json`
2. Registrar métricas en `.cm/baselines/BL-NNN.md`
3. Tag en git: `git tag v0.N.0`
4. Retrospectiva documentada en BL-NNN.md (alimenta el libro y el paper)

---

## 13. Comandos Útiles

```bash
# Entorno
docker-compose up

# Tests
pytest tests/unit/
pytest tests/integration/
pytest tests/features/

# Calidad
codeguard src/
designreviewer src/
architectanalyst src/ --sprint-id BL-NNN

# Formato
black src/ tests/
isort src/ tests/
```

---

## 14. Estado Actual del Proyecto

**Semana 0 — Inicialización**

| Artefacto | Estado | Ubicación |
|-----------|--------|-----------|
| Repositorio inicializado | ✅ | — |
| BL-000 baseline pre-código | ✅ | `.cm/baselines/BL-000-pre-codigo.md` |
| ADR-001 a ADR-005 | ✅ | `docs/adr/` |
| Contexto del experimento | ✅ | `docs/contexto/` (5 archivos) |
| Documentos del dominio | ✅ | `docs/dominio/` (5 archivos) |
| Marco metodológico IEDD | ✅ | `docs/iedd/` (4 archivos) |
| FASE-0-PLAN.md | ✅ | `docs/plans/FASE-0-PLAN.md` |
| DECISION-EVENT-STORMING.md | ✅ | `docs/contexto/DECISION-EVENT-STORMING.md` |
| vision.md | ✅ | `docs/requirements/vision.md` |
| Event Storming Big Picture | ✅ | `docs/design/event-storming-big-picture.md` |
| Context Map | ✅ | `docs/design/context-map.md` |
| ADR-005 BCs estratégico | ✅ | `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` |
| Event Storming Competencia | ⏳ pendiente | `docs/design/event-storming-competencia.md` |
| Domain Model | ⏳ pendiente | `docs/design/domain-model.md` |
| Architecture doc | ⏳ pendiente | `docs/design/architecture.md` |
| Estrategia desarrollo → BCs | ⏳ pendiente | `docs/design/estrategia-desarrollo-bc.md` |
| Traceability matrix | ⏳ pendiente | `docs/traceability/matrix.md` |
| Código SP1 | ⏳ pendiente | `src/` — empieza luego de Semana 0 |

**Herramientas (prerequisito para SP1):**

| Herramienta | Estado |
|-------------|--------|
| Claude Dev Kit (`/implement-us`) | ❌ No instalado — `skills/` vacío |
| software_limpio / quality-agents | ❌ No instalado — paquete ausente en dependencias |
| CodeGuard pre-commit hook | ⚠️ Configurado en `.pre-commit-config.yaml`, no funcional |
| DesignReviewer | ⚠️ Configurado en `pyproject.toml`, no funcional |
| ArchitectAnalyst | ⚠️ Configurado en `pyproject.toml`, carpeta `quality/` inexistente |

**Próximo paso:** completar los documentos de diseño estratégico restantes antes de iniciar SP1.
Ver plan completo en `docs/plans/FASE-0-PLAN.md`.
Secuencia: **event-storming-competencia.md** → domain-model.md → architecture.md →
estrategia-desarrollo-bc.md → matrix.md → instalar herramientas → BL-000 actualizada → arrancar SP1.

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

---

*Última actualización: 2026-03-18 — Semana 0, Context Map v1.1 y ADR-005: 6 BCs definitivos, ES en Notificaciones*
*Mantenido por: Claude Cowork (decisiones estratégicas) + Claude Code (implementación)*
