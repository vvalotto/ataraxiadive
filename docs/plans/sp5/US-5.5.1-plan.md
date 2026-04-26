# Plan de Implementacion: US-5.5.1 — Inscripcion completa del atleta + Declarar/Modificar AP

**Historia:** US-5.5.1
**Incremento:** INC-5.5
**Producto:** `frontend` + `identidad` + `registro` + `competencia`
**Estado:** REGULARIZADO POST-IMPLEMENTACION

---

## Alcance

Implementar la UX redefinida del atleta para:

- reemplazar el dashboard unico por shell movil dark con rutas dedicadas;
- permitir inscripcion via wizard de 3 pasos;
- mostrar `Mis inscripciones` por torneo/disciplina;
- permitir declarar o modificar AP desde pantalla dedicada;
- identificar al atleta por nombre y apellido en el portal.

Fuera de alcance de esta iteracion:

- persistencia real de adjuntos del wizard;
- pantalla completa S-07 Mi grilla;
- pantalla completa S-08 Resultados con ranking real;
- deadline de anuncios modelado explicitamente como entidad/evento separado del estado del torneo.

---

## Componentes a Modificar

### Identidad

- [x] `src/identidad/infrastructure/jwt_service.py`
  - agregar `nombre` y `apellido` al payload JWT.

- [x] `frontend/src/api/auth.ts`
- [x] `frontend/src/stores/useAuthStore.ts`
- [x] `frontend/src/types/auth.ts`
  - persistir `nombre` y `apellido` en el store del frontend.

### Registro

- [x] `src/registro/domain/ports/inscripcion_repository_port.py`
- [x] `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py`
  - agregar consulta `find_by_atleta`.

- [x] `src/registro/api/router.py`
  - exponer `GET /registro/atletas/{id}/inscripciones`.

- [x] `frontend/src/api/registro.ts`
  - consumir la consulta de inscripciones del atleta.

### Competencia

- [x] `src/competencia/api/router.py`
  - exponer `POST /competencia/{id}/registrar-ap`.

- [x] `src/competencia/application/commands/registrar_ap.py`
  - permitir actualizacion de AP si la performance sigue en `AnunciadaAP`.
  - rechazar modificacion si la performance ya avanzo.

### Frontend atleta

- [x] `frontend/src/App.tsx`
  - registrar rutas nuevas del portal atleta y redirect legacy.

- [x] `frontend/src/utils/auth.ts`
- [x] `frontend/src/pages/LoginPage.tsx`
- [x] `frontend/src/pages/RegistroPage.tsx`
- [x] `frontend/src/pages/ResetPasswordPage.tsx`
  - alinear redirects al nuevo home `/atleta`.

- [x] `frontend/src/components/atleta/AtletaShell.tsx`
  - shell dark, header sticky y tab bar persistente.

- [x] `frontend/src/pages/atleta/AtletaHomePage.tsx`
- [x] `frontend/src/pages/atleta/AtletaTorneosPage.tsx`
- [x] `frontend/src/pages/atleta/AtletaTorneoDetallePage.tsx`
- [x] `frontend/src/pages/atleta/AtletaInscripcionPage.tsx`
- [x] `frontend/src/pages/atleta/AtletaMisInscripcionesPage.tsx`
- [x] `frontend/src/pages/atleta/AtletaDeclararAPPage.tsx`
- [x] `frontend/src/pages/atleta/AtletaResultadosPage.tsx`
- [x] `frontend/src/pages/atleta/portalData.ts`
  - componer el flujo S-01..S-06 y placeholders navegables para S-08.

---

## Estrategia

1. Resolver identidad visible para destrabar el header del atleta.
2. Exponer consultas/operaciones backend faltantes para que la UX no quede mockeada.
3. Reemplazar la ruta `/atleta/dashboard` por un shell real con pantallas dedicadas.
4. Materializar wizard y AP con el mejor contrato disponible.
5. Validar build y tests focalizados del cambio semantico de AP.

---

## Riesgos / Waivers

- **Waiver UX/documentos:** el wizard exige adjuntos obligatorios, pero en esta iteracion se validan solo a nivel UI; no hay persistencia backend de archivos.
- **Waiver BDD UI:** el repo no tiene harness browser automatizado para montar el portal React end-to-end.
- **Waiver resultados/grilla:** S-07 y S-08 no quedaron completas en esta US; se priorizo alcance minimo navegable y S-04/S-05/S-06.

---

## Quality Gates

- [x] `npm run build` en `frontend/`
- [x] `./.venv/bin/pytest tests/unit/competencia/application/test_registrar_ap_handler.py -q`
- [x] `./.venv/bin/pytest tests/unit/identidad/application/test_handlers.py -q -k jwt_generate_y_verify_payload`
- [ ] automatizacion BDD UI completa
- [ ] evidencia de upload/persistencia documental en backend
