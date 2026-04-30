# Plan de Implementacion - US-5.7.1: Mis torneos inscriptos con estado actual

**Incremento:** INC-5.7 | **Sprint:** SP5  
**Producto:** frontend  
**Patron:** React/Vite frontend sobre pagina existente  
**Estimacion total:** 70 min

---

## Diagnostico

`AtletaTorneosPage` ya carga atleta, torneos e inscripciones, y separa los torneos abiertos
que no tienen inscripcion del atleta. Falta materializar la primera seccion "Mis torneos"
con los torneos donde el atleta ya esta inscripto, mostrando estado actual y disciplinas
inscriptas. No se requieren endpoints nuevos.

## Cambios por componente

### 1. Modelo de vista local

- [ ] `frontend/src/pages/atleta/AtletaTorneosPage.tsx` (15 min)
  - derivar `inscripcionesByTorneoId`
  - construir `misTorneos` desde los torneos cuyo `torneo_id` aparece en inscripciones
  - usar `InscriptoDto.disciplinas` como fuente de chips de disciplinas inscriptas
  - ordenar `misTorneos` por `fecha_inicio` ascendente

### 2. Render de seccion "Mis torneos"

- [ ] `frontend/src/pages/atleta/AtletaTorneosPage.tsx` (20 min)
  - renderizar la seccion antes de "Inscripciones abiertas"
  - mostrar nombre, fecha, sede/ciudad, badge de estado y chips de disciplinas
  - navegar a `/atleta/torneos/:torneoId` al abrir la card
  - mostrar estado vacio: "Aun no estas inscripto en ningun torneo."

### 3. Ajuste de filtros existentes

- [ ] `frontend/src/pages/atleta/AtletaTorneosPage.tsx` (10 min)
  - mantener `abiertos` excluyendo torneos ya inscriptos
  - evitar duplicacion visual de torneos entre "Mis torneos" e "Inscripciones abiertas"
  - revisar si "Proximos" debe seguir sin cambios segun spec

### 4. Consistencia visual

- [ ] `frontend/src/pages/atleta/AtletaTorneosPage.tsx` (10 min)
  - reutilizar estilos dark existentes del portal atleta
  - usar labels de `getEstadoTorneoLabel`
  - mantener texto legible en mobile y sin layout shift

### 5. Validacion

- [ ] revisar feature `tests/features/US-5.7.1-mis-torneos.feature` (5 min)
- [ ] `npm run build` en `frontend/` (5 min)
- [ ] `npm run lint` en `frontend/` si el entorno lo permite (5 min)

## Decisiones clave

- No se agrega endpoint backend: la seccion se deriva de `fetchAtletaMe`,
  `listarInscripcionesDeAtleta` y `fetchTorneos`.
- La seccion "Mis torneos" usa las disciplinas de la inscripcion del atleta, no todas las
  disciplinas configuradas para el torneo.
- Los estados del torneo se renderizan con `getEstadoTorneoLabel`, respetando el mapeo
  normalizado actual (`EJECUCION` -> "En ejecucion", `CERRADO` -> "Cerrado", etc.).
- La validacion BDD queda como feature documentada/manual porque el repo no tiene harness
  browser automatizado para montar esta pantalla.

## Riesgos y mitigaciones

- Si una inscripcion referencia un torneo que ya no aparece en `fetchTorneos`, se ignora
  para evitar una card incompleta.
- Si una inscripcion no trae disciplinas, la card mostrara "Por definir" como degradacion
  consistente con la seccion existente.
- Si `listarDisciplinasTorneo` falla para torneos abiertos, no debe afectar "Mis torneos",
  porque sus chips salen de la inscripcion.

## Criterio de salida

La implementacion termina cuando:

1. "Mis torneos" aparece como primera seccion.
2. Los torneos inscriptos muestran estado y disciplinas inscriptas.
3. Los torneos inscriptos no aparecen en "Inscripciones abiertas".
4. El estado vacio se muestra cuando el atleta no tiene inscripciones.
5. `frontend` compila correctamente.
