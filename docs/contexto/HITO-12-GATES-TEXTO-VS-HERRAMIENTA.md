# HITO-12 — Gates de texto vs constraints de herramienta: las instrucciones procedurales en lenguaje natural no son barreras reales para LLMs

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-12 — Análisis experimental |
| **Fecha** | 2026-03-26 |
| **Sprint** | SP2 — Inc 2.2 |
| **Relacionado** | `vvalotto/claude-dev-kit#44` · `vvalotto/claude-dev-kit#45` · `docs/contexto/IMPLEMENT-US-DISCREPANCIAS.md` |

---

## Contexto

Al finalizar la implementación de US-2.2.1, las Fases 8 (Documentación) y 9 (Reporte Final) del skill `/implement-us` fueron omitidas completamente. El LLM pasó directo de los quality gates aprobados al commit, push y PR.

No fue la primera vez. El mismo patrón ocurrió en US-1.2.5, INC-2.0 y US-2.2.1 — tres sesiones distintas, tres reincidencias del mismo comportamiento, a pesar de que el gate ya existía en los archivos del skill y de que el feedback estaba registrado en memoria.

---

## El gate que no funcionó

La Fase 9 de `/implement-us` ya contenía este texto:

> *"🔒 Gate de cierre — OBLIGATORIO antes de declarar el skill completo:*
> *Mostrar en el chat ≠ persistir en disco. El skill implement-us NO está completo hasta que este archivo exista en disco."*

El gate existía. Fue ignorado tres veces.

---

## Análisis

El problema no es de comprensión — el LLM entiende perfectamente qué dice el gate. El problema es de **criterio de completitud implícito que no coincide con el protocolo**.

Cuando los tests pasan y el quality gate aprueba, el LLM opera con un modelo mental donde "tests verdes = trabajo listo para mergear". Las Fases 8 y 9 no producen código ni hacen pasar tests: producen artefactos de documentación. Desde el punto de vista del LLM, cuando el contexto de implementación está "resuelto" y los resultados son verdes, la siguiente acción más natural de la conversación es avanzar hacia el siguiente estado visible (commit, push, merge) — no ejecutar pasos administrativos sobre trabajo ya completado.

Tres factores amplifican el problema:

1. **Sin verificador activo de fases**: No hay ningún mecanismo que calcule "fases ejecutadas vs fases requeridas" antes de permitir el commit.
2. **La sensación de completitud es anticipatoria**: El LLM "sabe" qué escribiría en el reporte, lo que hace que el acto de escribirlo físicamente parezca redundante.
3. **El feedback en memoria no es suficiente**: La corrección se registró después de US-1.2.5 y después de INC-2.0. No impidió la reincidencia en US-2.2.1. El patrón es más fuerte que la instrucción.

---

## El aprendizaje central

**Las instrucciones procedurales en lenguaje natural dentro de un skill no son equivalentes a constraints de herramienta.**

Un gate de texto dice "no hagas esto sin hacer aquello primero". Un constraint de herramienta hace que "aquello" sea literalmente imposible sin haber hecho "esto". La diferencia no es de claridad de la instrucción — es de mecanismo de enforcement.

Para un LLM, una instrucción en texto compite con el flujo conversacional, con el contexto acumulado, y con el modelo mental implícito de "qué es lo siguiente". Un constraint de herramienta no compite con nada: o se satisface o la acción falla.

---

## Implicancia para el experimento IEDD

Este hallazgo tiene relevancia directa para la Hipótesis H-2 del experimento:

> *"¿IEDD mejora la calidad de las especificaciones?"*

La hipótesis asume que una especificación bien redactada es suficiente para guiar el comportamiento. Este HITO sugiere que hay una categoría de comportamiento — el comportamiento **procedimental** del LLM durante la ejecución de un workflow — donde la calidad de la especificación textual no es el factor determinante. El factor determinante es si el mecanismo de enforcement opera a nivel de herramienta o a nivel de instrucción.

Dicho de otro modo: **IEDD puede producir especificaciones impecables de dominio y aún así fallar en garantizar la completitud de un pipeline si el enforcement es solo textual.**

Esto distingue dos tipos de especificación:
- **Especificación de comportamiento de dominio** → el LLM la sigue con alta fidelidad (invariantes, reglas de negocio, precondiciones)
- **Especificación de comportamiento procedimental del LLM** → requiere enforcement de herramienta, no solo texto

---

## Acción tomada

Creado issue `vvalotto/claude-dev-kit#44` con análisis de opciones:

- **Opción A** (recomendada): gate ejecutable en Bash al final de Fase 7 y Fase 9 — convierte el gate de texto en un comando con salida verificable
- **Opción C** (red de seguridad): pre-push hook que bloquea el push si el reporte no existe en disco

La combinación A+C cubre dos vectores de falla distintos: el flujo conversacional y la herramienta de git.

---

## Relevancia para otros proyectos con IEDD + LLM

Al diseñar un skill o workflow para LLM:

1. **Identificar qué pasos producen código/tests vs qué pasos producen artefactos administrativos** — los segundos son los de mayor riesgo de omisión
2. **Para pasos críticos de cierre: reemplazar el gate de texto por un comando verificable** con salida observable (exit code, archivo esperado, etc.)
3. **No asumir que el feedback en memoria previene reincidencias en patrones de flujo** — la memoria ayuda con decisiones de dominio, no con hábitos de ejecución

---

*Registrado: 2026-03-26 — Sesión Inc 2.2, post US-2.2.1*
