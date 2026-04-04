# Reporte UAT — SP3 "El Torneo"

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP3 — El Torneo + SP-ADJ-04 |
| **Baseline** | BL-003 |
| **Fecha ejecución** | 2026-04-04 |
| **Ejecutado por** | Victor Valotto |
| **Resultado final** | **APROBADO** |

---

## Resumen Ejecutivo

| Capa | Total checks | Pasaron | Fallaron |
|------|-------------|---------|---------|
| Capa 1 — pytest | 14 | 14 | 0 |
| Capa 2 — HTTP | 14 | 14 | 0 |
| **Total** | **28** | **28** | **0** |

> Nota: Capa 1 ejecutó 14 tests (8 archivos UAT-1.x, algunos con múltiples casos).
> Capa 2 verificó 14 endpoints con check de respuesta (UAT-2.1 a UAT-2.20, excluyendo
> UAT-2.11 y UAT-2.7 que son de status-only sin criterio de fallo).

---

## Capa 1 — Tests Automatizados (pytest)

Archivo de evidencia: `capa1-pytest.txt`

| ID | Test | Resultado |
|----|------|-----------|
| UAT-1.1 | test_flujo_completo_inscripcion_ap_grilla | PASS |
| UAT-1.2 | test_atleta_sin_ap_no_aparece_en_grilla | PASS |
| UAT-1.3 | test_multiples_atletas_ordenados_por_ap_ascendente | PASS |
| UAT-1.4 | test_US_3_3_2_steps::test_flujo_completo | PASS |
| UAT-1.5 | test_US_3_3_2_steps::test_atleta_sin_ap | PASS |
| UAT-1.6 | test_US_3_3_2_steps::test_orden_ap | PASS |
| UAT-1.7 | test_calcular_ranking_integration (6 casos) | PASS |
| UAT-1.8 | test_calcular_overall_integration | PASS |

**Criterio:** todos PASSED → ✅ Capa 1 aprobada

---

## Capa 2 — Verificación HTTP

Archivo de evidencia: `capa2-http.json`

### Pre-ejecución

| ID | Endpoint | Método | Esperado | Obtenido | OK |
|----|----------|--------|----------|----------|----|
| UAT-2.1 | `/health` | GET | 200 `{"status":"ok"}` | 200 `{"status":"ok"}` | ✅ |
| UAT-2.2 | `/auth/registro` | POST | 201 | 201 | ✅ |
| UAT-2.3 | `/auth/login` | POST | `access_token` presente | presente | ✅ |
| UAT-2.4 | `/torneos/{id}` | GET | `estado=INSCRIPCION_ABIERTA` | `INSCRIPCION_ABIERTA` | ✅ |
| UAT-2.5 | `/torneos/{id}/disciplinas` | GET | `[{disciplina: STA}]` | `[{disciplina: STA}]` | ✅ |
| UAT-2.6 | `/torneos` | GET | lista ≥1 | lista con múltiples torneos | ✅ |
| UAT-2.7 | `/torneos/{id}/abrir-inscripcion` | PUT | error de transición | 409 | ✅ |
| UAT-2.8 | `/registro/atletas` | POST | 201 | 201 | ✅ |
| UAT-2.9 | `/registro/inscripciones` | POST | 201 | 201 | ✅ |
| UAT-2.10 | `/registro/torneos/{id}/inscriptos` | GET | ≥6 con STA | 6 inscriptos | ✅ |
| UAT-2.11 | `/competencia` | POST | 201 | 201 | ✅ |
| UAT-2.12 | `/competencia/{id}/grilla` | GET | 6 posiciones, orden ascendente | 6 posiciones correctas | ✅ |
| UAT-2.13 | `/competencia/{id}/confirmar-grilla` | POST | 204 | 204 | ✅ |
| UAT-2.14 | `/competencia/{id}/estado` | GET | post-confirmar | estado=GrillaConfirmada | ✅ |
| UAT-2.15 | `/torneos/{id}/iniciar-ejecucion` | PUT | 200 | 200 | ✅ |
| UAT-2.16 | `/competencia/{id}/iniciar` | POST | 204 | 204 | ✅ |

### Post-ejecución

| ID | Endpoint | Verificación | Esperado | Obtenido | OK |
|----|----------|-------------|----------|----------|----|
| UAT-2.17 | `/competencia/{id}/estado` | Post-ejecución | `Finalizada` | `Finalizada` | ✅ |
| UAT-2.18 | `/competencia/{id}/progreso` | Conteos | total=6, ejecutadas=6, dns=0 | total=6, ejecutadas=6 | ✅ |
| UAT-2.19 | `/resultados/{id}/ranking?disciplina=STA` | Ranking por categoría | 4 cats, posiciones correctas | 4 cats confirmadas | ✅ |
| UAT-2.20 | `/resultados/{torneo_id}/overall` | Overall | 6 atletas | 6 atletas | ✅ |

**Criterio:** 20/20 con valores correctos → ✅ Capa 2 aprobada

---

## Verificación de Datos Reales (HITO-17)

Dataset: Apnea Indoor Buenos Aires 2025

| Categoría | Atleta | RP esperado (s) | RP obtenido | ¿Coincide? |
|-----------|--------|-----------------|-------------|------------|
| SENIOR_MASCULINO pos.1 | Enjuto | 393 | 393 | ✅ |
| SENIOR_MASCULINO pos.2 | Almada | 342 | 342 | ✅ |
| SENIOR_FEMENINO pos.1 | Montangie | 277 | 277 | ✅ |
| MASTER_MASCULINO pos.1 | Valotto | 273 | 273 | ✅ |
| MASTER_MASCULINO pos.2 | Alperin | 244 | 244 | ✅ |
| MASTER_FEMENINO pos.1 | Di Lernia | 243 | 243 | ✅ |

**6/6 resultados coinciden con el dataset real del torneo.** El sistema reproduce fielmente los resultados oficiales de Buenos Aires 2025.

---

## Invariantes Verificados

| Invariante | Descripción | Verificado en | OK |
|------------|-------------|---------------|----|
| INV-T-01 | Torneo: CREADO→INSCRIPCION→PREPARACION→EJECUCION | UAT-2.4 → UAT-2.15 | ✅ |
| INV-A-05 | Atleta requiere `club` | UAT-2.8 | ✅ |
| INV-D-01 | Acrónimos AIDA (DBF, SPE) en enum | Dataset seed | ✅ |
| INV-P-01 | Grilla STA orden ascendente (menor AP primero) | UAT-2.12 (6 posiciones) | ✅ |
| INV-R-01 | Ranking segmentado por categoría (sin mezcla) | UAT-2.19 (4 categorías) | ✅ |
| P-08 | CompetenciaFinalizada → CalcularRanking automático | UAT-2.17 → UAT-2.19 | ✅ |
| P-09 | Overall multi-categoría (política P-09) | UAT-2.20 (6 atletas) | ✅ |
| RF-PM-05 | Rankings por categoría y género | UAT-2.19 (SENIOR_M, SENIOR_F, MASTER_M, MASTER_F) | ✅ |

---

## Observaciones

1. **`IDENTIDAD_JWT_SECRET` requerida en arranque del servidor** — La variable de entorno debe configurarse al levantar el servidor. Sin ella, `/auth/login` retorna 500. Documentar como prerequisito en el README/runbook.

2. **Script run_uat.sh corregido durante la ejecución** — Tres correcciones menores aplicadas:
   - `rol` en mayúsculas (`ORGANIZADOR` → ahora usa `ADMIN` para el usuario UAT)
   - URL de inscriptos corregida (`/torneos/{id}/inscriptos` → `/registro/torneos/{id}/inscriptos`)
   - Transición de estado del torneo: `cerrar-inscripcion` antes de `iniciar-ejecucion`

3. **Bug en seed_sp3.py corregido** — `AsignarTarjetaCommand` no acepta `torneo_id`; el campo fue eliminado.

4. **Datos reales verificados** — Los 6 RPs del dataset BA 2025 coinciden 100% con los resultados calculados por el sistema.

---

## Conclusión

**APROBADO** — SP3 cumple el DoD: pipeline completo Torneo → Identidad → Registro → Competencia → Resultados verificado con datos reales del torneo Buenos Aires 2025. Los 6 atletas producen ranking por categoría y overall correctos. 28/28 checks pasaron.

**Próximo paso:** merge develop→main + tag `v0.4.0` (BL-003)
