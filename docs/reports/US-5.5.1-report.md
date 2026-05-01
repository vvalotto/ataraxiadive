# Reporte de Implementacion: US-5.5.1

## Resumen Ejecutivo

- **Historia de Usuario:** US-5.5.1 — Inscripcion completa del atleta + Declarar/Modificar AP
- **Incremento:** INC-5.5
- **Fecha:** 2026-04-26
- **Estado:** IMPLEMENTADO CON DESVIACIONES DECLARADAS

## Componentes Entregados

- [x] JWT extendido con `nombre` y `apellido`.
- [x] Store frontend de autenticacion actualizado al nuevo payload.
- [x] Endpoint de Registro para listar inscripciones del atleta.
- [x] Endpoint de Competencia para registrar AP desde el portal atleta.
- [x] `RegistrarAPHandler` ajustado para permitir modificacion mientras la performance siga `AnunciadaAP`.
- [x] Shell movil dark del atleta con tab bar persistente.
- [x] Nuevas pantallas:
  - Inicio
  - Torneos
  - Detalle del torneo
  - Inscribirme (wizard)
  - Mis inscripciones
  - Declarar AP
  - Resultados (placeholder navegable)

## Comportamiento Entregado

- El atleta ahora ingresa a `/atleta` y no a un dashboard monolitico.
- El portal muestra nombre/apellido/categoria/club en la experiencia principal.
- El flujo de inscripcion sigue la UX aprobada con wizard de 3 pasos.
- `Mis inscripciones` refleja estados `AP pendiente`, `AP declarado` y `AP cerrado`.
- El AP puede declararse o modificarse desde una pantalla dedicada mientras la performance no haya avanzado.

## Validacion Ejecutada

| Gate | Resultado |
|------|-----------|
| `npm run build` en `frontend/` | OK |
| `npm run lint` en `frontend/` | OK |
| `./.venv/bin/pytest tests/unit/competencia/application/test_registrar_ap_handler.py -q` | OK |
| `./.venv/bin/pytest tests/unit/identidad/application/test_handlers.py -q -k jwt_generate_y_verify_payload` | OK |
| `./.venv/bin/codeguard src/identidad src/registro src/competencia --config pyproject.toml --format json --analysis-type pre-commit` | Pendiente / no concluido en este entorno |
| BDD automatizado UI | Waiver |

## Desviaciones / Gaps Residuales

- Los adjuntos del wizard (`certificado medico` y `comprobante de pago`) se validan solo en UI; no se persisten aun en backend.
- La pantalla `Mis resultados` todavia no implementa ranking real ni resultado publicado completo.
- El cierre de AP se infiere desde `torneo.estado`, no desde un deadline explicito provisto por API.
- No se agrego evidencia automatizada browser-level del flujo UI.
- `codeguard` no devolvio salida utilizable dentro de un tiempo razonable durante esta corrida, por lo que no se marca como gate aprobado.

## Archivos Relevantes

- `frontend/src/App.tsx`
- `frontend/src/components/atleta/AtletaShell.tsx`
- `frontend/src/pages/atleta/AtletaHomePage.tsx`
- `frontend/src/pages/atleta/AtletaInscripcionPage.tsx`
- `frontend/src/pages/atleta/AtletaMisInscripcionesPage.tsx`
- `frontend/src/pages/atleta/AtletaDeclararAPPage.tsx`
- `frontend/src/pages/atleta/portalData.ts`
- `src/identidad/infrastructure/jwt_service.py`
- `src/registro/api/router.py`
- `src/competencia/api/router.py`
- `src/competencia/application/commands/registrar_ap.py`

## Criterios de Aceptacion

- [x] El atleta puede navegar por shell movil dark con tabs persistentes.
- [x] Existe detalle de torneo antes del CTA de inscripcion.
- [x] La inscripcion se realiza desde wizard de 3 pasos.
- [x] La UI bloquea el envio si faltan adjuntos.
- [x] Existe pantalla dedicada para declarar/modificar AP.
- [x] El AP puede modificarse antes del cierre visible.
- [x] `Mis inscripciones` muestra estado por disciplina.
- [ ] Persistencia backend de adjuntos obligatorios.
- [ ] Deadline de anuncios modelado explicitamente.
- [ ] Implementacion completa de resultados del atleta.
