# Hallazgos — Fase F-03: Volcado de Datos (Seed-B)

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-03-02 | F03-S01 | Cabeceras de la tabla de inscriptos sin centrar | ⚪ | Ver lista de inscriptos · cabeceras alineadas a la izquierda | ✅ Resuelto | `text-center` agregado a todos los `<th>` en `TablaInscriptos.tsx` |
| H-03-01 | F03-S01 | El badge mostraba "AP declarado · 52.40m" — el prefijo "AP declarado ·" es redundante cuando el valor está presente | 🟡 | Ver lista de inscriptos con AP declarada · columna ANUNCIO muestra el texto completo | ✅ Resuelto | `EstadoAPBadge.tsx`: cuando hay valor solo muestra el valor, sin prefijo |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| H-03-03 | F03 observación | Portal público no mostraba disciplinas ni categorías del torneo en las tarjetas | 🟡 Media |

**Fix H-03-03:** `PublicTorneosPage.tsx` — `TorneoCard` usa `useQuery` para obtener disciplinas por torneo y muestra chips de disciplinas (sky) y categorías (slate) cuando están disponibles.
