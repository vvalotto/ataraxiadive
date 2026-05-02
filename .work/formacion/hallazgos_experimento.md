# Hallazgos del Experimento AtaraxiaDive
## Fortalezas, debilidades y aspectos en evaluación

*Víctor Valotto — Abril 2026 | Base: SP1–SP4 completados (v0.2.0–v0.5.0)*

---

> Este documento sintetiza los hallazgos del experimento AtaraxiaDive al cierre de SP4.
> Se organiza en tres categorías: hallazgos positivos con evidencia, hallazgos negativos
> con evidencia, y aspectos que continúan en evaluación. Es material primario para la
> propuesta de formación y para el paper IEDD.

---

## 1. Hallazgos positivos — Fortalezas

### F-01 — El flujo agentic integrado funciona

El entorno completo (IEDD + Claude Dev Kit + Software Limpio) operó como sistema integrado
durante cuatro subproyectos consecutivos sin fricciones insalvables entre herramientas.
Cada herramienta cumplió su rol sin anular las otras. Esa integración no estaba garantizada
al inicio del experimento: era la primera hipótesis que se quería descartar.

**Evidencia:** BL-001 a BL-004 — cuatro ciclos completos con artefactos trazables por fase.

---

### F-02 — Overhead del flujo convergido y estable (~18 min/US)

El tiempo de ejecución por historia de usuario con `/implement-us` (10 fases completas)
convergió a aproximadamente 18 minutos tras los primeros dos o tres ciclos y se mantuvo
estable durante los sprints siguientes. La curva de aprendizaje existe y es corta.

**Evidencia:** HITO-4, HITO-5 (SP1). Confirmado en SP2 (retrospectiva BL-002).

---

### F-03 — Velocidad real vs. estimación propia: factor 6–9x

El PLAN-EXPERIMENTO (2026-03-14) proyectó 6-9 meses para completar los Horizontes 1 y 2
(SP1-SP4). El tiempo real fue aproximadamente 31 días calendarios:

| SP | Apertura | Cierre | Días |
|----|----------|--------|------|
| SP1 | 2026-03-21 | 2026-03-24 | 3 |
| SP2 + SP-ADJ-01 | 2026-03-20 | 2026-03-28 | 8 |
| SP3 + SP-ADJ-03/04 | 2026-03-29 | 2026-04-04 | 6 |
| SP4 + SP-ADJ-06 | 2026-04-04 | 2026-04-18 | 14 |
| **Total SP1–SP4** | | | **~31 días** |

No existe grupo de control externo, pero la brecha entre la estimación del propio autor
—hecha sin el método operativo— y la ejecución real es evidencia interna significativa.
El factor de compresión estimado es 6-9x.

**Evidencia:** PLAN-EXPERIMENTO (2026-03-14) vs. fechas de apertura/cierre en BL-001 a BL-004.

---

### F-04 — Cero violaciones críticas de diseño desde SP2

El DesignReviewer no registró ninguna violación CRITICAL desde el cierre de BL-002 en adelante.
Los 119 warnings en BL-003 y los 174 en BL-004 son conocidos, analizados y aceptados: métodos
largos en handlers hexagonales (patrón DDD), adapters de Event Sourcing, feature envy estructural
entre capas hexagonales. Ninguno señala deuda arquitectónica real.

**Evidencia:** Reportes DesignReviewer en `quality/reports/designreviewer/` — SP-ADJ-04-report.txt (BL-003), INC-4.6-report.txt (BL-004). El indicador `should_block=False` sostenido en todos los análisis ArchitectAnalyst.

---

### F-05 — 952 tests al 100% — cobertura domain/application > 90%

El sistema cierra SP4 con 952 tests pasando al 100%, cobertura mayor a 90% en las capas
de dominio y aplicación (las únicas que la metodología considera críticas de cubrir),
y sin ningún test ignorado o marcado como skip por conveniencia.

**Evidencia:** BL-004 métricas de tests. BL-003: 785 tests, 100%. BL-002: 481 tests, 100%.

---

### F-06 — SP-ADJ como patrón formal de gestión de deuda técnica

Formalizar la deuda técnica post-sprint en un sub-sprint propio (en lugar de ignorarla
o dispersarla en el backlog) resultó efectivo y reproducible. El patrón se validó en
cuatro instancias: SP-ADJ-01, SP-ADJ-02, SP-ADJ-03, SP-ADJ-04, SP-ADJ-06.
Cada SP-ADJ cerró con cero CRITICAL y mejoró métricas respecto al estado previo.

**Evidencia:** HITO-13 (SP2). Retrospectivas en BL-002, BL-003, BL-004.

---

### F-07 — Los quality gates funcionan como dispositivos de reflexión de diseño

El DesignReviewer no fue solo un detector de violaciones: en varios incrementos derivó
en decisiones de diseño que no estaban planificadas. El gate detuvo una violación DIP
real antes de llegar a main (BL-002) y generó la discusión que llevó a rediseñar
la dependencia entre BCs.

**Evidencia:** HITO-11 (SP2 — "Quality gate como catalizador de decisión arquitectónica").

---

### F-08 — Dataset real como oráculo empírico del dominio

El dataset del torneo Buenos Aires 2025 (30 atletas, 145 entradas) actuó como oráculo
empírico y reveló 10 discrepancias entre el modelo especificado y el comportamiento real
del deporte — 6 de las cuales se corrigieron antes de cerrar BL-003. El análisis teórico
previo no había detectado ninguna de ellas.

**Evidencia:** HITO-17 (SP3). SP-ADJ-04 — 6 US de correcciones de dominio real. UAT SP3: 6 RPs coinciden 100% con resultados oficiales del evento.

---

### F-09 — Trazabilidad completa dominio → especificación → código → tests

Existe una cadena trazable desde cada requisito funcional hasta los tests que lo verifican,
pasando por la US-IEDD y el plan de implementación. La traceability matrix (`docs/traceability/matrix.md`)
se mantuvo actualizada a lo largo de los 4 sprints.

**Evidencia:** `docs/traceability/matrix.md` — ~50 US trazadas al cierre de SP4.

---

### F-10 — UAT ejecutado con dispositivos físicos y datos reales

El UAT de SP4 no usó datos sintéticos ni simulados. Se ejecutó con el dataset Buenos Aires 2025
sobre dispositivos físicos: iPhone (juez offline-first), iPad (organizador/auditoría), Mac (API).
Tres flujos validados: offline-first con sincronización, email real vía Resend, auditoría con hash SHA-256.

**Evidencia:** BL-004 UAT. Evidencias en `quality/reports/uat/SP4/`.

---

### F-11 — La secuencialidad del método es parte del método, no una preferencia

La linealidad del pipeline `/implement-us` y del tracker de fases no es una restricción
operativa: es un mecanismo de verificación. Saltar fases o ejecutarlas fuera de orden
produce lagunas en los artefactos que no son visibles hasta que otra herramienta
del entorno las detecta.

**Evidencia:** HITO-16, HITO-21 (SP3, SP4).

---

### F-12 — Event Sourcing como base de integridad criptográfica sin persistencia adicional

La misma traza de eventos que soporta el flujo del juez puede sostener auditoría legible
e integridad verificable (hash SHA-256 encadenado) sin almacenamiento paralelo.
El Event Sourcing no es solo una elección de persistencia: es la fuente de verdad
sobre la que se construyen read models de auditoría y exportación portable.

**Evidencia:** HITO-22, HITO-23, HITO-24 (SP4 INC-4.6).

---

## 2. Hallazgos negativos — Debilidades

### D-01 — Sin grupo de control externo

No hay comparación sistemática con un equipo desarrollando el mismo sistema sin
el método. La velocidad, la calidad y la deuda técnica solo pueden evaluarse en
relación al propio experimento o a estimaciones del autor. Esto limita la capacidad
de generalizar los resultados con rigor científico.

**Impacto:** Los datos del experimento son evidencia interna, no externa.
Comparaciones con "desarrollo convencional" no están respaldadas por el experimento.

---

### D-02 — Proyecto unipersonal — no validado en equipo

Todo el experimento fue ejecutado por un solo desarrollador. No hay datos sobre
cómo el método escala cuando múltiples personas trabajan en el mismo codebase,
cuando hay conflictos de especificación entre desarrolladores, o cuando el overhead
del proceso se distribuye y se negocia.

**Impacto:** La extrapolación a equipos requiere un experimento separado.
El material de formación debe ser honesto sobre este límite.

---

### D-03 — Gates de texto no son barreras reales para LLMs

Las instrucciones procedurales en lenguaje natural no garantizan adherencia del LLM.
El modelo puede ignorar o saltear fases aunque estén explícitamente prohibidas en el
prompt de sistema. Las restricciones efectivas son las de herramienta (el tracker que
bloquea la fase siguiente), no las de texto.

**Evidencia:** HITO-12 (SP2 — "Gates de texto vs. constraints de herramienta").

---

### D-04 — Compresión de contexto del LLM degrada completitud de artefactos

En sesiones largas o con muchas herramientas activas, el LLM tiende a omitir artefactos
que en sesiones más cortas genera completos. La compresión de contexto produce
lagunas silenciosas que no son detectadas por el propio proceso hasta que otro mecanismo
las busca explícitamente.

**Evidencia:** HITO-8 (SP1 INC-1.3 — "Artefactos faltantes por compresión de contexto").

---

### D-05 — Script UAT frágil — prerequisitos sin documentar

El script de UAT de SP3 requirió tres correcciones durante la ejecución formal
(JWT, URL inscriptos, transición de estado). El prerequisito de arranque del servidor
(`IDENTIDAD_JWT_SECRET`) no estaba documentado. El UAT formal debe ejecutarse en
un entorno limpio y con un runbook validado antes de la sesión formal.

**Evidencia:** Retrospectiva BL-003 — "Qué mejorar".

---

### D-06 — Discrepancias de dominio que sobreviven a toda la especificación formal

El dataset real reveló errores de modelo que el Event Storming, los ADRs, las US-IEDD
y los tests no habían detectado. La especificación formal reduce el espacio de error
pero no lo elimina: algunas discrepancias solo se revelan con datos del mundo real.

**Evidencia:** HITO-17 (SP3). Del dataset BA 2025 quedaron 4 discrepancias sin resolver
al cerrar BL-003 (DISC-03, DISC-09, DISC-10 y otras).

---

### D-07 — Calibración de thresholds del DesignReviewer por sprint, no universal

Los umbrales de CBO/WMC del DesignReviewer no son universales: deben calibrarse
al inicio de cada sprint según la arquitectura y el patrón dominante del incremento.
Calibrarlos US por US genera inconsistencias y confusión sobre qué es una violación real
y qué es un falso positivo aceptado.

**Evidencia:** Retrospectiva BL-002. Feedback en `memory/feedback_designreviewer_cbo_wmc_policy.md`.

---

### D-08 — Stack Python exclusivo — los principios son transferibles, las herramientas no

Las implementaciones de referencia (Claude Dev Kit, Software Limpio) están construidas
para Python. Los principios que las fundan —especificación formal, flujo agentic estructurado,
quality gates por nivel— son independientes del stack, pero la evidencia empírica directa
existe solo para Python. Equipos con otros stacks deben adaptar sin la misma base de datos.

**Impacto:** La formación puede enseñar principios transferibles, pero no puede entregar
las herramientas listas para usar en Java, Node, Go o Rust.

---

## 3. Aspectos en evaluación

### E-01 — Extrapolación del método a equipos

La hipótesis de que IEDD + flujo agentic produce los mismos resultados en un equipo
de 3-8 personas no tiene evidencia. Las variables que cambian en equipo son sustanciales:
conflictos de especificación, revisión de PRs entre personas, distribución del overhead
de proceso, coordinación de los quality gates, y negociación de umbrales.

**Estado:** Sin datos. Requiere un segundo experimento con equipo real.

---

### E-02 — Sostenibilidad del método en proyectos de mayor escala

AtaraxiaDive tiene ~50 US-IEDD, 6 Bounded Contexts, y un desarrollador. No hay datos
sobre cómo evoluciona el overhead del proceso cuando el sistema tiene 200 US, 20 BCs,
y el codebase supera las 100.000 líneas. Los patrones de acoplamiento y los quality gates
pueden comportarse diferente a escala.

**Estado:** Sin datos. ArchitectAnalyst tendencias disponibles en BL-001 a BL-004,
pero la proyección a proyectos enterprise es especulativa.

---

### E-03 — Comparación IEDD vs. especificación convencional: ¿mejora real?

La hipótesis de que las US-IEDD con invariantes formales producen menos defectos
que las US clásicas es la pregunta central del experimento. Hay evidencia interna
(los quality gates detectaron menos violaciones en US bien especificadas), pero no
hay comparación sistemática con US clásicas en el mismo proyecto. La hipótesis
sigue siendo plausible, no demostrada.

**Estado:** En evaluación. Datos parciales en HITO-1, HITO-4, HITO-6.
Se necesita un protocolo de comparación explícito para afirmarlo con rigor.

---

### E-04 — Capitalización del conocimiento producido sin reescritura

La hipótesis de que el conocimiento generado durante el desarrollo (ADRs, HITOs,
retrospectivas, specs) puede capitalizarse directamente en material académico
sin reescribir desde cero está parcialmente validada: los HITOs tienen estructura
de paper, los ADRs tienen estructura de caso de estudio. Pero la capitalización
efectiva depende del tiempo y la energía disponibles para el ensamblaje.

**Estado:** En evaluación. 25 HITOs documentados al cierre de SP4.
El paper IEDD y los capítulos del libro están diseñados para usar estos artefactos,
pero el ensamblaje final no se ha ejecutado todavía.

---

### E-05 — Fricción real de coordinación entre herramientas del entorno

La hipótesis RQ1 del experimento pregunta si el ecosistema integrado genera fricción
de coordinación que anule parte del valor. La respuesta al cierre de SP4 es: la fricción
existe (HITO-8, HITO-12, D-05), pero no es insalvable. No hay una métrica objetiva
que cuantifique qué porcentaje del overhead total corresponde a fricción del entorno
vs. complejidad inherente del dominio.

**Estado:** En evaluación continua. HITO-4 a HITO-8 documentan la fricción observada.
La cuantificación precisa requiere un protocolo de medición separado.

---

## Síntesis ejecutiva

| Categoría | Cantidad | Indicador clave |
|-----------|:--------:|-----------------|
| Fortalezas con evidencia | 12 | F-03 (6-9x velocidad), F-04 (0 CRITICAL sostenido), F-05 (952 tests 100%) |
| Debilidades con evidencia | 8 | D-01 (sin control externo), D-02 (unipersonal), D-03 (gates de texto) |
| En evaluación | 5 | E-01 (equipos), E-03 (IEDD vs. convencional), E-05 (fricción) |

El experimento cerró SP4 con una base empírica sólida para un solo desarrollador
en un sistema de complejidad media. Las fortalezas son reales y medibles. Las debilidades
son honestas y conocidas. Los aspectos en evaluación son preguntas abiertas, no fracasos:
un experimento que cierra todas sus hipótesis no fue lo suficientemente ambicioso.

---

*Generado: 2026-04-19 — Base: SP1–SP4 (BL-001 a BL-004), HITOs 1-24, retrospectivas*
*Próxima actualización: al cierre de SP5 (BL-005)*
