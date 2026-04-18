# Contexto de Implementación — US-4.4.1

**US:** US-4.4.1 — Pre-carga de disciplina en IndexedDB  
**Incremento:** INC-4.4  
**Sprint:** SP4 — La Plataforma  
**Fecha:** 2026-04-13

---

## Objetivo validado

Persistir localmente la grilla y el estado de competencia para la disciplina activa del juez,
de modo que la pantalla de grilla siga operativa cuando se pierde conexión.

## Alcance técnico confirmado

- `frontend/src/db/`: cliente IndexedDB + schema + queries.
- `frontend/src/hooks/usePrecarga.ts`: fetch online + fallback local.
- `frontend/src/pages/juez/GrillaPage.tsx`: consumo de precarga, estados de error offline y aviso de cache.

## Restricciones del entorno

- El frontend no tiene harness automatizado de browser para ejecutar BDD e2e reales.
- La validación automática de esta US se apoya en `npm run lint` y `npm run build`.
- La validación funcional offline queda como smoke manual documentado en reporte.

## Riesgos relevantes

1. `GrillaPage` hoy depende de fetch directo; refactor incompleto puede romper navegación del juez.
2. Sin cache previo + offline debe mostrar error explícito, nunca pantalla vacía.
3. Se debe mantener una única instancia de DB para evitar conexiones duplicadas a IndexedDB.

