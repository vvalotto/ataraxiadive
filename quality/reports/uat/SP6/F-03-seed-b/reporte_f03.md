# Reporte Fase F-03: Volcado de Datos (Seed-B)

**Fecha de ejecución:** 2026-05-11  
**Ejecutor:** Victor Valotto  
**Dispositivos usados:** Desktop · Móvil

## Métricas

| Métrica | Valor |
|---------|-------|
| Escenarios ejecutados | 3 |
| PASS | 3 |
| FAIL | 0 |
| SKIP | 0 |
| Hallazgos 🔴 | 0 |
| Hallazgos 🟡 | 1 (H-03-01) |
| Hallazgos ⚪ | 1 (H-03-02) |
| Mejoras registradas | 1 (H-03-03) |

## Resumen

Seed-B ejecutado con éxito: 31 atletas cargados con APs correctas en todas las disciplinas. Se detectaron y corrigieron 2 defectos visuales en `TablaInscriptos` (badge redundante, cabeceras sin centrar) y se aplicó una mejora en el portal público para mostrar disciplinas y categorías en las tarjetas de torneos. Todos los escenarios cerraron en PASS.

## Hallazgos resueltos

| ID | Severidad | Descripción | Fix |
|----|-----------|-------------|-----|
| H-03-01 | 🟡 Minor | Badge mostraba prefijo "AP declarado ·" redundante cuando había valor | `EstadoAPBadge.tsx`: solo muestra el valor cuando existe |
| H-03-02 | ⚪ Cosmético | Cabeceras de tabla sin centrar | `TablaInscriptos.tsx`: `text-center` en todos los `<th>` |
| H-03-03 | 🟡 Mejora | Portal público sin disciplinas ni categorías en tarjetas | `PublicTorneosPage.tsx`: chips via `useQuery` por torneo |

## Criterio de Salida

- [x] Seed-B ejecutado sin errores
- [x] 31 atletas visibles en lista de inscriptos
- [x] APs correctas por disciplina (metros y mm:ss)
- [x] Estado del torneo: `INSCRIPCION_ABIERTA`

## Estado: ✅ CERRADA
