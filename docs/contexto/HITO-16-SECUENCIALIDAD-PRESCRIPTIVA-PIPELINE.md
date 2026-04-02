# HITO-16 — La secuencialidad del pipeline no es una optimización: es una prescripción metodológica

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-16 — Aprendizaje experimental durante SP3 |
| **Fecha** | 2026-04-02 |
| **Sprint** | SP3 — US-3.5.1 (RankingOverall) |
| **Relacionado** | `docs/plans/WORKFLOW-DESARROLLO.md` · `docs/specs/sp3/US-3.5.1.md` · `docs/reports/US-3.5.1-report.md` |

---

## Contexto

Durante la ejecución de `US-3.5.1` se intentó operar el tracking del pipeline
de `/implement-us` con invocaciones paralelas del CLI (`init`, `start-phase`,
`end-phase`) mientras se inspeccionaban otros artefactos en paralelo.

El resultado fue:

- pérdida intermitente del "tracking activo";
- fases abiertas/cerradas en estados inconsistentes;
- archivos JSON del tracker con contenido corrupto o truncado;
- necesidad de reconstrucción manual del tracker al cierre de la US.

El problema parecía, en la superficie, una falla técnica del sistema de tracking.
El análisis posterior mostró algo más importante.

---

## El hallazgo

**La secuencialidad del pipeline `/implement-us` no es una preferencia operativa.
Es una restricción constitutiva del método.**

El workflow del proyecto ya lo prescribía:

- una branch por US;
- un tracker activo por vez;
- una fase por vez;
- aprobación explícita en Fase 2 y Fase 8;
- artefactos físicos producidos en orden.

La herramienta de tracking no está diseñada para tolerar concurrencia porque
el método no la contempla. Tratar esa linealidad como "detalle de implementación"
fue un error conceptual.

---

## Qué pasó realmente

La interpretación inicial fue: "el tracker se corrompe con facilidad; tal vez
habría que endurecerlo técnicamente con locks, writes atómicos o mayor tolerancia
a concurrencia".

Ese diagnóstico es incorrecto dentro del marco del experimento.

Lo que falló no fue la herramienta frente a un uso legítimo. Lo que falló fue
la ejecución frente a una **violación del protocolo prescripto**.

Cuando se paralelizaron operaciones del tracker:

- se rompió la hipótesis de "una sola transición de estado por vez";
- se invalidó el criterio de "tracker activo";
- dejó de ser confiable la correspondencia entre pipeline real y artefacto de control.

En otras palabras: la corrupción observada no fue evidencia contra la
herramienta; fue evidencia de que el método depende de la secuencialidad.

---

## Aprendizaje metodológico central

> En un pipeline prescriptivo como `/implement-us`, la secuencialidad no debe
> tratarse como una característica accidental de tooling, sino como parte del
> contrato metodológico que garantiza trazabilidad y confiabilidad del proceso.

Esto tiene una consecuencia práctica fuerte:

- hay actividades que sí pueden paralelizarse, como lecturas auxiliares o
  inspecciones de contexto;
- pero **ninguna transición de estado del pipeline** debe ejecutarse en paralelo:
  ni tracker, ni cambios de fase, ni cierres/aprobaciones.

El pipeline expresa un proceso linealmente gobernado. Su valor experimental
depende de preservar esa linealidad.

---

## Relación con HITO-12

HITO-12 mostró que las instrucciones textuales no alcanzan cuando el LLM tiene
un modelo implícito de completitud distinto del protocolo.

HITO-16 agrega una dimensión nueva:

- HITO-12: un gate textual puede ser insuficiente para forzar completitud.
- HITO-16: incluso con protocolo correcto, si se viola la secuencialidad
  prescripta, los artefactos de control dejan de representar fielmente el proceso.

Ambos hitos apuntan a la misma dirección: el comportamiento procedimental del
LLM debe gobernarse con reglas operativas explícitas, no solo con intención.

---

## Aprendizaje secundario surgido en la misma US

La implementación de `US-3.5.1` dejó además un hallazgo arquitectónico útil:

**El Overall conviene calcularse desde rankings por disciplina ya construidos en
el BC `resultados`, no desde performances crudas de `competencia`.**

La spec permitía una lectura ambigua sobre la fuente del cálculo. El trabajo
real mostró que:

- `US-3.5.1` debe concentrarse en la lógica de agregación overall;
- `US-3.5.2` debe encargarse de la política P-09 que decide cuándo dispararlo;
- mantener el cálculo dentro de `resultados` preserva mejor la frontera del BC.

Esto refuerza una idea ya sugerida por HITO-15: ciertas decisiones de lectura y
proyección no emergen plenamente de la especificación de dominio, sino del
contacto entre especificación, implementación y arquitectura.

---

## Implicancia para el experimento

Este HITO fortalece la hipótesis de que el `human-in-the-loop` sigue siendo
esencial no solo para decidir sobre dominio y arquitectura, sino también para
**gobernar el propio proceso de automatización**.

No alcanza con tener:

- specs rigurosas,
- skill definido,
- quality gates,
- tracking automático.

También hace falta criterio humano para preservar las condiciones de validez del
método. En este caso, la condición era la secuencialidad del pipeline.

---

## Regla operativa derivada

Para futuras US del experimento:

1. Las operaciones del tracker y del pipeline de fases se ejecutan siempre en serie.
2. Solo las lecturas auxiliares pueden paralelizarse.
3. Si el tracker queda inconsistente, se registra como incidente metodológico,
   no como simple bug técnico.
4. La pregunta correcta no es "¿cómo hacemos el tracker concurrente?" sino
   "¿cómo evitamos violar la secuencialidad prescripta?".

---

*Registrado: 2026-04-02 — durante la ejecución de US-3.5.1 en SP3*
