# Integracion - US-5.1.9

## Estado

Waiver de automatizacion.

La US requiere montar `JuecesPanel` con tres fuentes:

- `GET /torneos/{id}/disciplinas`
- `GET /usuarios?rol=JUEZ`
- `GET /competencia?torneo_id={id}` + `GET /competencia/{id}/estado`

El repo no tiene harness browser/DOM para simular esas queries y validar el DOM resultante.

## Flujo critico a validar manualmente

- Disciplina con competencia en estado `GrillaGenerada` o posterior: selector habilitado.
- Disciplina sin competencia: selector deshabilitado y mensaje operativo.
- Disciplina con juez existente pero sin grilla: juez visible y selector bloqueado.
- Error de carga en grillas/competencias: mensaje de error.

## Gates sustitutos

- `npm run build`
- `npm run lint`
