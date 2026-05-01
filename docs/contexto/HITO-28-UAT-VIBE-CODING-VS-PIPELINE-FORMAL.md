# HITO-28 — UAT: Vibe Coding vs Pipeline Formal

**Fecha:** 2026-04-23
**SP:** SP5 — La Puesta en Marcha
**Incremento de referencia:** INC-5.2 + SP-ADJ-08
**Autor:** Victor Valotto + Claude Code

---

## Observación

En SPs anteriores, el ciclo de UAT seguía un pipeline formal completo:
UAT manual → registrar no conformidades → SP-ADJ con US-IEDD por ajuste.
Este ciclo resultó adecuado para hallazgos con impacto funcional (BUG-SP4-003,
BUG-SP4-004, SCOPE-SP4-001 → SP-ADJ-07).

En INC-5.2, los hallazgos UAT se resolvieron con una dinámica de vibe coding:
iteración directa sobre el código frontend sin spec previa, sin branch formal,
sin pipeline de 10 fases. El resultado fue SP-ADJ-08 con 3 US (US-ADJ-8.1,
8.2, 8.3) completadas con mayor velocidad que los SP-ADJs anteriores.

---

## Hipótesis

El costo de formalismo no es uniforme para todos los tipos de hallazgos UAT.
Los ajustes de UX —wording, layout, restricciones de interacción, claridad
de estados— son inherentemente iterativos y reversibles. Aplicarles el mismo
pipeline que a un bug de dominio produce overhead desproporcionado.

---

## Patrón establecido: clasificación por artefacto tocado

El criterio de clasificación de un hallazgo UAT es **qué archivos requiere
modificar**, no la severidad percibida del problema.

### Track informal — vibe coding

**Condición:** el cambio toca exclusivamente `frontend/`.

**Justificación:**
- El frontend no tiene invariantes de dominio
- Los cambios son reversibles y no afectan otros BCs
- No existen tests de dominio que los protejan (ni deben existir)
- La iteración visual rápida produce mejor UX que la especificación anticipada

**Proceso:**
- Sin branch dedicada, sin spec US-IEDD, sin pipeline de 10 fases
- Commits descriptivos con referencia al hallazgo UAT (ej: `fix(frontend): clarificar estados del panel organizador [UAT-5.2-03]`)
- Se puede agrupar varios hallazgos en un único commit o PR si son coherentes temáticamente

### Track formal — pipeline completo

**Condición:** el cambio requiere tocar cualquier archivo en `src/`.

**Justificación:**
- `src/` contiene comandos, eventos, invariantes y queries con efectos en el dominio
- Un cambio puede tener efectos colaterales en otros BCs, el event store, o tests de integración
- El formalismo no es overhead — es la protección contra efectos invisibles

**Proceso:** US-IEDD → spec → `/implement-us` → PR → pipeline estándar.

---

## Regla de pivote

El track se declara **antes de empezar a codear**, no después.

Si al iniciar la resolución de un hallazgo "de UX" la primera acción
necesaria es abrir un archivo de `src/`, ese es el momento de pivotar
al track formal. No continuar en modo vibe coding una vez que el scope
supera la frontera `frontend/`.

---

## Relación con el experimento IEDD

Este hallazgo cuestiona una asunción implícita del pipeline de 10 fases:
que toda unidad de trabajo que produce código merece el mismo nivel de
especificación formal. La evidencia empírica muestra que para cambios
de UX acotados al frontend, el formalismo inhibe la iteración sin
agregar valor de especificación (no hay invariantes que proteger).

La hipótesis derivada: la US-IEDD es valiosa en proporción a la densidad
de invariantes del cambio. Cambios con cero invariantes de dominio
no se benefician del formato US-IEDD.

---

## Impacto en el proceso

Formalizado en `docs/plans/WORKFLOW-DESARROLLO.md` v1.7:
- §6 Cierre de Incremento: clasificación de hallazgos UAT por track
- §7 Ciclo por SP: UAT post-SP incluye el criterio de clasificación
- §8 Quality Gates: nota sobre el track informal en hallazgos UAT
