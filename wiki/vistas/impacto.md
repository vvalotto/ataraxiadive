---
title: "Vista de Impacto"
type: vista
last_updated: "2026-05-20"
sources:
  - src/
  - docs/adr/
  - wiki/bounded-contexts/
---

# Vista de Impacto

> El sistema visto desde las dependencias y el riesgo de cambio.

## Propósito

Responder preguntas sobre qué se ve afectado cuando algo cambia. Mapear los
puntos de acoplamiento del sistema, las interfaces críticas y los componentes
de mayor riesgo. Es la vista de mayor valor para mantenimiento y la única
que el wiki crea por inferencia — no existe como documentación previa en el
proyecto.

## Stakeholder principal

Desarrollador planificando una modificación, tech lead evaluando el alcance
de una tarea.

## Preguntas características

1. Si cambio la interfaz de `EventStorePort`, ¿qué módulos se ven afectados?
2. ¿Qué BCs dependen del BC Identidad para funcionar?
3. ¿Qué tests fallarían si modifico el aggregate Performance?
4. ¿Qué documentos habría que actualizar si cambia el esquema del Event Store?
5. ¿Cuál es el componente de mayor acoplamiento en el sistema?
6. ¿Qué cambios en el BC Torneo impactan al BC Competencia?
7. Si agrego un nuevo tipo de tarjeta, ¿qué partes del sistema debo revisar?

## Puntos de acoplamiento conocidos

> *Vacío — se construye durante Fase 2 por inferencia del LLM sobre el código
> y los ADRs. Es la única sección del wiki que no tiene fuente documental
> directa: el LLM la genera analizando relaciones entre BCs, puertos e interfaces.*

Componentes de alto impacto esperados (a validar en Fase 2):
- `EventStorePort` — usado por Competencia y Notificaciones
- `JWT / Identidad` — dependencia transversal de todos los BCs
- `Grilla` / estructura de competencia — conecta Torneo → Competencia
- ACL Registro → Torneo (lectura de atletas e inscripciones)
- ACL Resultados → Competencia (lectura de performances)

## Recorridos sugeridos

**Para analizar el impacto de un cambio en una interfaz:**
`[[impacto/<interfaz>]]` → BCs consumidores → tests afectados
→ ADRs relacionados → documentos a actualizar

**Para evaluar el riesgo de tocar un BC:**
`[[<nombre-bc>]]` → sección "dependencias entrantes" → BCs dependientes
→ `[[impacto/<componente-critico>]]`

**Para planificar una nueva feature:**
`[[vistas/trazabilidad]]` (entender qué existe) →
`[[vistas/decisiones]]` (entender restricciones) →
`[[vistas/impacto]]` (entender qué se afecta)

## Páginas hub de esta vista

- `wiki/impacto/` — páginas por componente/interfaz crítica (a crear en Fase 2)
- [[competencia]] — BC de mayor complejidad y más dependencias
- [[identidad]] — BC transversal del que todos dependen

---
*Vista pendiente de poblarse — requiere Fase 2 (construcción por inferencia del LLM)*
*Esta es la única vista sin fuente documental directa — se genera analizando src/ y ADRs*
