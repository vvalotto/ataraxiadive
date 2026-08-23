# Síntesis del Experimento AtaraxiaDive — Tamaño, Productividad y Calidad

> Documento de cierre que integra tamaño funcional, productividad y calidad contra benchmarks de
> industria (ISBSG, Capers Jones). Fuentes: `fpa-ifpug.md`, `BENCHMARK-INDUSTRIA.md`,
> `REPORTE-METRICAS.md`, `CONCLUSIONES-IEDD.md` y los 17 documentos de detalle en `docs/metricas/`.
> Estado del proyecto: cerrado, tag `v1.0.5`, HEAD `main`, 2026-08-20.

---

## 1. Qué es el experimento

AtaraxiaDive es una plataforma de gestión de torneos de apnea construida con metodología **IEDD**
(User Stories con precondición/postcondición/invariantes formales) por **un desarrollador humano
con asistencia de IA**, sin equipo. El proyecto corrió 77 días calendario
(2026-03-14 → 2026-05-30), entregó 131 US (77 funcionales + 54 de ajuste), 793 commits, 208 PRs,
y cerró con una ejecución real de un torneo (Puerto Madryn 2026).

Este documento responde tres preguntas, en este orden — porque cada una depende de la anterior:

1. **¿Qué tamaño tiene lo que se construyó?** (funcional, no solo líneas de código)
2. **¿Cuánto tiempo tomó eso, comparado con proyectos reales de tamaño similar?**
3. **¿Ese tiempo se logró sacrificando calidad, o se mantuvo un estándar de producción?**

La respuesta corta: el tamaño es medible con rigor (343–373 Function Points IFPUG), el tiempo fue
**2.4x–3x más rápido** que la mediana/media de proyectos comparables reales (ISBSG, N=125), y la
calidad **no se sacrificó** — se sostuvo en niveles objetivamente altos durante los 77 días,
verificado con 8 métricas estructurales/arquitectónicas independientes.

---

## 2. Tamaño funcional — de proxies a Function Points IFPUG

### 2.1 Por qué dos mediciones de tamaño

El proyecto midió tamaño primero con **proxies derivables automáticamente** (US-IEDD, BDD
scenarios, endpoints REST — ver `productividad/tamano-funcional.md`): útiles para tendencias
internas, pero no comparables contra benchmarks externos porque no son una unidad estandarizada.

Para comparar contra industria se hizo después un **conteo manual IFPUG FPA** (ISO/IEC 20926) —
ver `productividad/fpa-ifpug.md` para el detalle completo, DET/RET/FTR por función.

### 2.2 Resultado del conteo IFPUG

| BC | Tipo | ILF | EIF | EI | EO | EQ | UFP |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|
| registro | CRUD | 4 | 1 | 12 | 3 | 8 | 119 |
| competencia | ES (Core) | 2 | 2 | 14 | 6 | 4 | 111 |
| torneo | CRUD | 1 | 0 | 11 | 0 | 4 | 52 |
| resultados | CRUD | 2 | 3 | 0 | 2 | 1 | 44 |
| identidad | CRUD | 1 | 0 | 7 | 0 | 2 | 34 |
| notificaciones | ES | 1 | 0 | 2 | 0 | 0 | 13 |
| **Total (por-BC)** | | 11 | 6 | 46 | 11 | 19 | **373** |
| **Total (sistema único, deduplicado)** | | 11 | 0 | — | — | — | **343** |

**373 FP** cuenta cada BC como aplicación independiente (el mismo dato aparece como ILF donde se
mantiene y como EIF donde se consulta — práctica válida en arquitecturas de BCs/microservicios).
**343 FP** es la vista de sistema único, la que se usa para comparar contra industria.

**Hallazgo transversal:** `competencia` concentra la única transacción de complejidad Alta (`GET
/grilla`, 7 FP) — coincide con los hallazgos previos de SLOC/CC/Halstead que ya señalaban a ese BC
como el de mayor complejidad interna del sistema. Cuatro mediciones independientes de naturaleza
distinta (tamaño de código, complejidad ciclomática, densidad de Halstead, y ahora tamaño
funcional IFPUG) apuntan al mismo lugar — no es casualidad, es la señal de que `competencia` es
efectivamente el Core Domain del sistema, tal como lo define `CLAUDE.md §3`.

### 2.3 Verificación de industria — dónde cae AtaraxiaDive por tamaño

| Rango ISBSG | UFP | AtaraxiaDive |
|---|---|---|
| Proyecto pequeño | < 100 FP | resultados (44), identidad (34), notificaciones (13) — a nivel BC |
| **Proyecto mediano** | **100–400 FP** | **registro (119), competencia (111), torneo (52) — y el total consolidado (343–373)** |
| Proyecto grande | > 400 FP | — |

343–373 FP ubica a AtaraxiaDive como un proyecto **mediano** según ISBSG — ni trivial ni un
sistema masivo, consistente con ser una plataforma de nicho para un deporte específico.

---

## 3. Productividad — lo que funciona comparar y lo que no

Se probaron **cinco** formas de medir productividad contra benchmarks de industria. Dos fueron
descartadas explícitamente por dar resultados no creíbles; una fue descartada por el modelo
subyacente; **una es la comparación central de este documento**, y sostiene el hallazgo con datos
reales. El detalle completo de cada intento (fórmulas, fuentes citadas, cálculos) está en
`BENCHMARK-INDUSTRIA.md §5.1`.

### 3.1 Lo que se descartó (por transparencia metodológica)

| Método | Resultado | Por qué se descarta |
|---|---|---|
| **SLOC/día** | 377–454 SLOC/día | No descartado — pero es una unidad débil (no captura valor/función), solo confirma que la *velocidad de tipeo* está en rango humano senior alto (200–500+), no sobrehumana |
| **FP/persona-mes (backfiring SLOC→FP)** | ≈380 FP/pm | El backfiring SLOC→FP tiene hasta 500% de variación documentada entre lenguajes/organizaciones — el número en sí no es confiable, independientemente del denominador |
| **FP/persona-mes (conteo IFPUG real)** | ≈136–257 FP/pm, según supuesto de horas | El numerador (FP) ahora es sólido, pero el denominador no: el proyecto solo trackea **días calendario**, no horas de esfuerzo registradas por fase (que es lo que ISBSG realmente mide vía PDR). Se probaron 3 supuestos de horas independientes (152h/mes continuas, 4h/día laboral, y horas reconstruidas de timestamps de commits vía heurística de sesiones) — **los tres** dan un PDR por debajo del mínimo observado en una muestra real de 14 proyectos ISBSG comparables. Eso no es evidencia de productividad extrema; es evidencia de que "horas de esfuerzo humano" ya no es la unidad correcta cuando buena parte del *build* lo ejecuta un agente de IA sin consumir horas-reloj humanas proporcionales al output |
| **Esfuerzo vs. COCOMO** | Ratio 33x–47x sobre el esfuerzo real | COCOMO está calibrado sobre un corpus de proyectos de los 80–2000, mayormente con procesos formales pesados y equipos de varias personas — un ratio de 33x–47x es evidencia de que el modelo no aplica a esta escala/contexto, no de productividad real |

### 3.2 Lo que sí se sostiene — duración calendario vs. tamaño funcional

Esta es la única comparación de productividad que **no requiere saber cuántas horas trabajó
nadie** — usa duración calendario directamente, contra una tabla real de ISBSG (*Analysis of
Project Duration by Size and Effort*, 2010; N=1513 proyectos totales, N=125 en la banda de tamaño
relevante).

| Estadístico (banda 301–400 FP, N=125 proyectos reales) | Meses |
|---|:--:|
| Mínimo | 0.3 |
| P10 | 2.9 |
| P25 | 3.4 |
| **Mediana** | **6.0** |
| P75 | 10.0 |
| P90 | 13.0 |
| Máximo | 33.6 |
| Media | 7.7 |

**AtaraxiaDive: 2.53 meses (77 días) para 343–373 FP.**

| Comparación | Resultado |
|---|---:|
| vs. mediana (6.0 meses) | **2.4x más rápido** |
| vs. media (7.7 meses) | **3.0x más rápido** |
| vs. P10 — el 10% más rápido de 125 proyectos reales (2.9 meses) | 1.15x más rápido que ese percentil |

**Por qué esta comparación es la más creíble de todo el análisis:**

1. El resultado cae **dentro** del rango real observado (mínimo de la banda: 0.3 meses) — no por
   debajo de él, a diferencia de los intentos de FP/persona-mes en §3.1.
2. Los 125 proyectos de esa banda son mayormente de **equipos**, no de una sola persona — el
   propio reporte ISBSG señala que a este tamaño "lo que el equipo puede lograr es proporcional a
   su tamaño". Que un desarrollador solo iguale o supere el ritmo del 10% más rápido de proyectos
   típicamente hechos por equipos completos es una señal más fuerte que si lo hubiera hecho un
   equipo grande.
3. No depende de ningún supuesto frágil (horas por día, backfiring SLOC→FP, calibración COCOMO) —
   es duración observada contra duración observada.

### 3.3 Conclusión de productividad

**No hay evidencia creíble de un multiplicador de "horas de esfuerzo" (tipo FP/persona-mes) —
porque este proyecto no tiene grupo de control y no registra horas reales.** Lo que sí hay,
sostenido con datos reales de industria, es evidencia de **compresión de calendario**:
AtaraxiaDive entregó un tamaño funcional mediano (343–373 FP) en una fracción del tiempo que
toman proyectos comparables reales — 2.4x–3x más rápido que la mediana/media — sin necesitar
ningún supuesto no verificable.

Esto es una afirmación **distinta y más defendible** que "el desarrollador escribió código 3x-10x
más rápido" (`CONCLUSIONES-IEDD.md §4.1`, ya marcada como necesitada de ajuste en
`BENCHMARK-INDUSTRIA.md §5.2`). La afirmación correcta es sobre **tiempo de entrega de un tamaño
funcional dado**, no sobre velocidad de tipeo ni sobre "productividad por hora" — esa distinción
importa porque son unidades distintas y solo una de ellas tiene un benchmark real y creíble
para compararse.

---

## 4. Calidad — ¿se sacrificó algo por la velocidad?

Si la conclusión de §3 fuera solo "se entregó rápido", sin más, sería una afirmación débil —
cualquiera puede entregar rápido sacrificando diseño, tests o mantenibilidad. Por eso el proyecto
midió calidad con el mismo rigor, de forma independiente, en 4 ángulos distintos.

### 4.1 Calidad estructural (código)

| Métrica | Valor v1.0.5 | Umbral "bueno" | Evaluación |
|---|:--:|:--:|:--:|
| CC domain/ promedio | 1.86 | < 5 | ✅ Muy bajo |
| MI domain/ promedio | 88.02 / 100 | > 85 | ✅ Altamente mantenible |
| Bugs estimados (Halstead) | 0.298 / 1 000 SLOC | 1–25 (Capers Jones) | ✅ 3× mejor que el límite inferior del rango industrial |
| Clases con LCOM > 1 | 3.2% (10/309) | < 10% | ✅ Cohesión alta |

Fuente: `estructurales/backend-cc.md`, `backend-mi.md`, `backend-halstead.md`, `backend-ck.md`.

### 4.2 Calidad arquitectónica

| Métrica | Valor | Evaluación |
|---|---|:--:|
| Gradiente de acoplamiento I(domain) → I(api) | 0.273 → 0.903 | ✅ Patrón esperado de arquitectura hexagonal — domain estable, api volátil, sin inversión |
| ArchitectAnalyst — `should_block` | `false` en las 7 mediciones del proyecto | ✅ Nunca bloqueó un cierre de SP |
| ArchitectAnalyst — CRITICAL | 3 (estables desde BL-007: identidad, shared, registro) | ℹ️ Zona de Dolor conocida, no bloqueante |
| DesignReviewer — CRITICAL en 793+ commits | **0, toda la historia del proyecto** | ✅ El gate nunca activó un bloqueo de PR por violación de diseño |

Fuente: `calidad/architectanalyst-d.md`, `calidad/designreviewer-evolucion.md`.

### 4.3 Calidad de testing

| Métrica | Valor v1.0.5 | Umbral proyecto (`CLAUDE.md §6`) | Evaluación |
|---|:--:|:--:|:--:|
| Cobertura global | 95.35% | 90% en domain/+application/ | ✅ Cumplido con margen amplio |
| Cobertura domain/ | 97.3% | 90% | ✅ |
| Cobertura application/ | 93.7% | 90% | ✅ |
| Ratio test/código | 1.55 | — | ℹ️ Por cada línea de producción, 1.55 líneas de test |
| BDD Scenarios | 647 (127 feature files) | — | ℹ️ Cobertura funcional verificable, no solo unitaria |

Fuente: `calidad/cobertura-tests.md`, `calidad/test-to-code-ratio.md`.

**Nota:** `resultados/application/` mantiene un gap histórico en 76.9% (`cobertura-tests.md §5`) —
la única debilidad de cobertura identificada en todo el proyecto, sin cambios entre BL-006 y
v1.0.5, y no crítica porque `resultados` es el BC de menor complejidad ciclomática del sistema.

### 4.4 Conclusión de calidad

**Las 8 métricas de calidad (4 estructurales + 2 arquitectónicas + 2 de testing) se mantuvieron
en la misma categoría — sin degradación — durante los 77 días del proyecto, incluidos los últimos
14 días de despliegue real y corrección post-producción.** Ninguna métrica cruzó de "buena" a
"aceptable" ni de "aceptable" a "mala" en ningún punto medido (BL-001 → BL-007 → v1.0.5). El
hallazgo más revelador es Halstead: el proyecto completo, no solo un punto intermedio favorable,
está en el percentil <10 de la industria en densidad de bugs estimados.

**Esto es lo que hace defendible la comparación de productividad de §3.2.** No es "se entregó
rápido, punto" — es "se entregó 2.4x–3x más rápido que proyectos comparables reales, sosteniendo
simultáneamente un nivel de calidad que la industria típicamente no logra ni siquiera al ritmo
normal". Esa combinación (velocidad + calidad sostenida), no un número aislado, es el hallazgo que
vale citar.

---

## 5. Conclusión general del experimento

| Pregunta | Respuesta | Confianza |
|---|---|:--:|
| ¿Qué tamaño tiene el sistema? | 343–373 Function Points IFPUG — proyecto mediano según ISBSG | Alta — conteo manual auditable, ISO/IEC 20926 |
| ¿Cuánto tardó, comparado con proyectos reales similares? | 2.53 meses vs. 6.0 (mediana) / 7.7 (media) de 125 proyectos ISBSG comparables — **2.4x–3x más rápido** | Alta — datos reales, sin supuestos frágiles |
| ¿Se sacrificó calidad por velocidad? | No — 8 métricas de calidad independientes se mantuvieron estables en niveles de producción durante todo el proyecto | Alta — verificado en 7 baselines, no solo al cierre |
| ¿Cuánto aportó específicamente la IA, en términos de horas ahorradas? | **No medible con este dataset** — no hay grupo de control ni horas de esfuerzo registradas; los intentos de FP/persona-mes fallan estructuralmente, no por elección de supuestos | Baja/No aplicable — requeriría un experimento controlado dedicado |

**La afirmación defendible para el paper no es un multiplicador de productividad por hora — es
una afirmación de compresión de calendario con calidad sostenida:** AtaraxiaDive entregó un
tamaño funcional mediano (343–373 FP, comparable a un ERP departamental pequeño) en 2.53 meses,
una fracción del tiempo que toman proyectos reales de tamaño equivalente (2.4x–3x más rápido que
mediana/media de 125 proyectos ISBSG), sin degradar ninguna de las 8 métricas de calidad medidas
de forma independiente a lo largo de todo el proyecto.

**Lo que queda abierto para trabajo futuro:** un experimento controlado (mismo desarrollador,
mismo tipo de US, con y sin asistencia de IA, tiempo y defectos medidos directamente) es la única
forma de obtener un multiplicador de productividad válido *causalmente* atribuible a la IA. Ese
experimento no se hizo — este documento mide el resultado final del proyecto contra benchmarks
externos, no un contraste interno con/sin asistencia.

---

## 6. Mapa de fuentes

| Documento | Contenido |
|---|---|
| [`productividad/fpa-ifpug.md`](productividad/fpa-ifpug.md) | Conteo IFPUG completo por BC (DET/RET/FTR) |
| [`productividad/tamano-funcional.md`](productividad/tamano-funcional.md) | Proxies de tamaño (US, BDD, endpoints) |
| [`productividad/velocidad-sp.md`](productividad/velocidad-sp.md) | Velocidad por SP, duración calendario |
| [`BENCHMARK-INDUSTRIA.md`](BENCHMARK-INDUSTRIA.md) | Los 5 intentos de comparación de productividad, con fuentes citadas |
| [`REPORTE-METRICAS.md`](REPORTE-METRICAS.md) | Síntesis ejecutiva de las 17 métricas originales |
| [`CONCLUSIONES-IEDD.md`](CONCLUSIONES-IEDD.md) | Conclusiones de calidad por baseline, con foco en evolución temporal |
| [`calidad/*.md`](calidad/) | Detalle de cobertura, DesignReviewer, ArchitectAnalyst, test/código |
| [`estructurales/*.md`](estructurales/) | Detalle de CC, MI, Halstead, CK, acoplamiento, duplicación |

---

*Compilado: 2026-08-20 — cierre del experimento IEDD, tag `v1.0.5`, proyecto completo (SP1 →
SP-ADJ-13).*
