# Plan de Implementación — US-6.2.3

**US:** US-6.2.3 — Resultados: quitar PTS FAAS + andarivel numérico + AP como Anuncio  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.3-resultados-anuncio-andarivel`  
**Estimación:** 40 min  
**Estado:** Completado  
**Fecha implementación:** 2026-05-05  

---

## Contexto Validado

- Spec fuente: `docs/specs/sp6/US-6.2.3.md`
- Hallazgo fuente: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-05
- Fuente UX consultada:
  - `docs/design/ux/wireframes-organizador.md`
  - `docs/design/ux/prototipos/prototipo-organizador.html`
  - `docs/design/ux/README.md`
- Componentes afectados:
  - `frontend/src/components/organizador/TablaDisciplinaResultados.tsx`
  - `frontend/src/components/organizador/FilaResultado.tsx`
  - `frontend/src/pages/organizador/ResultadosPage.tsx`

La US es frontend puro. Por instrucción operativa del usuario, se omiten Fase 1 y Fase 6 de BDD. La validación se hará con build/lint de frontend y revisión manual del comportamiento.

---

## Hallazgos de Fase 0

- `TablaDisciplinaResultados` tiene helper `formatearLinea` que convierte `1 → A`, `2 → B`.
- `TablaDisciplinaResultados` renderiza header `AP`.
- `TablaDisciplinaResultados` renderiza header `Pts FAAS`.
- La celda de puntos FAAS se renderiza en `FilaResultado`.
- `ResultadosPage` contiene copy visible: `Tabla de ejecucion ordenada por OT con AP, RP, tarjeta y puntos FAAS.`
- La spec `US-6.2.3` no incluye el campo obligatorio `## Fuente de verdad UX` definido por `WORKFLOW-DESARROLLO.md` para US que tocan `frontend/`.

---

## Tareas

### 1. Implementación UI — TablaDisciplinaResultados (15 min)

- [x] Reemplazar `formatearLinea` por `formatearAndarivel`.
- [x] Mostrar andarivel numérico literal.
- [x] Mostrar `—` si el andarivel es `null`, `undefined` o `0`.
- [x] Cambiar header `AP` por `Anuncio`.
- [x] Eliminar header `Pts FAAS`.
- [x] Mantener el campo `puntos` en DTO/API; no tocar API ni queries.

### 2. Implementación UI — FilaResultado (5 min)

- [x] Eliminar render de celda `puntosDisplay`.
- [x] Mantener el resto de columnas alineado con la tabla.
- [x] No modificar `rp`, `tarjeta` ni formato de anuncio.

### 3. Copy de ResultadosPage (5 min)

- [x] Cambiar copy visible para no mencionar `AP` ni `puntos FAAS`.
- [x] Usar lenguaje de organizador: `Anuncio`, `RP`, `tarjeta` y `andarivel`.

### 4. Ajuste documental mínimo de la spec (5 min)

- [x] Agregar `## Fuente de verdad UX` a `docs/specs/sp6/US-6.2.3.md`.
- [x] Referenciar wireframes, prototipo, PLAN-SP6 y componentes React comparados.

### 5. Validación frontend (10 min)

- [x] Ejecutar `cd frontend && npm run build`.
- [x] Ejecutar ESLint focalizado sobre los archivos modificados.
- [x] Ejecutar `cd frontend && npm run lint` para registrar estado global.
- [x] Verificar que no se tocaron archivos de backend.

### 6. Cierre de US (5 min)

- [x] Actualizar estado de `US-6.2.3` de `Pending` a `Done` si la validación pasa.
- [x] Generar `docs/reports/US-6.2.3-report.md`.
- [x] Cerrar tracker de `US-6.2.3`.
- [ ] Commit atómico con referencia `[US-6.2.3]`.

---

## Validación Esperada

- La tabla de resultados no muestra columna `Pts FAAS`.
- El andarivel `1` se muestra como `1`, no `A`.
- Andarivel faltante o `0` se muestra como `—`.
- La columna de marca anunciada dice `Anuncio`.
- El copy visible no menciona puntos FAAS.
- Sin cambios en backend ni contratos API.

---

## Riesgos

- `GrillaAtletaDto.andarivel` parece tipado como número obligatorio en el frontend, pero la spec pide manejar `null`/`undefined`; el helper aceptará esos casos para robustez sin cambiar tipos de API.
- `FilaResultadoData.puntos` puede quedar como dato interno no renderizado. Si TypeScript marca dato no usado, se eliminará solo de la fila de presentación, no de DTOs ni queries.

---

## Resultado de Validación

- `npm run build`: OK.
- `./node_modules/.bin/eslint src/components/organizador/TablaDisciplinaResultados.tsx src/components/organizador/FilaResultado.tsx src/pages/organizador/ResultadosPage.tsx`: OK.
- `npm run lint`: falla por hallazgo preexistente fuera de alcance en `frontend/src/pages/juez/GrillaPage.tsx` y warning en `frontend/src/components/organizador/JuecesPanel.tsx`.

---

## Lecciones Aprendidas

- La columna FAAS estaba dividida entre header (`TablaDisciplinaResultados`) y celda (`FilaResultado`), por lo que la implementación debía tocar ambos componentes para mantener alineación de columnas.
- El copy de página también forma parte del criterio de claridad operativa; dejar `puntos FAAS` en texto visible hubiera contradicho el objetivo de la US aunque la tabla estuviera corregida.
