# Notas de Implementacion — US-5.1.4

## Endpoint agregado

Se agrego `POST /competencia/{competencia_id}/generar-grilla` en
`src/competencia/api/router.py`.

Body:

```json
{
  "disciplina": "DNF",
  "ot_inicio": "2026-04-20T09:00:00Z",
  "andariveles": 1
}
```

El endpoint delega en `GenerarGrillaHandler`, reutilizando:

- `PerformancesAPAdapter`
- `DisciplinaDescriptorAdapter`
- `EventStorePort`

## Frontend

El tab `Grilla` de `DetalleTorneoPage` ahora renderiza `GrillaPanel`.

Componentes nuevos:

- `ConfigurarGrillaForm`: intervalo OT, primer OT y accion `Generar grilla`.
- `TablaGrilla`: tabla con drag HTML nativo para reordenar posiciones.
- `GrillaPanel`: orquesta disciplina, competencia, estado, grilla, ajustes y confirmacion.

API client extendido:

- `crearCompetencia`
- `generarGrilla`
- `ajustarGrilla`
- `confirmarGrilla`

## Validaciones

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
- `npm run lint`: falla por `frontend/.vite/deps/react-router-dom.js`, artefacto generado
  preexistente fuera de `src`.
- `python3 -m py_compile`: aprobado para router y tests nuevos.
- `pytest`: bloqueado por dependencia Python faltante `aiosqlite`.

## Decisiones

- No se agrego `@dnd-kit/core`; el reordenamiento usa Drag and Drop nativo para evitar
  modificar dependencias durante la US.
- El primer OT se envia como ISO datetime construido desde el campo `time` de la UI.
