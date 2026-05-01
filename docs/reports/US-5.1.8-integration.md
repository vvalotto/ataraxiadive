# Integracion - US-5.1.8

## Estado

Waiver de automatizacion.

La US requiere montar una page React con dos queries:

- `GET /torneos/{id}/disciplinas`
- `GET /competencia?torneo_id={id}`

El repo no tiene harness E2E/browser configurado para simular esos endpoints y validar
el DOM resultante.

## Flujo critico a validar manualmente

- Torneo con disciplinas y sin competencias: una card por disciplina, estado
  `Competencia pendiente`, auditoria deshabilitada.
- Torneo con competencia para una disciplina: auditoria habilitada solo en esa card.
- Torneo sin disciplinas: mensaje de ausencia de disciplinas configuradas.
- Error en disciplinas o competencias: mensaje de error de carga.

## Gates sustitutos

- `npm run build`
- `npm run lint`
