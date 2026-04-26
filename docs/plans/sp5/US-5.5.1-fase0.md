# US-5.5.1 — Fase 0: Validacion de Contexto

**Fecha:** 2026-04-26
**Producto:** `frontend` + `identidad` + `registro` + `competencia`
**Incremento:** INC-5.5 — Portal atleta e inscriptos
**Spec canonica:** `docs/specs/sp5/US-5.5.1.md`

---

## Historia

**US:** US-5.5.1 — Inscripcion completa del atleta + Declarar/Modificar AP

Como **atleta**, quiero **inscribirme a un torneo mediante el flujo UX aprobado y luego declarar o modificar mi AP por disciplina antes del cierre**, para **gestionar mi participacion completa desde el portal del atleta, con navegacion movil y estados claros por torneo y disciplina**.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp5/US-5.5.1.md`
- `docs/design/ux/wireframes-atleta.md`
- `docs/design/ux/flujos-por-rol.md`
- `docs/design/ux/prototipos/prototipo-atleta.html`
- `.work/revision-sp5/04-hallazgos-ux-portal-atleta.md`
- `.work/revision-sp5/03-hallazgos-uat-inc-5.5.md`

---

## Contexto Relevante

### Frontend atleta

- El estado previo estaba concentrado en `frontend/src/pages/atleta/AtletaDashboardPage.tsx`.
- La UX aprobada exige shell movil dark, tab bar persistente y navegacion por pantallas dedicadas.
- El gap critico identificado en revision UX fue `UX-ATL-08`: wizard de inscripcion de 3 pasos.

### Identidad

- El JWT solo exponia `sub`, `email` y `rol`.
- El hallazgo UAT `UAT-5.5-01` pedia nombre/apellido visibles en el portal atleta.

### Registro

- El BC Registro ya exponia `POST /registro/inscripciones` y `GET /registro/atletas/{id}`.
- No existia consulta publica del atleta a sus propias inscripciones.

### Competencia

- El BC Competencia ya tenia `RegistrarAPHandler`.
- El comando no estaba expuesto en `src/competencia/api/router.py`.
- La logica previa rechazaba un segundo AP, pero la spec actualizada exige **declarar o modificar** mientras el plazo siga abierto.

---

## Riesgos Detectados

- El wizard UX pide adjuntos obligatorios, pero el contrato backend actual de Registro no persiste archivos.
- La nocion visible de “deadline de anuncios” no tiene aun un artefacto de dominio explicito en frontend; el estado actual se infiere desde `torneo.estado`.
- Cambiar el comportamiento de `RegistrarAPHandler` puede impactar tests historicos que asumian alta unica.
- El portal atleta nuevo convive con el archivo legacy `AtletaDashboardPage.tsx`, que no debe romper la build.

---

## Quality Gates Esperables

- `npm run build` en `frontend/`
- tests focalizados de `RegistrarAPHandler`
- tests focalizados de JWT payload para nombre/apellido
- validacion BDD documental (waiver de automatizacion UI si no hay harness browser)

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 — Escenarios BDD
2. Fase 2 — Plan de implementacion
3. Fase 3 — Implementacion formal
