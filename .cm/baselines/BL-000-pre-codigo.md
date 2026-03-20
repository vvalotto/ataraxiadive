# BL-000 — Baseline Pre-Código

| Campo | Valor |
|-------|-------|
| **Tipo** | Fundacional |
| **Fecha apertura** | 2026-03-14 |
| **Fecha cierre Fase 0** | 2026-03-19 |
| **Git tag inicial** | `v0.0.0` |
| **Git tag Fase 0** | `v0.1.0` |
| **Estado** | ✅ Cerrada — Fase 0 completa |

---

## Descripción

Baseline pre-código. No hay implementación todavía. Esta baseline captura el estado
de la documentación fundacional sobre la cual arranca el desarrollo de AtaraxiaDive.

---

## Inventario de Configuration Items

### CIs iniciales (v0.0.0 — 2026-03-14)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-D01 | `docs/adr/ADR-001-event-sourcing-competencia.md` | Decisión | Event Sourcing para BC Competencia |
| CI-D02 | `docs/adr/ADR-002-fastapi-backend.md` | Decisión | FastAPI como framework backend |
| CI-D03 | `docs/adr/ADR-003-offline-first-pwa.md` | Decisión | Offline-first con PWA + IndexedDB |
| CI-D04 | `docs/adr/ADR-004-reglas-como-datos.md` | Decisión | Reglas de competencia como datos configurables |
| CI-D05 | `CLAUDE.md` | Convención | Convenciones del proyecto para Claude Code |
| CI-D06 | `pyproject.toml` | Configuración | Dependencias y herramientas de calidad |
| CI-D07 | `docker-compose.yml` | Infraestructura | Entorno de desarrollo local |
| CI-D08 | `.pre-commit-config.yaml` | Calidad | Hooks de pre-commit |

### CIs agregados en Fase 0 (v0.1.0 — 2026-03-19)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-D09 | `docs/requirements/vision.md` | Especificación | Visión del producto — 5 roles, alcance v1, criterios de éxito |
| CI-D10 | `docs/contexto/DECISION-EVENT-STORMING.md` | Decisión metodológica | Incorporación de ES entre Capa 1 y Capa 2 de IEDD |
| CI-D11 | `docs/design/event-storming-big-picture.md` | Modelo | ES Big Picture — 6 fases, 25 hot spots, 4 BCs emergentes |
| CI-D12 | `docs/design/context-map.md` | Modelo | Context Map v1.1 — 6 BCs definitivos, relaciones DDD |
| CI-D13 | `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md` | Decisión | 6 BCs + Event Sourcing en Competencia y Notificaciones |
| CI-D14 | `docs/design/event-storming-competencia.md` | Modelo | ES Process Modeling BC Competencia — 2 aggregates, 15 invariantes, 12 US candidatas |
| CI-D15 | `docs/design/domain-model.md` | Modelo | Domain Model v1.0 — aggregates, VOs, repositorios (puertos) |
| CI-D16 | `docs/design/architecture.md` | Arquitectura | Arquitectura C4 v1.0 — L1+L2+L3a+L3b |
| CI-D17 | `docs/design/estrategia-desarrollo-bc.md` | Plan | Mapeo BC×SP — secuencia, dependencias, hot spots resueltos |
| CI-D18 | `docs/traceability/matrix.md` | Trazabilidad | Matriz RF→BC→incremento→US-IEDD — 53 RFs, 85% definidos |

### CIs agregados en sesión pre-SP1 — stack técnico (2026-03-20)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-D19 | `docs/adr/ADR-006-estructura-bc-first.md` | Decisión | Estructura src/ BC-first — 6 paquetes Python + shared/ + app.py |
| CI-D20 | `docs/plans/WORKFLOW-DESARROLLO.md` | Proceso | Workflow completo: branching, PRs, quality gates, gestión con GitHub Issues+Milestones |
| CI-D21 | `docs/adr/ADR-007-sqlite-persistencia-bc.md` | Decisión | SQLite — un archivo `.db` por Bounded Context |
| CI-D22 | `docs/adr/ADR-008-event-store-sqlite.md` | Decisión | Event Store como tabla `events` append-only en SQLite |
| CI-D23 | `docs/adr/ADR-009-migraciones-por-bc.md` | Decisión | Migraciones Alembic independientes por BC |
| CI-D24 | `docs/adr/ADR-010-docker-produccion-cloud-run.md` | Decisión | Docker solo en prod — Cloud Run + Litestream |
| CI-D25 | `docs/adr/ADR-011-structlog-logging.md` | Decisión | structlog para logging estructurado (JSON prod / texto dev) |
| CI-D26 | `docs/adr/ADR-012-rfc7807-errores-http.md` | Decisión | RFC 7807 (Problem Details) para errores HTTP |
| CI-D27 | `docs/plans/SP1-candidatas.md` | Plan | SP1 — 4 incrementos, 7 US candidatas con pre/post/invariantes |
| CI-D28 | `docs/design/architecture.md` (v1.1) | Arquitectura | L4 Deployment candidato + SQLite/aiosqlite en todos los niveles C4 |

### CIs agregados en sesión pre-SP1 — herramientas (2026-03-20)

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-T01 | `.claude/skills/implement-us/` | Herramienta | Claude Dev Kit v1.3 — skill /implement-us (10 fases), perfil fastapi-rest |
| CI-T02 | `quality-agents v0.3.1` | Herramienta | software_limpio — codeguard, designreviewer, architectanalyst operativos |
| CI-T03 | `.githooks/pre-push` | Automatización | Pre-push hook: DesignReviewer bloquea push a develop si hay violaciones CRITICAL |
| CI-D19 | `docs/adr/ADR-006-estructura-bc-first.md` | Decisión | Estructura src/ BC-first — 6 paquetes Python + shared/ + app.py |
| CI-D20 | `docs/plans/WORKFLOW-DESARROLLO.md` | Proceso | Workflow completo: branching, PRs, quality gates, gestión con GitHub Issues+Milestones |
| CI-C01 | `src/` | Código | Esqueleto BC-first: 6 BCs × {domain,application,infrastructure,api} + shared/ |
| CI-C02 | `tests/` | Tests | Estructura unit/<bc>/, integration/<bc>/, features/steps/ |
| CI-C03 | `quality/reports/` | Calidad | Carpetas por agente: codeguard/, designreviewer/, architectanalyst/ |

---

## Estado del Código

Sin código de producción. Sin tests. Sin métricas de calidad.

---

## Documentación Fundacional (fuente de verdad del dominio)

Los siguientes documentos del proyecto de ingeniería (externos al repo) son la
base de este desarrollo:

| Documento | Ubicación | Contenido |
|-----------|-----------|-----------|
| Torneos de Apnea | `Mi Ingenieria de Software/AtaraxiaDive/` | Descripción del dominio |
| Arquitectura de Referencia v1 | ídem | Hexagonal + Event Sourcing + 6 aggregates |
| Atributos de Calidad v1 | ídem | 9 áreas con IDs AC-XX-NN |
| Estrategia de Desarrollo v2 | ídem | 5 subproyectos, 22 incrementos |
| Requerimientos Funcionales v1 | ídem | 48 preguntas/respuestas elicitadas |

---

## Deuda Técnica Conocida

Ninguna. El proyecto no tiene código todavía.

---

## Métricas de Fase 0

| Métrica | Valor |
|---------|-------|
| Artefactos planificados | 11 |
| Artefactos completados | 11 |
| Sesiones de trabajo | 7 |
| Hot spots resueltos | 9 / 9 (HS-02/10/12 + HS-P1 en ES · HS-19/22/25/P2 en sesión 7) |
| RFs mapeados | 53 (45 definidos · 7 pendientes SP4+ · 2 fuera de alcance v1) |
| US-IEDD candidatas SP1 | 8 |
| BCs definitivos | 6 (1 Core Domain · 3 Supporting · 2 Generic) |
| Commits en Fase 0 | 17 |

## Próximos Pasos

- **SP1 — La Performance:** elaborar US candidatas en `docs/plans/SP1-candidatas.md` y arrancar con `/implement-us`
- Crear Milestone SP1 en GitHub Issues
- Primera US-IEDD: `US-1.1.1`

---

## Notas

Esta baseline marca el inicio del experimento: desarrollo de AtaraxiaDive usando
el entorno completo CM Framework + Claude Dev Kit + Software Limpio + IEDD.

### Retrospectiva Fase 0 — aprendizajes clave

1. ES Big Picture → Context Map produce fronteras de BC más fundamentadas que derivarlas directamente de RFs.
2. ES Process Modeling produce invariantes que mapean directamente a precondiciones de US-IEDD.
3. Resolver hot spots en diseño (Capa 2 IEDD) cuesta minutos; en implementación, horas.
4. Las reglas de negocio viven en el BC que las configura, no en el que las usa (`FormulaPuntos`, `VentanaImpugnacion`).
5. El mapeo BC×SP hace visibles dependencias de implementación no obvias (Notificaciones al final).

**Hipótesis experimental a contrastar en BL-001:**
> Los invariantes derivados del Process Modeling producen US-IEDD con menos edge cases
> no anticipados durante la implementación de SP1.

Ver `docs/design/estrategia-desarrollo-bc.md` §11 para detalle completo.

---

### Retrospectiva Pre-SP1 — configuración del entorno de desarrollo (2026-03-20)

#### Lecciones operacionales

1. **El instalador del Dev Kit no tolera entornos sin TTY ni directorios preexistentes.** Requiere `--force` y Python con `pyyaml` disponible. Workaround: usar Python del sistema, no el venv gestionado por uv. Issues documentados en `vvalotto/claude-dev-kit` (#38, #39, #40).

2. **`uv pip install` falla si el proyecto tiene problemas de build en `pyproject.toml`.** La solución es instalar directamente desde git (`uv pip install git+https://...`) para evitar que uv intente reconstruir el proyecto.

3. **La estructura BC-first requiere configuración explícita en todas las herramientas.** `pyproject.toml` necesita secciones `[tool.codeguard]`, `[tool.designreviewer]`, `[tool.architectanalyst]` y `[tool.coverage.run]` apuntando a `src/{bc}/`, no a rutas genéricas.

4. **El hook `.githooks/pre-push` debe activarse manualmente** con `git config core.hooksPath .githooks` en cada clon. No es automático. Documentado en `CLAUDE.md` §13.

#### Lecciones experimentales (RQ1: fricción de integración del ecosistema)

5. **El Dev Kit asume arquitectura layered; el proyecto usa hexagonal DDD BC-first.** La fricción fue real y abarcó todas las fases del skill: paths, tipos de componente, paths de tests, quality gates. Requirió tres artefactos de adaptación: `ATARAXIADIVE-CONTEXT.md`, `customizations/fastapi-rest.json` v2.0.0, y patch de `phase-0-validation.md`.

6. **La fricción de integración es solucionable pero no es cero.** El ecosistema funciona integrado, pero exige un trabajo de calibración inicial proporcional a cuánto se aleja el proyecto del perfil genérico. En AtaraxiaDive, ~3 horas de configuración para un proyecto con arquitectura no-trivial.

7. **La adaptación del Dev Kit produce artefactos reutilizables.** El documento `ATARAXIADIVE-CONTEXT.md` y el `fastapi-rest.json` v2.0.0 eliminan la fricción en todas las US futuras. El costo es una inversión puntual, no recurrente.

8. **El mecanismo de adaptación debería ser un skill propio.** El proceso manual de calibración es candidato a automatización: issue #41 en `vvalotto/claude-dev-kit` propone `/adapt-project` como skill de configuración inicial.

**Observación experimental:**
> La fricción detectada en RQ1 es de tipo *incompatibilidad de supuestos arquitectónicos*, no de *incompatibilidad técnica*. Las herramientas coexisten sin conflicto; el problema es que el perfil genérico no conoce la arquitectura del proyecto. Esto sugiere que el Dev Kit necesita un mecanismo de onboarding por proyecto, no solo perfiles por stack tecnológico.

---

### Retrospectiva Pre-SP1 — stack técnico ADR-007..012 (2026-03-20)

#### Lección 9 — El stack técnico es una cascada de decisiones, no decisiones independientes

ADR-007 a ADR-012 forman una cadena: SQLite → Event Store en SQLite → Alembic por BC
→ sin Docker en dev → Cloud Run → structlog JSON. Cada decisión habilita o condiciona
a la siguiente. IEDD no tiene mecanismo explícito para capturar estas dependencias entre
decisiones técnicas — los ADRs las documentan, pero la relación entre ellos no es
visible en la metodología. Candidato a formalización.

#### Lección 10 — SQLite es una decisión de escala, no de conveniencia

La elección de SQLite en lugar de PostgreSQL no fue por facilidad sino por escala real
(500 performances/torneo, 4 torneos/año, 50 usuarios concurrentes). El puerto hexagonal
hace que la migración futura sea un cambio de adaptador — no de dominio. Esto convierte
la decisión en un caso de prueba empírico de la arquitectura hexagonal: si en SP3/SP4
se migra a PostgreSQL, la retrospectiva medirá cuánto cambió fuera de `infrastructure/`.

#### Lección 11 — Las restricciones del desarrollador son datos de contexto de Capa 1

La ausencia de Docker Desktop en el entorno de desarrollo condicionó ADR-010 y simplificó
el ciclo de trabajo (git clone + uv sync + uv run). Las restricciones del desarrollador
deberían ser explícitas en Capa 1 de IEDD — no supuestos implícitos que emergen al
tomar decisiones técnicas.

---

### Retrospectiva Pre-SP1 — consistencia documental post-ADR (2026-03-20)

#### Lección 12 — Una decisión tardía que contradice supuestos previos genera fricción de consistencia proporcional a su "distancia"

ADR-007 (PostgreSQL → SQLite) impactó 9 archivos en 4 carpetas. ADR-012 (RFC 7807),
en cambio, no impactó ningún documento previo. La diferencia: ADR-007 contradecía
supuestos de documentos tempranos; ADR-012 formalizaba algo no definido. El costo de
consistencia de un ADR es proporcional a cuántos supuestos previos contradice, no a la
magnitud del cambio técnico.

#### Lección 13 — La distinción documentos-de-entrada / documentos-derivados es necesaria y no estaba formalizada

Durante la revisión emergió una distinción operativa crítica: `docs/contexto/`,
`docs/dominio/` y `docs/requirements/vision.md` son documentos de entrada — capturan
el conocimiento previo al análisis técnico y no se modifican retroactivamente.
`docs/design/`, `docs/adr/`, `CLAUDE.md` y `docs/traceability/` son documentos
derivados — se actualizan cuando cambia un ADR. Esta distinción debería ser explícita
en el WORKFLOW-DESARROLLO.md.

#### Lección 14 — La revisión de consistencia es fricción inherente, no falla del método

Una sesión completa dedicada a consistencia documental no es ineficiencia — es el precio
de tener documentación rigurosa en un proceso iterativo. El valor diferencial: la
inconsistencia es detectable y corregible. Sin documentación, el supuesto incorrecto
simplemente se implementa y el costo aparece mucho más tarde.

**Hipótesis a evaluar en BL-001:**
> Si la revisión de consistencia se hace inmediatamente al aprobar el ADR (no en sesión
> posterior), el costo se reduce significativamente. Próximo bloque de ADRs: medir.

Ver `docs/contexto/HITO-2-STACK-TECNICO-CONSISTENCIA.md` para análisis completo.
