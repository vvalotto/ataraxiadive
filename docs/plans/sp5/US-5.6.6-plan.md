# Plan de Implementacion - US-5.6.6: UI podios por categoria y genero

**Incremento:** INC-5.6 | **Sprint:** SP5
**Patron:** React/Vite frontend sobre pagina existente
**Estimacion total:** 95 min

---

## Diagnostico

`ResultadosPage` ya cubre la tabla de ejecucion de `US-5.6.5`, pero todavia no materializa
la segunda vista del incremento: podios por disciplina y overall agrupados en las 6
divisiones fijas. La API ya expone `ranking` y `overall`; el trabajo es de composicion,
visibilidad y presentacion en frontend.

## Cambios por componente

### 1. Pagina y composicion de datos

- [ ] `frontend/src/pages/organizador/ResultadosPage.tsx` (25 min)
  - consumir `fetchOverall(torneoId)`
  - derivar si la disciplina activa esta finalizada
  - derivar progreso de cierre `(N de M)`
  - renderizar seccion `Podios` bajo la tabla
  - renderizar seccion `Overall` en estado vacio o disponible

### 2. Componentes nuevos de podio

- [ ] `frontend/src/components/organizador/PodiosSection.tsx` (20 min)
  - contenedor reutilizable para 6 paneles
  - titulo, subtitulo y empty state contextual
- [ ] `frontend/src/components/organizador/PanelCategoria.tsx` (15 min)
  - panel por division fija
  - lista de atletas o mensaje "Sin participantes"
- [ ] `frontend/src/components/organizador/FilaPodio.tsx` (15 min)
  - posicion con badges oro/plata/bronce/muted
  - nombre, club, RP y puntos
  - soporte de empates con misma posicion

### 3. Adaptacion de datos

- [ ] mapear ranking + inscriptos a filas de podio por categoria (10 min)
  - 6 categorias fijas en orden canonico
  - join por `atleta_id`
  - `Apellido, Nombre` como etiqueta visible
- [ ] mapear overall + inscriptos a filas overall (5 min)
  - `RP` no disponible en overall -> placeholder `—`
  - `puntos_overall` como valor destacado

### 4. Validacion

- [ ] `npm run build` en `frontend/` (3 min)
- [ ] `npm run lint` en `frontend/` (5 min)
- [ ] documentacion y reporte final (7 min)

## Decisiones clave

- No se rehace el layout general de `ResultadosPage`; se extiende la pagina existente.
- La agrupacion no se infiere dinamicamente: se usa una constante con las 6 categorias canonicas.
- Los empates reutilizan la `posicion` ya provista por backend en `ranking` y `overall`.
- El overall se considera disponible solo si todas las competencias del torneo estan cerradas.
- Para `RP` en overall se mostrara `—`, porque el DTO de overall no expone un resultado realizado unico por atleta.

## Riesgos y mitigaciones

- Si `fetchOverall()` falla antes del cierre completo, la UI no debe bloquear la tabla principal.
- Si una categoria no esta presente en el payload, igualmente debe renderizarse su panel vacio.
- Si hay datos incompletos de inscripto, el podio debe degradar con nombre existente y club `—`.

## Criterio de salida

La fase de implementacion termina cuando:

1. `ResultadosPage` muestra podios por disciplina finalizada.
2. `Overall` informa correctamente estado bloqueado o disponible.
3. La pagina compila y pasa lint en `frontend/`.
