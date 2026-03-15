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
                            docs/requirements/vision.md                  ⏳ pendiente
         ↓
Capa 2 — MODELO (DDD)    → docs/design/context-map.md                   ⏳ pendiente
                            docs/design/domain-model.md                  ⏳ pendiente
         ↓
Capa 3 — ESPECIFICACIÓN  → docs/iedd/US-IEDD-template.md                ✅
                            Una US-IEDD por cada historia (pre/post/invariantes)
         ↓
    [ IA como traductor conceptual — Claude Dev Kit /implement-us ]
         ↓
Capa 4 — ARQUITECTURA    → docs/design/architecture.md                  ⏳ pendiente
                            docs/adr/ADR-001 a ADR-004                   ✅
         ↓
Capa 5 — IMPLEMENTACIÓN  → src/  (empieza en SP1, luego de completar Semana 0)
```

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
- **Arquitectura:** Hexagonal + Event Sourcing (contexto Competencia)
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
├── adr/             ← Architecture Decision Records (ADR-001 a ADR-004 ✅)
├── contexto/        ← Documentos fundacionales del experimento (5 archivos ✅)
├── design/          ← Context Map, Domain Model, Architecture (⏳ pendientes)
├── dominio/         ← Descripción del dominio y RFs (5 archivos ✅)
├── iedd/            ← Marco metodológico IEDD (4 archivos ✅)
├── plans/           ← US-IEDD por incremento (genera el Dev Kit)
├── reports/         ← Reportes /implement-us (genera el Dev Kit)
├── requirements/    ← vision.md (⏳ pendiente)
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

## 7. Bounded Contexts (diseño estratégico — pendiente de formalizar)

El Context Map completo está pendiente (`docs/design/context-map.md`).
Mapa orientativo basado en el análisis previo:

| Bounded Context | Tipo | Contenido principal |
|----------------|------|---------------------|
| **Competencia** | Core Domain | Performance, ejecución, Event Sourcing |
| **Gestión de Torneo** | Supporting | Torneo, ciclo de vida, estados |
| **Registro** | Supporting | Atleta, inscripción, anuncios, FAZ |
| **Resultados** | Supporting | Rankings, podios, certificados |
| **Configuración** | Generic | Disciplinas, categorías, reglas |
| **Identidad** | Generic | Usuarios, roles, permisos |
| **Notificaciones** | Generic | Email, push |

**Competencia es el Core Domain.** Es donde vive la lógica no trivial, los invariantes
duros y el Event Sourcing. Todo lo demás sirve a Competencia.

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
| ADR-001 a ADR-004 | ✅ | `docs/adr/` |
| Contexto del experimento | ✅ | `docs/contexto/` (5 archivos) |
| Documentos del dominio | ✅ | `docs/dominio/` (5 archivos) |
| Marco metodológico IEDD | ✅ | `docs/iedd/` (4 archivos) |
| vision.md | ⏳ pendiente | `docs/requirements/vision.md` |
| Context Map | ⏳ pendiente | `docs/design/context-map.md` |
| Domain Model | ⏳ pendiente | `docs/design/domain-model.md` |
| Architecture doc | ⏳ pendiente | `docs/design/architecture.md` |
| Código SP1 | ⏳ pendiente | `src/` — empieza luego de Semana 0 |

**Próximo paso:** completar los documentos de diseño estratégico (Capas 1-4 de IEDD)
antes de iniciar SP1. Secuencia: vision.md → context-map.md → domain-model.md →
architecture.md → BL-000 actualizada → arrancar SP1.

---

## 15. Los Tres Horizontes del Experimento

| Horizonte | Duración estimada | SPs | Criterio de éxito |
|-----------|------------------|-----|-------------------|
| **1 — Validar** | 2-3 meses | SP1 + SP2 | BL-002 con métricas reales, primera retrospectiva del entorno |
| **2 — Construir** | 4-6 meses | SP3 + SP4 | Simulación de torneo completo, material para paper IEDD |
| **3 — Producir** | 6-12 meses | SP5 + capitalización | Torneo real, capítulos del libro, curso, ponencia |

---

*Última actualización: 2026-03-15 — Semana 0, incorporación de contexto experimental completo*
*Mantenido por: Claude Cowork (decisiones estratégicas) + Claude Code (implementación)*
