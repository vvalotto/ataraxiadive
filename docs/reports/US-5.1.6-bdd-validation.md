# Validacion BDD — US-5.1.6

**Feature:** `tests/features/US-5.1.6-monitor-ejecucion.feature`
**Producto:** frontend

## Escenarios cubiertos

- Organizador ve progreso de una disciplina en ejecucion.
- Disciplina sin atleta en llamada muestra estado de espera.
- Refresco automatico cada 30 segundos.
- Todas las disciplinas completas muestran estado de premiacion disponible.
- Sin disciplinas en ejecucion muestra estado de espera.

## Resultado

Validacion documental/manual para frontend. El repositorio no tiene harness automatizado de
browser ni Vitest/Testing Library configurado para ejecutar estos escenarios como tests.

La verificacion ejecutable de esta US queda cubierta por:

- `npm run build`
- `npm run lint`

## Observaciones

- La spec menciona `/competencia/{id}/proximas`; la implementacion usa el endpoint real
  `/competencia/{id}/performance/proximas?disciplina=...`.
- El OT visible se obtiene cruzando la performance actual/proximos con la grilla de la
  competencia, porque los endpoints de monitor no exponen `ot_programado` directamente.
