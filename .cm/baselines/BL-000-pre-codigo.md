# BL-000 — Baseline Pre-Código

| Campo | Valor |
|-------|-------|
| **Tipo** | Fundacional |
| **Fecha** | 2026-03-14 |
| **Git tag** | `v0.0.0` |
| **Estado** | Cerrada |

---

## Descripción

Baseline pre-código. No hay implementación todavía. Esta baseline captura el estado
de la documentación fundacional sobre la cual arranca el desarrollo de AtaraxiaDive.

---

## Inventario de Configuration Items

| CI | Artefacto | Tipo | Descripción |
|----|-----------|------|-------------|
| CI-D01 | `docs/adr/ADR-001-event-sourcing-competencia.md` | Decisión | Event Sourcing para fase de competencia |
| CI-D02 | `docs/adr/ADR-002-fastapi-backend.md` | Decisión | FastAPI como framework backend |
| CI-D03 | `docs/adr/ADR-003-offline-first-pwa.md` | Decisión | Offline-first con PWA + IndexedDB |
| CI-D04 | `docs/adr/ADR-004-reglas-como-datos.md` | Decisión | Reglas de competencia como datos configurables |
| CI-D05 | `CLAUDE.md` | Convención | Convenciones del proyecto para Claude Code |
| CI-D06 | `pyproject.toml` | Configuración | Dependencias y herramientas de calidad |
| CI-D07 | `docker-compose.yml` | Infraestructura | Entorno de desarrollo local |
| CI-D08 | `.pre-commit-config.yaml` | Calidad | Hooks de pre-commit |

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

## Próximos Pasos

- Incremento 1.1: Fundación técnica (estructura de capas + docker-compose + health-check)
- Redactar US-IEDD-1.1.1 en `docs/plans/` antes de empezar

---

## Notas

Esta baseline marca el inicio del experimento: desarrollo de AtaraxiaDive usando
el entorno completo CM Framework + Claude Dev Kit + Software Limpio + IEDD.
