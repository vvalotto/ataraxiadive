# Reporte Final SP1 — "La Performance"

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP1 — La Performance |
| **Baseline** | BL-001 |
| **Período** | 2026-03-14 → 2026-03-24 |
| **Estado** | COMPLETO — pendiente tag v0.2.0 |
| **Autor** | Victor Valotto |

---

## 1. Alcance entregado

### Incrementos y US implementadas

| Inc | US | Descripción | Tests | Pylint |
|-----|----|-------------|-------|--------|
| 1.1 | — | Walking Skeleton: EventStorePort, SQLiteEventStore, Alembic, GET /health | 7 integration | — |
| 1.2 | US-1.2.1 | RegistrarAP + aggregate Performance (INV-P-01..P-04) | ~80 unit | 9.2 |
| 1.2 | US-1.2.2 | LlamarAtleta + AtletaLlamado (INV-P-05) | +unit | 9.4 |
| 1.2 | US-1.2.3 | RegistrarResultado + ResultadoRegistrado (INV-P-06) | +unit | 9.4 |
| 1.2 | US-1.2.4 | AsignarTarjeta + TarjetaAsignada (INV-P-07) | +unit | 9.3 |
| 1.2 | US-1.2.5 | RegistrarDNS + DNSRegistrado (INV-P-08, P-09) | +unit | 9.5 |
| 1.2 | US-1.2.6 | CorregirResultado + ResultadoCorregido (INV-P-10) | +unit | 9.5 |
| 1.3 | US-1.3.1 | Interfaz del Juez: Read Models + 3 endpoints GET | +integration | 9.58 |
| 1.4 | US-1.4.1 | Black-out con Distancia: INV-P-11 (distancia_blackout) | +unit+BDD | 9.53 |
| 1.4 | US-1.4.2 | Flujo E2E: GET /events audit log + 5 atletas DoD | +integration+BDD | 9.55 |

### Artefactos de código entregados

- **1 aggregate:** `Performance` con máquina de estados completa (AnunciadaAP → Llamada → Ejecutada/DNS)
- **6 domain events:** APRegistrado, AtletaLlamado, ResultadoRegistrado, TarjetaAsignada, DNSRegistrado, ResultadoCorregido
- **6 commands + handlers:** flujo completo del juez
- **1 infrastructure:** SQLiteEventStore append-only con Alembic
- **3 queries + Read Models:** PerformanceActual, ProximasPerformances, Progreso
- **5 endpoints REST:** GET /health, /events, /performance/actual, /performance/proximas, /progreso
- **9 feature files BDD** (uno por US)

---

## 2. Métricas finales

| Métrica | Objetivo SP1 | Real |
|---------|-------------|------|
| Tests totales | — | **207** (127 unit + 42 integration + 38 BDD) |
| Tests PASSING | 100% | **100%** (207/207) |
| Pylint `domain/` | ≥ 8.0 | **9.55 / 10** |
| Violations CRITICAL | 0 | **0** |
| DoD SP1 (5 performances E2E) | Binario | **✅ APROBADO** |
| UAT Capa 1 (pytest) | 7/7 | **7/7 PASSED** |
| UAT Capa 2 (HTTP real) | 4/4 | **4/4 OK** |
| Eventos en Event Store (UAT) | ≥ 15 | **20 eventos** |
| HITOs generados | — | **9** |
| ADRs registrados | — | **12** (ADR-001 a ADR-012) |

---

## 3. Estimación de esfuerzo

### Actividad por día (commits como proxy)

| Fecha | Commits | Actividad principal |
|-------|---------|---------------------|
| 2026-03-14 | 1 | Inicialización del repositorio, BL-000 |
| 2026-03-15 | 3 | Documentos fundacionales, sistema de sesión |
| 2026-03-16 | 1 | vision.md, decisión Event Storming |
| 2026-03-17 | 1 | Event Storming Big Picture |
| 2026-03-18 | 7 | ES Competencia, Context Map, ADR-005, Domain Model |
| 2026-03-19 | 6 | Architecture, cierre Fase 0, HITO-1 |
| 2026-03-20 | 24 | SP1 planificación, ADR-009 a 012, fixes consistencia |
| 2026-03-21 | 21 | Inc 1.1 walking skeleton + US-1.2.1 |
| 2026-03-22 | 10 | US-1.2.2, US-1.2.3, US-1.2.4 |
| 2026-03-23 | 19 | US-1.2.5, 1.2.6, 1.3.1, 1.4.1, 1.4.2, BL-001 |
| 2026-03-24 | 1 | UAT SP1 |
| **Total** | **94 commits** | **11 días calendario** |

### Estimación en días reales de desarrollo

| Fase | Días calendario | Días activos | Descripción |
|------|----------------|--------------|-------------|
| Fase 0 (diseño y arquitectura) | 6 (03-14 → 03-19) | 6 | Domain, ES, Context Map, 12 ADRs, Architecture |
| SP1 planificación | 1 (03-20) | 1 | ADR-009..012, candidatas, fixes documentales |
| SP1 implementación | 4 (03-21 → 03-24) | 4 | 9 USs, 207 tests, UAT |
| **TOTAL** | **11** | **11** | |

**Estimación de horas efectivas por día activo:**

Las sesiones con Claude Code son intensas pero discontinuas. Estimando carga por actividad:

| Día | Horas estimadas |
|-----|----------------|
| 03-14 a 03-17 | ~1-2h/día (setup inicial y documentos livianos) |
| 03-18 a 03-19 | ~4-5h/día (Event Storming, Domain Model, Architecture) |
| 03-20 | ~4-5h (planificación técnica + fixes) |
| 03-21 | ~5-6h (walking skeleton + primera US con /implement-us) |
| 03-22 | ~4-5h (3 USs en el segundo ciclo del Dev Kit) |
| 03-23 | ~6-7h (4 USs + BL-001 + HITOs + PRs) |
| 03-24 | ~3h (UAT diseño + ejecución + documentación) |

**Esfuerzo total estimado: 35–45 horas efectivas**

> En términos convencionales de proyecto de software, 9 USs con Event Sourcing,
> arquitectura hexagonal, 207 tests y documentación completa representarían
> 30–60 días-persona en un equipo tradicional sin asistencia IA.
> El factor de aceleración observado es aproximadamente **5x a 10x**.

### ¿Qué explica la velocidad?

1. **El Dev Kit absorbe la fricción de proceso:** cada ciclo `/implement-us` es reproducible. Una vez estabilizado (US-1.2.2), el overhead cayó de 2h a ~15min.
2. **IEDD reduce la ambigüedad:** las precondiciones, postcondiciones e invariantes formales de cada US-IEDD evitan decisiones de diseño en medio de la implementación.
3. **La arquitectura hexagonal es favorable al AI:** las capas bien separadas generan código predecible. El AI no improvisa cuando las interfaces ya están definidas.
4. **Los tests BDD como especificación ejecutable:** escribir el `.feature` antes del código obliga a concretar el comportamiento antes de implementar — reduce retrabajo.

---

## 4. Logros del experimento

### Hipótesis del experimento confirmadas/parcialmente confirmadas

| Hipótesis | Estado | Evidencia |
|-----------|--------|-----------|
| H-1: IEDD produce invariantes más completos que el análisis directo de RFs | **Confirmada parcialmente** | Los 11 invariantes (INV-P-01..P-11) emergieron del Event Storming Nivel 2, no de los RFs. En la retrospectiva (HITO-4) se observó que el dominio guiaba naturalmente la especificación. |
| H-2: El ecosistema CM + Dev Kit converge a overhead mínimo | **Confirmada** | US-1.2.1: 2h de overhead → US-1.2.2: 9min → estabilizado en ~15-18min (HITO-5, memory). |
| H-3: La arquitectura hexagonal facilita la implementación AI-asistida | **Confirmada** | DesignReviewer nunca reportó CRITICAL en código nuevo. La separación de capas fue respetada en las 10 USs sin corrección manual. |
| H-4: El conocimiento se capitaliza directamente en artefactos académicos | **Parcialmente** | 9 HITOs generados directamente del desarrollo. Requieren edición para publicación pero la sustancia está capturada. |

### Logros técnicos destacados

- **Aggregate Performance** con máquina de estados completa e invariantes formales — el núcleo del Core Domain, sin deuda técnica en SP1.
- **Event Sourcing funcional** desde SP1: el Event Store serializa, ordena y proyecta eventos sin ORM ni framework externo — solo SQLite + aiosqlite.
- **Cobertura 100% del flujo del juez** via tests automatizados: cada estado, transición e invariante tiene al menos un test unitario, uno de integración y un escenario BDD.
- **UAT con evidencia versionada:** `tests/uat/` + `quality/reports/uat/` establecen el patrón para SP2-SP5.

---

## 5. Aprendizajes clave (HITOs)

| HITO | Aprendizaje | Impacto en el proyecto |
|------|-------------|----------------------|
| HITO-1 | IEDD Fase 0: la metodología sobrevive el contacto con un proyecto real, con desvíos menores | Validó la secuencia de capas; el ES Big Picture y el ES Competencia produjeron los BCs correctos |
| HITO-2 | Stack técnico y consistencia documental: los ADRs no son burocracia, son anclas de decisión | Evitó 3 debates recurrentes de "¿por qué SQLite?" en cada US |
| HITO-3 | Inc 1.1 walking skeleton: la infraestructura primero desbloquea todas las USs del dominio | El EventStorePort estuvo listo antes que el primer aggregate |
| HITO-4 | Primer ciclo `/implement-us`: alto costo de setup, pero la 10-fase structure funciona | 2h → 9min en el segundo ciclo; el framework es inversión, no overhead permanente |
| HITO-5 | Segundo ciclo: el Dev Kit estabilizado es predecible y reproducible | Permitió hacer 4 USs en un solo día (03-23) |
| HITO-6 | BDD × Event Sourcing: la fricción es real pero manejable con step definitions explícitas | Los 38 escenarios BDD están pasando; pytest-bdd requiere cuidado con el contexto de pasos |
| HITO-7 | Fiabilidad del AI en protocolos estructurados: el AI es preciso cuando las pre/postcondiciones son formales | Las USs IEDD con invariantes explícitos generan implementaciones correctas en el primer intento |
| HITO-8 | Degradación silenciosa de artefactos por compresión de contexto: el AI puede "recordar" haber hecho algo sin haberlo hecho | Gate explícito en Phase 7 y Phase 9 del Dev Kit para verificar existencia real en disco |
| HITO-9 | UAT híbrido cuando no hay endpoints POST: pytest + seed script + HTTP GET es evidencia formal suficiente | Patrón establecido para SP1; SP2 podrá usar flujo HTTP completo |

---

## 6. Deuda técnica identificada para SP2

| Ítem | Prioridad | Descripción |
|------|-----------|-------------|
| DIP en router.py | Alta | `SQLiteEventStore` instanciado directamente en `get_event_store()` — viola DIP. Refactorizar a puerto abstracto. |
| OCP en `_apply_stored` de Performance | Media | Switch por tipo de evento — cada nuevo evento requiere modificar el método. Refactorizar a tabla de dispatch. |
| StubCompetenciaEstadoAdapter | Media | Puerto informal sin interfaz explícita. Formalizar como `CompetenciaEstadoPort` antes de SP2. |
| Endpoints POST no expuestos | — | No es deuda — es diseño de SP1. Los comandos se exponen en SP2. |

---

## 7. Próximo paso inmediato

Cierre formal de SP1:
1. `git checkout main && git merge develop --no-ff`
2. `git tag v0.2.0`
3. Cerrar Milestone SP1 en GitHub

---

*Generado: 2026-03-24 — Al completar UAT SP1 y antes del tag v0.2.0*
