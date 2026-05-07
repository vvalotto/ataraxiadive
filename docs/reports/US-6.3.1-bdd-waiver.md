# Waiver BDD — US-6.3.1

**US:** Inicio Atleta — "En línea" en Header + Sin "Hola" + Torneos en Curso Ordenados
**Incremento:** INC-6.3 — Ajustes Atleta
**Producto:** frontend
**Fecha:** 2026-05-07

---

## Decisión

Las Fases 1 y 6 de BDD se omiten para `US-6.3.1` porque la historia modifica solo
presentación y ordenamiento local en `frontend/`, sin cambios de backend, contratos HTTP,
persistencia ni reglas de dominio.

La validación se reemplaza por:

- `npm run build`
- `npm run lint`
- revisión UI/manual del portal atleta

---

## Mapeo de Criterios

| Criterio de aceptación | Evidencia esperada |
|---|---|
| Header muestra "En línea" con punto verde | `AtletaShell.tsx` + revisión UI |
| No aparece "Hola" antes del nombre | `AtletaHomePage.tsx` + revisión UI |
| OT futuro más próximo aparece primero | helper `sortDisciplinasPorOt` |
| OT pasado aparece al final | helper `sortDisciplinasPorOt` |
| Sin OT va antes de realizadas | helper `sortDisciplinasPorOt` |

---

## Alcance del Waiver

Este waiver aplica solo a `US-6.3.1`. Si una US de INC-6.3 toca `src/` o endpoints
backend, debe volver al flujo formal con escenarios BDD/HTTP cuando corresponda.
