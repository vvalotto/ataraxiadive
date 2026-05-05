# Plan de Implementación — US-6.2.4

**US:** US-6.2.4 — Panel torneo: alertas sin Resolver + jueces simplificados  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature-US-6.2.4-panel-torneo`  
**Estimación:** 35 min  
**Estado:** Completado  
**Fecha plan:** 2026-05-05  

---

## Contexto Validado

- Spec fuente: `docs/specs/sp6/US-6.2.4.md`
- Hallazgos fuente: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-02, UI-ORG-06
- Fuente UX consultada:
  - `docs/design/ux/wireframes-organizador.md`
  - `docs/design/ux/prototipos/prototipo-organizador.html`
- Componentes afectados:
  - `frontend/src/pages/organizador/DashboardOperativoPage.tsx`
  - `frontend/src/components/organizador/JuecesPanel.tsx`
  - `frontend/src/components/organizador/TablaJueces.tsx`

La US es frontend puro. Por evaluación de Fase 1 y regla operativa del usuario,
se omiten BDD ejecutable y Fase 6. La validación se hará con build/lint de
frontend y revisión manual del comportamiento.

---

## Hallazgos de Fase 0

- `DashboardOperativoPage` renderiza `Resolver ->` en el encabezado de alertas activas.
- `DashboardOperativoPage` renderiza `Resolver ->` dentro de cada alerta.
- `JuecesPanel` renderiza tarjetas `Cobertura operativa` y `Estado de asignación`.
- `TablaJueces` renderiza texto adicional bajo `JuezSelector` con `Pendiente`, `Guardando...` o el nombre del juez.
- `TablaJueces` contiene helper `juezLabel` usado solo para ese texto adicional.
- La spec original no incluía `## Fuente de verdad UX`; se corrigió en Fase 0.
- La fila de juez vive en `TablaJueces.tsx`, no directamente en `JuecesPanel.tsx`; se corrigió la lista de archivos afectados.

---

## Tareas

### 1. Implementación UI — DashboardOperativoPage (8 min)

- [x] Eliminar el `Link`/acción `Resolver ->` del encabezado de alertas activas.
- [x] Eliminar el texto `Resolver ->` dentro de cada alerta.
- [x] Mantener las alertas visibles y navegables si el contenedor ya funciona como `Link`.
- [x] No modificar cálculo ni fuente de datos de `alertas`.

### 2. Implementación UI — JuecesPanel (8 min)

- [x] Eliminar el bloque de resumen `Cobertura operativa`.
- [x] Eliminar el bloque de resumen `Estado de asignación`.
- [x] Mantener header, badge de asignación completa/pendiente, selector de disciplina y tabla.
- [x] Eliminar variables derivadas que queden sin uso (`sinJuecesAsignados`) si TypeScript/ESLint lo exige.
- [x] Corregir warning focal de hook envolviendo `disciplinas` en `useMemo`.

### 3. Implementación UI — TablaJueces (7 min)

- [x] Eliminar el texto adicional bajo `JuezSelector`.
- [x] Mantener el selector habilitado/deshabilitado igual que antes.
- [x] Mantener feedback de guardado sin reintroducir nombre duplicado; si hace falta feedback, usar `disabled` del selector existente.
- [x] Eliminar helper `juezLabel` si queda sin uso.

### 4. Validación frontend (8 min)

- [x] Ejecutar `cd frontend && npm run build`.
- [x] Ejecutar ESLint focalizado sobre:
  - `src/pages/organizador/DashboardOperativoPage.tsx`
  - `src/components/organizador/JuecesPanel.tsx`
  - `src/components/organizador/TablaJueces.tsx`
- [x] Ejecutar `cd frontend && npm run lint` para registrar estado global.
- [x] Verificar que no se tocaron archivos de backend.

### 5. Cierre documental (4 min)

- [x] Actualizar estado de `US-6.2.4` de `Pending` a `Done` si la validación pasa.
- [x] Generar `docs/reports/US-6.2.4-report.md`.
- [ ] Cerrar tracker de `US-6.2.4`.
- [ ] Commit atómico con referencia `[US-6.2.4]`.

---

## Validación Esperada

- El panel de alertas no muestra ningún texto visible `Resolver`.
- Las alertas siguen mostrando atleta, disciplina y descripción.
- `JuecesPanel` ya no muestra `Cobertura operativa` ni `Estado de asignación`.
- Cada fila de asignación muestra el `JuezSelector` sin nombre/texto duplicado debajo.
- La asignación de juez sigue invocando `onAsignar(row, juezId)`.
- Sin cambios en backend ni contratos API.

---

## Riesgos

- Si se elimina todo feedback textual bajo el selector, durante el guardado el usuario solo verá el selector deshabilitado. Es aceptable para el alcance de la US porque el objetivo explícito es dejar solo el selector.
- El encabezado de alertas quedará sin CTA global. Esto coincide con el hallazgo: el organizador no resuelve esas alertas desde ese rol.

---

## Resultado de Validación

- `npm run build`: OK.
- `./node_modules/.bin/eslint src/pages/organizador/DashboardOperativoPage.tsx src/components/organizador/JuecesPanel.tsx src/components/organizador/TablaJueces.tsx`: OK.
- `npm run lint`: falla por hallazgo preexistente fuera de alcance en `frontend/src/pages/juez/GrillaPage.tsx`.
- Revisión textual focal: sin `Resolver ->`, `Cobertura operativa`, `Estado de asignación`, `juezLabel`, `Pendiente` ni `Guardando...` visibles en los componentes objetivo.
- `git diff --check`: OK.
