# Plan de Implementacion: US-ADJ-7.3 — Cablear P-11 a CompetenciaFinalizada

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-07 |
| **Tipo** | feat de integracion |
| **Branch** | `feature/US-ADJ-7.3-cablear-p11` |
| **BC principal** | composition root (`src/app.py`) |
| **BCs involucrados** | `competencia`, `resultados`, `registro`, `torneo`, `notificaciones` |
| **Estimacion** | 2-3 h |
| **Estado** | Completado |

---

## Alcance

Cablear la politica P-11 en el callback `_on_finalizada` para que, luego de P-08
calcule el ranking, se construya un evento `ResultadosPublicados` y se invoque
`PoliticaP11Handler`.

No se modifican reglas de dominio de los BCs. El cambio vive en el composition root
y en tests de integracion/BDD del wiring.

---

## Decisiones de implementacion

- Reutilizar el `ranking_store` ya creado por `_on_finalizada`; P-11 debe correr
  despues de `_calcular_ranking_por_finalizacion`.
- Construir `ResultadosPublicados.id` como `str(competencia_id)` para mantener
  idempotencia por par `competencia_id:atleta_id`.
- Leer atletas desde `SQLiteAtletaRepository(registro_db_path)`.
- Leer nombre de torneo con `SQLiteTorneoRepository(torneo_db_path)`; fallback
  `"Torneo sin nombre"` si no hay `torneo_id`.
- En `build_p11_handler()`, usar `ResendEmailAdapter` solo si hay `RESEND_API_KEY`;
  si no, usar `LoggingEmailAdapter`, consistente con P-10 y apto para tests/smoke.
- Capturar excepciones de P-11 dentro de `_on_finalizada` para que notificaciones
  no rompan la finalizacion ni P-08/P-09.

---

## Tareas

### 1. BDD

- [x] Crear `tests/features/US-ADJ-7.3-p11-competencia-finalizada.feature`.
- [x] Crear steps BDD para ejecutar el callback de finalizacion con stores temporales.

### 2. Composition root

- [x] Actualizar imports en `src/app.py`:
  - `ObtenerRankingHandler`, `ObtenerRankingQuery`
  - `ResultadoPublicadoAtleta`, `ResultadosPublicados`, `PodioPublicado`
- [x] Ajustar `build_p11_handler()` para fallback a `LoggingEmailAdapter` sin API key.
- [x] Agregar `_obtener_nombre_torneo(torneo_id, torneo_db_path)`.
- [x] Agregar `_notificar_resultados_p11(...)`.
- [x] Llamar P-11 desde `_on_finalizada` despues de P-08/P-09 con `try/except`.

### 3. Tests

- [x] Unit: `tests/unit/test_app_p11_wiring.py`
  - Construye `ResultadosPublicados` desde ranking + atleta + torneo.
  - Fallback de torneo sin nombre.
  - No llama P-11 si ranking esta vacio.
- [x] Integration: `tests/integration/test_p11_callback_integration.py`
  - Camino feliz: 3 emails/notificaciones.
  - Atleta ausente/sin email: registra `NotificacionFallida` y sigue.
  - Idempotencia: dos ejecuciones no duplican `NotificacionEnviada`.
  - Fallo de proveedor no propaga al callback y deja ranking disponible.
- [x] BDD: `tests/features/steps/p11_competencia_finalizada_steps.py`.

### 4. Cierre SP-ADJ-07

- [x] Actualizar `docs/specs/sp-adj-07/US-ADJ-7.3.md` a `Implementada`.
- [x] Marcar `US-ADJ-7.3` en `docs/plans/sp-adj-07/PLAN-SP-ADJ-07.md`.
- [x] Ejecutar DesignReviewer manual post-SP-ADJ-07 con `--config pyproject.toml`.
- [x] Documentar quality gate y reporte final.

---

## Validacion esperada

```bash
.venv/bin/pytest tests/unit/test_app_p11_wiring.py -q
.venv/bin/pytest tests/integration/test_p11_callback_integration.py -q
.venv/bin/pytest tests/features/steps/p11_competencia_finalizada_steps.py -q
.venv/bin/pytest tests/unit/test_app_p10_wiring.py tests/unit/test_app_p09.py tests/unit/test_app_p11_wiring.py tests/integration/test_p11_callback_integration.py tests/features/steps/p11_competencia_finalizada_steps.py --cov=app --cov-config=/tmp/ataraxiadive-empty-coveragerc --cov-report=term-missing --cov-report=json:quality/reports/codeguard/US-ADJ-7.3-coverage.json -q
.venv/bin/codeguard src/app.py --format json
designreviewer src/ --config pyproject.toml
```

Resultado actual:

- Unit/Integration/BDD de US-ADJ-7.3: 12 passed.
- Regresión P-09/P-10/P-11 + cobertura de `src/app.py`: 18 passed, cobertura 96%.
- CodeGuard sobre `src/app.py`: 0 errores, 0 warnings.
- DesignReviewer post-SP-ADJ-07 sobre `src/`: 0 blocking issues, 208 warnings no bloqueantes.

---

## Riesgos

- El repo de `Atleta` exige email valido; para simular sin email conviene usar
  atleta inexistente o stub/repo fake en unit tests, y verificar `NotificacionFallida`.
- P-11 no debe ejecutarse si P-08 falla; el orden dentro de `_on_finalizada` es parte
  del criterio de aceptacion.
- `ResendEmailAdapter` no debe ser obligatorio en entorno local sin `RESEND_API_KEY`.

---

*Creado: 2026-04-19 — cierre SP-ADJ-07*
*Completado: 2026-04-19 — US-ADJ-7.3*
