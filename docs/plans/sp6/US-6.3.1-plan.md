# Plan de Implementación — US-6.3.1

**US:** Inicio Atleta — "En línea" en Header + Sin "Hola" + Torneos en Curso Ordenados
**Incremento:** INC-6.3 — Ajustes Atleta
**Producto:** frontend
**Patrón:** React/Vite frontend
**Estimación total:** 55 min
**Estado:** ✅ COMPLETADO
**Fecha completado:** 2026-05-07
**BDD:** No aplica por decisión operativa para US solo frontend; se valida con build/lint y revisión UI.

---

## Alcance

Implementar tres ajustes visuales y de ordenamiento en el portal atleta:

- Agregar indicador estático "En línea" junto a "AtaraxiaDive" en el header.
- Eliminar el saludo redundante "Hola" en la página de inicio.
- Ordenar las disciplinas dentro de cada tarjeta de torneo activo según OT.

No hay cambios de backend, contratos HTTP ni persistencia.

---

## Componentes a Modificar

### 1. Header atleta

- [x] `frontend/src/components/atleta/AtletaShell.tsx` (10 min)
  - Agregar punto verde y texto "En línea" junto al badge "AtaraxiaDive".
  - Mantener compatibilidad con `showBack` y `actions`.
  - Verificar que el layout no colapse en ancho móvil `max-w-[430px]`.

### 2. Inicio atleta

- [x] `frontend/src/pages/atleta/AtletaHomePage.tsx` (25 min)
  - Eliminar el `<p>Hola</p>` redundante.
  - Agregar helper local de ordenamiento para entries por OT:
    - OT futuro primero, ascendente.
    - Sin OT después de futuras.
    - OT pasado al final, ascendente.
  - Aplicar el orden solo a la lista interna de disciplinas de cada torneo.
  - Mantener el orden actual entre torneos.

### 3. Evidencia de BDD omitido

- [x] `docs/reports/US-6.3.1-bdd-waiver.md` (5 min)
  - Registrar que Fase 1 y Fase 6 se omiten por tratarse de cambio solo frontend.
  - Mapear criterios de aceptación a verificación por build/lint y revisión UI/manual.

### 4. Validación

- [x] `npm run build` en `frontend/` (10 min)
- [x] `npm run lint` en `frontend/` (5 min)

---

## Métricas de Validación

| Gate | Resultado |
|---|---|
| `npm run build` | ✅ pasa |
| `npm run lint` | ✅ pasa |
| BDD | Waiver por frontend puro |

---

## Criterios de Aceptación Cubiertos

| Criterio | Implementación | Validación |
|---|---|---|
| Header muestra "En línea" con punto verde | `AtletaShell.tsx` | Revisión UI/manual + build |
| No aparece "Hola" antes del nombre | `AtletaHomePage.tsx` | Revisión UI/manual + build |
| OT futuro más próximo aparece primero | helper de ordenamiento | Revisión de código + build |
| OT pasado aparece al final | helper de ordenamiento | Revisión de código + build |
| Sin OT va antes de realizadas | helper de ordenamiento | Revisión de código + build |

---

## Riesgos y Mitigaciones

- **Riesgo:** Comparar fechas inválidas puede producir orden inestable.
  **Mitigación:** Clasificar entradas sin OT parseable como "sin OT".

- **Riesgo:** El indicador de conexión compite con el botón `Salir` en móvil.
  **Mitigación:** Mantener el indicador dentro del bloque de marca y `actions` como `shrink-0`.

---

## Definition of Done

- [x] Cambios implementados en los dos archivos frontend previstos.
- [x] Waiver BDD persistido en `docs/reports/`.
- [x] `npm run build` pasa.
- [x] `npm run lint` pasa o se documenta bloqueo preexistente.
- [ ] Reporte final persistido en `docs/reports/US-6.3.1-report.md` antes del commit.

---

*Generado: 2026-05-07 — Fase 2 /implement-us US-6.3.1*
