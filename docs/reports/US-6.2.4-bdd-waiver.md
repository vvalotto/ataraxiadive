# Waiver BDD — US-6.2.4
## Panel torneo: alertas limpias y jueces simplificados

**Fecha:** `2026-05-05`  
**Decisión:** `BDD no ejecutable para frontend puro`

## Justificación

`US-6.2.4` modifica exclusivamente presentación React en el portal organizador:

- elimina acciones visibles `Resolver ->` que no corresponden al rol organizador;
- elimina tarjetas de resumen redundantes del panel de jueces;
- elimina texto adicional junto al selector de juez.

No introduce reglas de dominio, endpoints, persistencia, contratos API ni comportamiento en `src/`.
El repositorio no cuenta hoy con harness automatizado de UI React (`vitest`,
`playwright` o equivalente) ni con steps BDD reutilizables para navegación del
portal organizador. Crear esa infraestructura en esta US desviaría el alcance
hacia una plataforma de testing frontend transversal.

## Validación sustitutiva

- `npm run build` en `frontend/`.
- ESLint focalizado sobre archivos modificados.
- `npm run lint` global para registrar estado del frontend.
- Revisión manual de ausencia de textos:
  - `Resolver ->`
  - `Cobertura operativa`
  - `Estado de asignación`
- Revisión manual de que el selector de juez conserva la asignación.

## Alcance del waiver

- Se omite la creación de `.feature` y steps para esta US.
- Se omite Fase 6 de validación BDD ejecutable.
- No exime Fase 2, implementación, validación frontend, documentación ni reporte final.
