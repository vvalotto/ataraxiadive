# Hallazgos — Fase F-06: Inicio de Ejecución

## H-06-01 🟡 — Andarivel no visible como columna en la grilla de asignación de jueces

**Escenario:** Pre-F06-S01 (detectado durante preparación de la fase)  
**Descripción:** En `TablaJueces`, el andarivel aparece como subtext dentro de la celda "Atleta" (`Posición X · Andarivel Y`), en lugar de ser una columna propia. Esto dificulta la lectura al asignar jueces por andarivel.  
**Impacto:** Observación — no bloquea la asignación, pero reduce claridad operativa.  
**Fix:** Agregar columna "And." entre OT y AP en `TablaJueces.tsx`.  
**Estado:** ✅ Resuelto
