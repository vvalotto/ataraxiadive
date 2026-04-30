# Implementation Notes - US-5.7.1

## Cambio implementado

`AtletaTorneosPage` ahora muestra la seccion "Mis torneos" como primera seccion de la
pantalla Torneos del portal atleta.

## Comportamiento

- Carga el atleta autenticado con `fetchAtletaMe`.
- Carga inscripciones del atleta con `listarInscripcionesDeAtleta`.
- Carga torneos con `fetchTorneos`.
- Construye `misTorneos` cruzando `torneo_id` entre torneos e inscripciones.
- Muestra chips de disciplinas desde `InscriptoDto.disciplinas`, que representa lo que
  el atleta efectivamente inscribio.
- Mantiene "Inscripciones abiertas" excluyendo torneos donde el atleta ya esta inscripto.
- Mantiene "Proximos" sin cambios funcionales.

## Archivos modificados

- `frontend/src/pages/atleta/AtletaTorneosPage.tsx`

## Artefactos generados

- `docs/plans/sp5/US-5.7.1-fase0.md`
- `docs/plans/sp5/US-5.7.1-plan.md`
- `docs/plans/sp5/US-5.7.1-test-notes.md`
- `tests/features/US-5.7.1-mis-torneos.feature`
- `quality/reports/codeguard/US-5.7.1-quality.txt`

## Validacion

- `npm run build`: PASS.
- `npx eslint src/pages/atleta/AtletaTorneosPage.tsx`: PASS.
- `npm run lint`: FAIL por hallazgos existentes fuera del scope de esta US:
  - `frontend/src/pages/juez/GrillaPage.tsx`
  - `frontend/src/components/organizador/JuecesPanel.tsx`

## Waiver

No se agrego test automatizado de componente porque el frontend no tiene harness browser
o testing-library configurado para montar paginas con React Query y mocks de API. Los
escenarios BDD quedan documentados para validacion manual.
