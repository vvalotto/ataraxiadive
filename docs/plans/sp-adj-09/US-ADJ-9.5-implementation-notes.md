# US-ADJ-9.5 - Implementation Notes

**Fecha:** 2026-04-28
**Sprint:** `SP-ADJ-09`
**US:** `US-ADJ-9.5`

---

## Resumen

La pantalla `Resultados` fue reencuadrada dentro del shell dark del organizador,
alineando el header, la jerarquia visual y la composicion entre ranking de
disciplina y overall sin tocar la logica de datos ya entregada por `US-5.6.5`
y `US-5.6.6`.

---

## Cambios implementados

### `ResultadosPage`

- `frontend/src/pages/organizador/ResultadosPage.tsx`
  - se actualizo el subtitulo para expresar:
    - torneo
    - disciplina activa
    - estado del ranking
    - progreso de cierre de disciplinas
  - se reemplazo la accion dominante `Volver` por:
    - `Publicar resultados`
    - `Cambiar torneo`
  - se rehizo el selector de disciplinas con lenguaje visual dark
  - se reorganizo la pantalla para separar mejor:
    - bloque principal de ranking por disciplina
    - bloque secundario de overall

### Tabla de disciplina

- `frontend/src/components/organizador/TablaDisciplinaResultados.tsx`
- `frontend/src/components/organizador/FilaResultado.tsx`
  - se adaptaron bordes, fondos, chips y tipografia al shell dark
  - se mantuvo intacta la logica de join entre:
    - grilla
    - ranking
    - inscriptos

### Podios y overall

- `frontend/src/components/organizador/PodiosSection.tsx`
- `frontend/src/components/organizador/PanelCategoria.tsx`
- `frontend/src/components/organizador/FilaPodio.tsx`
  - se migraron las superficies al sistema dark del organizador
  - se reforzo la separacion visual entre:
    - podios de disciplina
    - overall del torneo
  - se conservaron:
    - empty states
    - paneles por categoria
    - puntos y RP visibles

---

## Conservacion funcional

- se preservo la funcionalidad de tabla por disciplina de `US-5.6.5`
- se preservo la funcionalidad de podios por categoria de `US-5.6.6`
- se preservo el bloqueo/disponibilidad condicional del overall
- no se tocaron:
  - endpoints
  - algoritmos de ranking
  - reglas de dominio

---

## Quality Gates

- `npm run build` en `frontend/`: OK
- `npm run lint` en `frontend/`: falla solo por error preexistente fuera de alcance en:
  - `frontend/src/pages/atleta/portalData.ts:120`

---

## Observaciones

- esta US actua sobre composicion UX y no sobre datos
- el layout final prioriza claridad visual entre disciplina y overall sin forzar
  una reescritura de la tabla real implementada en SP5
- `Publicar resultados` queda expresado visualmente en el header, aunque la US no
  introduce una accion de dominio nueva asociada a ese boton
