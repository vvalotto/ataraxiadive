# Plan de Implementación — US-6.3.2

**US:** Formulario de Inscripción — AP en wizard + persistir adjuntos
**Incremento:** INC-6.3 — Ajustes Atleta
**Producto:** registro + frontend
**Patrón:** Hexagonal DDD BC-first + React/Vite frontend
**Estimación total:** 3h 20min
**Estado:** ✅ COMPLETADO
**Fecha completado:** 2026-05-07

---

## Alcance

La US agrega AP inline dentro del wizard de inscripción y persistencia mínima de
adjuntos de inscripción: apto médico y constancia de pago.

No se introduce port de storage ni abstracción nueva. La persistencia de archivos queda
en filesystem local `data/adjuntos/{inscripcion_id}/`, según la spec.

---

## Componentes a Modificar

### 1. Frontend — Wizard de inscripción

- [x] `frontend/src/pages/atleta/AtletaInscripcionPage.tsx` (45 min)
  - Agregar estado `apPorDisciplina`.
  - Mostrar input AP bajo cada disciplina seleccionada en paso 2.
  - Descartar AP al deseleccionar disciplina.
  - Validar AP ingresado antes de avanzar al paso 3.
  - Permitir AP vacío.
  - Tras crear inscripción, persistir APs y adjuntos best-effort.
  - Mostrar advertencia no bloqueante si falla una llamada posterior a la inscripción.

- [x] `frontend/src/api/registro.ts` (15 min)
  - Agregar `subirAptoMedico(inscripcionId, archivo)`.
  - Agregar `subirConstanciaPago(inscripcionId, archivo)`.
  - Usar `FormData` sin header `Content-Type` manual.
  - Reutilizar token actual y manejo 401.

### 2. Backend — Dominio registro

- [x] `src/registro/domain/aggregates/inscripcion.py` (20 min)
  - Agregar `apto_medico_path: str | None`.
  - Agregar `constancia_pago_path: str | None`.
  - Agregar `adjuntar_apto_medico(path)`.
  - Agregar `adjuntar_constancia_pago(path)`.
  - Validar path no vacío.

### 3. Backend — Persistencia SQLite

- [x] `src/registro/infrastructure/repositories/sqlite_inscripcion_repository.py` (35 min)
  - Migrar schema con columnas nullable `apto_medico_path` y `constancia_pago_path`.
  - Incluir campos en `INSERT OR REPLACE`.
  - Reconstituir inscripciones legacy con `None`.
  - Mantener compatibilidad con datos existentes.

### 4. Backend — API uploads

- [x] `src/registro/api/router.py` (45 min)
  - Agregar endpoints:
    - `POST /registro/inscripciones/{id}/apto-medico`
    - `POST /registro/inscripciones/{id}/constancia-pago`
  - Aceptar `UploadFile`.
  - Validar tamaño máximo 10 MB.
  - Retornar 404 si no existe inscripción.
  - Guardar en `data/adjuntos/{inscripcion_id}/`.
  - Actualizar aggregate y persistir.
  - Mantener auth `AtletaDep`.

- [x] `.gitignore` (5 min)
  - Agregar `data/adjuntos/`.

---

## Tests y Validación

### Unitarios

- [x] `tests/unit/registro/test_inscripcion.py` (20 min)
  - Adjuntar apto médico válido.
  - Adjuntar constancia de pago válida.
  - Rechazar path vacío.

### Integración

- [x] `tests/integration/registro/test_sqlite_inscripcion_repository.py` (25 min)
  - Persistir y recuperar paths de adjuntos.
  - Migrar fila legacy sin columnas de adjuntos.

- [x] `tests/integration/registro/test_adjuntos_inscripcion_endpoint.py` (35 min)
  - Upload apto médico 200.
  - Upload constancia de pago 200.
  - Archivo > 10 MB devuelve 413.
  - Inscripción inexistente devuelve 404.

### Frontend gates

- [x] `npm run build` en `frontend/` (10 min)
- [x] `npm run lint` en `frontend/` (5 min)

### Backend gates focalizados

- [x] `pytest tests/unit/registro tests/integration/registro` (15 min)

---

## Métricas de Validación

| Gate | Resultado |
|---|---|
| `.venv/bin/pytest tests/unit/registro/test_inscripcion.py tests/integration/registro/test_sqlite_inscripcion_repository.py tests/integration/registro/test_adjuntos_inscripcion_endpoint.py tests/features/steps/inscripcion_ap_adjuntos_steps.py` | ✅ 32 passed |
| `.venv/bin/ruff check` sobre archivos Python tocados | ✅ pasa |
| `npm run build` | ✅ pasa |
| `npm run lint` | ✅ pasa |
| BDD | ✅ 8 escenarios |

---

## Artefactos

- [x] `tests/features/US-6.3.2-inscripcion-ap-adjuntos.feature`
- [ ] `docs/reports/US-6.3.2-report.md`
- [x] `docs/traceability/matrix.md`

---

## Riesgos y Mitigaciones

- **Riesgo:** `UploadFile` requiere `python-multipart` en runtime.
  **Mitigación:** verificar dependencia al correr tests; si falta, documentar bloqueo o agregar dependencia si el proyecto ya acepta uploads.

- **Riesgo:** llamadas post-inscripción pueden fallar y dejar inscripción parcial.
  **Mitigación:** mantener comportamiento best-effort y mostrar advertencia; no revertir inscripción.

- **Riesgo:** filesystem local no es storage definitivo.
  **Mitigación:** implementar alcance mínimo pedido y documentar path relativo como decisión v1.0.

---

## Definition of Done

- [x] AP inline visible y validado en paso 2.
- [x] Inscripción creada aunque AP esté vacío.
- [x] AP declarado se persiste tras inscripción cuando es válido.
- [x] Adjuntos se suben y quedan referenciados en la inscripción.
- [x] Inscripciones legacy sin adjuntos siguen cargando.
- [x] Tests focalizados pasan.
- [x] `npm run build` y `npm run lint` pasan.
- [ ] Reporte final en `docs/reports/US-6.3.2-report.md`.

---

*Generado: 2026-05-07 — Fase 2 /implement-us US-6.3.2*
