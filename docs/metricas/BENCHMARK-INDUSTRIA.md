# Benchmark de Industria — AtaraxiaDive vs. Contexto Comparable

> Estado documental: vigente
> Compara las métricas de `REPORTE-METRICAS.md` (estado v1.0.5, cierre del proyecto) contra
> benchmarks de industria — clasificando primero el tipo de aplicación para elegir un contexto
> de comparación válido, en vez de comparar contra "la industria" en general.
> Fecha: 2026-08-13

---

## 1. Por qué clasificar antes de comparar

Comparar métricas de software sin fijar primero el contexto es un error metodológico común: la
cobertura de tests esperada de un sistema de trading no es la de un blog, y la velocidad de
entrega de un equipo de 8 personas no es la de un desarrollador solo. Antes de citar un solo
número de industria, este documento fija las 5 dimensiones que determinan qué benchmark aplica.

---

## 2. Clasificación de AtaraxiaDive

| Dimensión | Clasificación | Por qué importa |
|---|---|---|
| **Tipo de aplicación** | Sistema de información de gestión (MIS) — "vertical SaaS" de administración de eventos deportivos | Determina el benchmark de defectos/cobertura aplicable — no es embebido, no es tiempo-real crítico, no es científico/data-intensive |
| **Nivel de riesgo/criticidad** | Bajo-medio — deporte amateur/competitivo, sin datos de pago ni datos médicos sensibles | Excluye los benchmarks de fintech/healthcare (85–95% cobertura exigida); aplica el rango de "aplicación de negocio estándar" (70–90%) |
| **Arquitectura/stack** | Monolito modular (6 Bounded Contexts), Hexagonal + Event Sourcing parcial, API REST (FastAPI/Python) + SPA/PWA (React/TypeScript) | Stack "web moderno" típico — comparable a benchmarks de proyectos backend+frontend actuales, no a sistemas legacy (COBOL, mainframe) |
| **Escala** | ~29 027 SLOC totales (13 259 backend + 15 768 frontend) | En términos COCOMO: proyecto **pequeño** (categoría "Organic", <50K SLOC) — el rango de benchmark más laxo, no el de proyectos "Semidetached"/"Embedded" de gran escala |
| **Equipo** | 1 desarrollador humano + asistencia de IA (par no convencional) | **La mayor desviación respecto a los benchmarks disponibles** — ISBSG, DORA y la mayoría de encuestas de productividad están calibrados sobre equipos de 3–9 personas. Se marca explícitamente en cada comparación de productividad. |
| **Metodología** | Ágil incremental con especificación formal por historia (IEDD) | Comparable a benchmarks de "equipos ágiles de alto desempeño", no a waterfall |

**Contexto de comparación resultante:** *proyecto pequeño de aplicación de negocio web moderna
(MIS/vertical SaaS), riesgo bajo-medio, desarrollado por un equipo atípicamente pequeño con
asistencia de IA.* Los benchmarks se eligieron para calzar con esta clasificación — no se usó
ningún benchmark de sistemas embebidos, fintech/healthcare, ni proyectos de gran escala.

---

## 3. Fuentes de benchmark utilizadas

| Fuente | Qué mide | Aplicabilidad a AtaraxiaDive |
|---|---|---|
| **ISBSG** (International Software Benchmarking Standards Group) | Productividad, +11 000 proyectos, por tipo de aplicación y tamaño de equipo | Base de referencia estándar para proyectos MIS/business application |
| **Capers Jones** (Software Assessments, Benchmarks and Best Practices) | Densidad de defectos por function point, por tipo de sistema | ~5 defectos/FP promedio EE.UU., 85% removidos antes de entrega → ~0.75 defectos entregados/FP |
| **Encuestas de cobertura de tests** (industria, agregadas de múltiples fuentes 2024-2025) | % cobertura por nivel de riesgo de aplicación | 70–90% aplicaciones de negocio estándar · 85–95% crítico/regulado · 60–75% herramientas internas de bajo riesgo |
| **McCabe / escala estándar de Complejidad Ciclomática** | Umbrales de riesgo por CC | 1–10 bajo riesgo · 11–20 moderado · 21–50 alto riesgo · 50+ intestable |
| **Maintainability Index** (Microsoft/radon, escala 0–100) | Umbrales de mantenibilidad | ≥20 verde/mantenible · 10–19 amarillo/alerta · <10 rojo/crítico |
| **SonarQube — convención de industria para duplicación** | % duplicación de código | <3% excelente · 3–5% aceptable · 5–10% alerta · >10% crítico |
| **Standish Group CHAOS Report** | Éxito de proyectos, no rework directo | Referencia contextual — sin cifra de "% rework típico" confiable; se usa el rango DeMarco/Lister (30–80% retrabajo) ya citado en `CONCLUSIONES-IEDD.md` como la mejor referencia disponible |
| **GitHub Copilot — estudios de productividad con IA** (2025) | Velocidad con asistencia de IA vs. baseline | 55% más rápido en completar tareas · ciclo de PR 9.6→2.4 días (−75%) · 30–60% ahorro de tiempo en código/tests/docs |

---

## 4. Comparación de Calidad

| Métrica | AtaraxiaDive v1.0.5 | Benchmark de industria (contexto: MIS/negocio, riesgo bajo-medio) | Posición |
|---|:---:|---|:---:|
| **Cobertura de tests** | 94.7% global (95.35% sin código muerto) | 70–90% aplicación de negocio estándar | ✅ **Por encima del rango típico** — se acerca al piso del rango exigido a sistemas críticos (85–95%) sin serlo |
| **Defectos estimados** (Halstead, proxy) | 0.297 / 1 000 SLOC | Capers Jones: ~5 defectos/function point entregados a razón de ~0.75/FP tras remoción — la conversión SLOC↔FP depende del lenguaje, pero incluso con supuestos conservadores (Python: ~1 FP ≈ 40–50 SLOC) el proxy de AtaraxiaDive equivale a un orden de magnitud **por debajo** del promedio EE.UU. | ✅ **Muy por debajo del promedio** — coherente con la alta cobertura de tests |
| **Complejidad Ciclomática** (domain/) | 1.86 promedio | 1–10 = bajo riesgo (McCabe) | ✅ **Muy por debajo del umbral de riesgo** — el sistema completo (peor capa: infra 2.17) sigue firmemente en "bajo riesgo" |
| **Índice de Mantenibilidad** (domain/) | 88.02 / 100 | ≥20 = verde/mantenible | ✅ **4.4× el umbral mínimo** — la capa más débil (api/, 68.69) sigue en zona verde |
| **Duplicación de código** (frontend) | 4.05% | <3% excelente · 3–5% aceptable · 5–10% alerta | ⚠️ **Dentro del rango aceptable, pero no excelente** — más cerca del límite superior (5%) que del piso |
| **Cohesión OO (LCOM > 1)** | 3.2% de clases | Sin benchmark de industria estandarizado con esta forma exacta — se usa < 10% como referencia razonable derivada de prácticas comunes de code review | ✅ **Bien por debajo de una referencia razonable** |
| **Quality gates bloqueantes (CRITICAL)** | 0 en toda la historia del proyecto (793 commits, 193 PRs) | Sin benchmark cuantitativo estándar — referencia cualitativa: proyectos con gates bien calibrados reportan tasas de bloqueo bajas pero no nulas | ℹ️ Dato fuerte pero sin comparación numérica de industria disponible |

**Lectura de conjunto:** en **5 de 6 métricas de calidad con benchmark cuantificable**,
AtaraxiaDive está por encima o muy por encima del contexto comparable (MIS/negocio, riesgo
bajo-medio). La única métrica en zona "aceptable pero no excelente" es la duplicación de código
frontend (4.05%, banda 3-5%) — consistente con el hallazgo ya documentado en
`frontend-duplicacion.md` de que los API clients repiten un patrón técnico de fetch sin
abstracción compartida.

---

## 5. Comparación de Productividad

> **Advertencia metodológica, antes de leer esta sección:** los benchmarks de productividad de
> industria (ISBSG, DORA, encuestas de velocidad ágil) están calibrados sobre **equipos de 3–9
> personas**. AtaraxiaDive fue construido por **1 desarrollador + asistencia de IA**. Comparar
> directamente "US/día de AtaraxiaDive" contra "story points/sprint de un equipo típico" no es
> una comparación de manzanas con manzanas — se normaliza por desarrollador donde es posible, y
> se marca explícitamente donde no.

| Métrica | AtaraxiaDive (fase de construcción, SP1–SP6) | Benchmark de industria | Posición |
|---|:---:|---|:---:|
| **Velocidad con asistencia de IA** | Ritmo de crucero 1.5 US func./día (~20 min/US mediana, pipeline de 10 fases) | Copilot (2025): +55% velocidad de tarea, ciclo de PR −75% (9.6→2.4 días), 30–60% ahorro de tiempo en código/tests/docs | ⚠️ **El +55%–75% de Copilot es la referencia más comparable, y es sustancialmente menor que el "3x–10x" citado en `CONCLUSIONES-IEDD.md`** — ver nota crítica abajo |
| **Ratio de retrabajo formalizado (SP-ADJ)** | 60% (SP1–SP6) — 0.60 US de ajuste por US funcional | Sin cifra de industria confiable y comparable directamente; DeMarco/Lister estiman 30–80% de esfuerzo total en retrabajo en proyectos tradicionales (cifra no formalizada como SP-ADJ, generalmente invisible en el reporte de horas) | ℹ️ **Dentro del rango citado, pero la comparación es débil** — son unidades distintas (US formalizadas vs. % de esfuerzo estimado) |
| **Tasa de éxito de entrega** | 100% de SPs cerrados según plan (7/7), 0 abandono, 0 cancelación | Standish CHAOS: ~31% de proyectos "exitosos" (a tiempo, en presupuesto, alcance completo), ~50% "desafiados", ~19% fallidos | ✅ **Muy por encima** — aunque un proyecto de 1 persona sin stakeholders externos no enfrenta las mismas presiones que motivan la mayoría de las fallas del CHAOS Report (alcance cambiante multi-stakeholder, dependencias organizacionales) |
| **Cobertura de tracking de tiempo** | 26% de las US (34/131) | Sin benchmark de industria — es una métrica interna del proyecto, no comparable externamente | — No aplica |

### Nota crítica — el claim "3x–10x" necesita ajuste

`CONCLUSIONES-IEDD.md §4.1` cita un ratio implícito de 3x–5x a 6x–12x sobre un desarrollador
senior sin IA, derivado de una estimación *ad hoc* (2–4 h/US tradicional vs. 20 min/US medido).
Los estudios de industria más rigurosos sobre asistencia de IA (Copilot, 2025, muestra
longitudinal con equipos reales) miden **+55% de velocidad de tarea** y **reducción del 75% en
ciclo de PR** — órdenes de magnitud más conservadores que "3x–10x".

**La discrepancia no invalida el hallazgo de AtaraxiaDive, pero cambia lo que se puede afirmar:**

1. El pipeline IEDD no es solo "autocompletado asistido" (que es lo que miden los estudios de
   Copilot) — incluye especificación formal (precondición/postcondición/invariantes) generada
   con asistencia de IA, tests generados, y una revisión automatizada de diseño (DesignReviewer)
   en cada commit. Es un proceso más integral que "sugerencias de código en el editor", por lo
   que un múltiplo mayor no es descabellado.
2. Pero el "2–4 h/US" usado como baseline humano es una **estimación, no una medición** —
   mientras que el estudio Copilot 2025 mide contra un baseline real medido de otros
   desarrolladores humanos. **El "3x–10x" de AtaraxiaDive tiene menos rigor metodológico que el
   "+55%" de la industria.**
3. **Recomendación para el paper:** presentar el ratio 3x–10x como *hipótesis derivada de
   estimación interna*, con el +55%/−75% de Copilot como *piso conservador con evidencia externa
   más sólida* — no promediarlos ni presentar solo el número más favorable.

---

## 6. Síntesis — dónde AtaraxiaDive está por encima, en línea, o por debajo del contexto comparable

| Categoría | Resultado |
|---|:---:|
| Cobertura de tests | ✅ Por encima |
| Defectos estimados | ✅ Muy por encima (mejor) |
| Complejidad / Mantenibilidad | ✅ Muy por encima (mejor) |
| Duplicación de código | ⚠️ En el límite aceptable |
| Tasa de bloqueo de gates | ℹ️ Sin comparación cuantitativa disponible |
| Velocidad vs. baseline IA (Copilot) | ⚠️ **Claim propio 5-15x más optimista que la evidencia externa más rigurosa** |
| Retrabajo formalizado (SP-ADJ) | ℹ️ Dentro de rango citado, pero comparación metodológicamente débil |
| Tasa de éxito de entrega | ✅ Muy por encima (con caveat de escala) |

**Conclusión general:** en las métricas de **calidad de código** (que sí tienen benchmarks
cuantitativos sólidos y aplicables al contexto MIS/negocio de riesgo bajo-medio), AtaraxiaDive
está consistentemente por encima del promedio de industria. En las métricas de **productividad**,
el proyecto también se ve favorable, pero la comparación es estructuralmente más débil: faltan
benchmarks de industria calibrados para "1 desarrollador + IA" (la categoría de equipo más
atípica de todo el experimento), y el claim más citable del proyecto (3x-10x) usa una
metodología de estimación menos rigurosa que la evidencia externa disponible (Copilot, +55%).
**Para el paper, se recomienda liderar con las métricas de calidad (evidencia sólida) y presentar
las de productividad con el ajuste de expectativas de esta sección.**

---

## 7. Limitaciones de esta comparación

1. **N=1 proyecto, N=1 desarrollador.** Ningún benchmark de industria fue calibrado sobre esta
   configuración exacta — todas las comparaciones de productividad requieren normalización o
   interpretación cualitativa.
2. **Conversión SLOC↔Function Point es aproximada.** El benchmark de Capers Jones usa function
   points, no SLOC; la conversión depende del lenguaje y del estilo de codificación, así que la
   comparación de defectos es direccional, no exacta.
3. **Sin grupo de control contemporáneo.** No existe una versión de AtaraxiaDive construida sin
   IEDD/IA para comparar directamente — todas las comparaciones son contra benchmarks externos de
   otros proyectos, no contra un control interno.
4. **Los benchmarks de industria citados agregan datos de múltiples fuentes/años**, no de un
   único estudio longitudinal — se priorizaron fuentes con metodología explícita y trazable
   (ISBSG, Capers Jones, SonarQube, McCabe, Copilot 2025) sobre cifras sueltas sin fuente.

---

## Sources

- [ISBSG — International Software Benchmarking Standards Group](https://www.isbsg.org/resources-productivity/)
- [ISBSG — Benchmarking resources](https://www.isbsg.org/resources-benchmarking/)
- [Capers Jones — Sources of Software Benchmarks](https://insights.cermacademy.com/14-sources-of-software-benchmarks-c-capers-jones-2/)
- [Capers Jones — Software Assessments, Benchmarks, and Best Practices](https://books.google.com/books/about/Software_Assessments_Benchmarks_and_Best.html?id=2sAvWFjZeVEC)
- [KPI Depot — Test Coverage KPI Definition, Formula, & Benchmarks](https://kpidepot.com/kpi/test-coverage)
- [TechTarget — What unit test coverage percentage should teams aim for?](https://www.techtarget.com/searchsoftwarequality/tip/What-unit-test-coverage-percentage-should-teams-aim-for)
- [LinearB — Cyclomatic Complexity explained](https://linearb.io/blog/cyclomatic-complexity)
- [Microsoft Learn — Maintainability index range and meaning](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-maintainability-index-range-and-meaning?view=visualstudio)
- [KPI Depot — Code Duplication Index](https://kpidepot.com/kpi/code-duplication-index)
- [Sonar Community — Duplicate Code Threshold](https://community.sonarsource.com/t/duplicate-code-threshold/46854)
- [Standish Group — CHAOS Report / Project Resolution Benchmark](https://www.standishgroup.com/products/project-resolution-benchmark)
- [arXiv — Developer Productivity With and Without GitHub Copilot: A Longitudinal Mixed-Methods Case Study](https://arxiv.org/html/2509.20353v2)
- [GitClear — AI Assistant Code Quality 2025 Research](https://www.gitclear.com/ai_assistant_code_quality_2025_research)

---

*Generado: 2026-08-13 — comparación de `REPORTE-METRICAS.md` (v1.0.5) contra benchmarks de industria clasificados por contexto*
