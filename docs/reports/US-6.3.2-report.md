# Reporte de Implementación — US-6.3.2

**US:** Formulario de Inscripción — AP en wizard + persistir adjuntos
**Incremento:** INC-6.3 — Ajustes Atleta
**Producto:** registro + frontend
**Branch:** `feature-US-6.3.2-inscripcion-ap-adjuntos`
**Fecha:** 2026-05-07
**Estado:** Implementada, pendiente de PR

---

## Resumen

`US-6.3.2` incorpora AP inline en el wizard de inscripción y persiste los
adjuntos obligatorios de apto médico y constancia de pago en el backend de registro.
La estrategia de storage es mínima y local: `data/adjuntos/{inscripcion_id}/`.

---

## Cambios Implementados

| Área | Archivos | Cambio |
|---|---|---|
| Frontend wizard | `AtletaInscripcionPage.tsx` | AP por disciplina en paso 2, validación, envío best-effort de AP y adjuntos. |
| Frontend API | `frontend/src/api/registro.ts` | Helpers `subirAptoMedico` y `subirConstanciaPago` con `FormData`. |
| Dominio registro | `inscripcion.py` | Campos `apto_medico_path`, `constancia_pago_path` y métodos de adjuntar. |
| Infraestructura | `sqlite_inscripcion_repository.py` | Migración nullable, persistencia y reconstitución de paths. |
| API registro | `router.py` | Endpoints de upload con `UploadFile`, 10 MB máximo y auth `AtletaDep`. |
| Runtime | `.gitignore` | Exclusión de `data/adjuntos/`. |

---

## Tests y Gates

| Gate | Resultado |
|---|---|
| `.venv/bin/pytest tests/unit/registro/test_inscripcion.py tests/integration/registro/test_sqlite_inscripcion_repository.py tests/integration/registro/test_adjuntos_inscripcion_endpoint.py tests/features/steps/inscripcion_ap_adjuntos_steps.py` | ✅ 32 passed |
| `.venv/bin/ruff check` sobre archivos Python tocados | ✅ pasa |
| `npm run build` en `frontend/` | ✅ pasa |
| `npm run lint` en `frontend/` | ✅ pasa |
| BDD | ✅ 8 escenarios ejecutables |

Notas:
- El build mantiene la advertencia conocida de Vite por chunk mayor a 500 kB.
- Los tests muestran warnings existentes por `datetime.utcnow()`.

---

## Criterios de Aceptación

| Criterio | Estado |
|---|---|
| Input AP aparece al seleccionar disciplina | ✅ Cumplido |
| AP inválido bloquea avance al paso 3 | ✅ Cumplido |
| AP vacío no bloquea avance | ✅ Cumplido |
| AP declarado se persiste tras inscripción | ✅ Cumplido |
| Apto médico persistido en backend | ✅ Cumplido |
| Constancia de pago persistida en backend | ✅ Cumplido |
| Archivo > 10 MB rechazado | ✅ Cumplido |
| Inscripciones legacy sin adjuntos siguen funcionando | ✅ Cumplido |

---

## Artefactos

- Spec: `docs/specs/sp6/US-6.3.2.md`
- Plan: `docs/plans/sp6/US-6.3.2-plan.md`
- Feature BDD: `tests/features/US-6.3.2-inscripcion-ap-adjuntos.feature`
- Steps BDD: `tests/features/steps/inscripcion_ap_adjuntos_steps.py`
- Tracking: `.claude/tracking/US-6.3.2-tracking.json`

---

## Notas Operativas

- Las llamadas post-inscripción son best-effort: si AP o adjuntos fallan, la inscripción queda creada y el frontend muestra advertencia.
- El upload usa `FormData`; no se setea `Content-Type` manual para conservar el boundary del browser.
- Los cambios locales en `.work/formacion/` no pertenecen a esta US y no deben incluirse en el commit.

---

*Generado por Fase 9 `/implement-us` — US-6.3.2*
