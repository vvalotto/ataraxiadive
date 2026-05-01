# US-ADJ-9.7 - Notas de Implementacion

## Decisiones principales

- `registro` pasa a ser la fuente primaria del AP mediante `Inscripcion.ap_por_disciplina`.
- Se agregó el VO `APDeclarado` para validar valor positivo y derivar la unidad desde la disciplina.
- `registro/api/router.py` ahora expone lectura y escritura de AP por `inscripcion_id`, y `inscriptos-detalle` deja de consultar AP en `competencia`.
- `torneo` valida una precondición externa antes de `cerrar-inscripcion`; si faltan AP, responde `409`.
- `competencia` consume AP desde `registro` a través de `PerformancesAPAdapter`, usando la proyección `competencias_por_torneo` para resolver `torneo_id`.

## Compatibilidad con el modelo anterior

- Se mantuvo el endpoint legado `POST /competencia/{competencia_id}/registrar-ap`.
- Ese endpoint ahora dispara una proyección hacia `registro` mediante callback configurado en `app.py`.
- `GenerarGrillaHandler` hace bootstrap de streams de `Performance` si todavía no existen para atletas con AP en `registro`, evitando que la ejecución posterior falle por ausencia de stream.
- `SQLiteInscripcionRepository` migra en forma lazy agregando la columna `ap_por_disciplina` si la tabla histórica no la tiene.

## Cambios de frontend

- El portal atleta declara AP contra `registro`, sin depender de que la competencia ya exista.
- `InscriptosPanel` carga siempre los inscriptos y habilita edición inline solo en `INSCRIPCION_ABIERTA`.
- `GrillaPanel` comunica explícitamente que la grilla usa AP declarados durante la inscripción.

## Validación realizada

- Backend:
  - `./.venv/bin/python -m pytest tests/integration/registro/test_inscriptos_detalle_endpoint.py tests/integration/torneo/test_cierre_inscripcion_precondition.py tests/unit/torneo/application/test_transiciones_handlers.py tests/unit/competencia/application/test_generar_grilla_handler.py`
- Frontend:
  - `npm run build`
  - `npm run lint`

## Riesgos residuales

- Persisten warnings de deprecación por `datetime.utcnow()` en código previo de `registro`.
- La validación BDD de esta US quedó respaldada por el `.feature` y por tests unitarios/integración; no se agregaron step definitions nuevas en esta iteración.
