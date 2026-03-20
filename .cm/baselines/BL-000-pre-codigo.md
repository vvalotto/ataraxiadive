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

### CIs agregados en sesión pre-SP1 (2026-03-20)

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
