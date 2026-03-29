# Diseño de Pruebas UAT — SP2 "La Competencia"

| Campo | Valor |
|-------|-------|
| **Subproyecto** | SP2 — La Competencia |
| **Baseline** | BL-002 |
| **US cubiertas** | US-2.1.1 a US-2.4.2 |
| **Fecha diseño** | 2026-03-29 |
| **Autor** | Victor Valotto |

---

## Objetivo

Verificar de forma observable que el BC Competencia cumple el DoD de SP2:
grilla generada con andariveles, ejecución multi-andarivel con al menos 2 atletas
en paralelo, `CompetenciaFinalizada` disparado automáticamente y ranking calculado
en BC Resultados.

Este UAT genera evidencia para el cierre formal de SP2 y alimenta la retrospectiva de BL-002.

---

## Contexto técnico

En SP2, **tres comandos tienen endpoints HTTP POST** nuevos (vs. SP1 donde ninguno tenía):
- `POST /{id}/ajustar-grilla`
- `POST /{id}/confirmar-grilla`
- `POST /{id}/iniciar`

Los demás comandos (`ConfigurarIntervaloOT`, `GenerarGrilla`, `RegistrarAP`,
`LlamarAtleta`, `RegistrarResultado`, `AsignarTarjeta`, `RegistrarDNS`, `CorregirResultado`)
siguen siendo solo Application layer.

Esto determina la estrategia: **UAT híbrido en dos capas**, igual que SP1, pero
con más superficie HTTP verificable en Capa 2.

---

## Estrategia

```
Capa 1 — Automatizada (pytest)
  Reutiliza tests de integración e2e existentes:
    - test_flujo_e2e_inc21.py  → grilla generada, confirmada, iniciada, ejecución multi-andarivel
    - test_competencia_finalizada_integration.py → CompetenciaFinalizada automático (P-08)
    - test_calcular_ranking_integration.py → ranking calculado
  Evidencia: salida pytest -v

Capa 2 — HTTP (seed + curl al servidor real)
  Seed: ConfigurarIntervaloOT + RegistrarAP ×5 + GenerarGrilla (detiene antes de confirmar)
  HTTP verifica:
    - POST confirmar-grilla (nuevo SP2)
    - POST iniciar (nuevo SP2)
    - GET grilla, GET estado, GET andariveles (nuevos SP2)
    - GET events (tipos SP2 presentes)
    - GET progreso
    - GET /resultados/{id}/ranking (BC Resultados)
  Evidencia: respuestas JSON capturadas
```

---

## Escenario DoD

Disciplina STA con 3 andariveles, 5 atletas — ejercita ejecución multi-andarivel
(andariveles 1, 2 y 3 ocupados en distintos momentos):

| Atleta | AP | Grilla | Flujo | Tarjeta | Andarivel |
|--------|----|--------|-------|---------|-----------|
| A | 300s | pos. 1 | AP → Llamar → Resultado 300s → Tarjeta | Blanca | 1 |
| B | 240s | pos. 2 | AP → Llamar → DNS | — | 2 |
| C | 180s | pos. 3 | AP → Llamar → Resultado 180s → Tarjeta | Blanca | 3 |
| D | 150s | pos. 4 | AP → Llamar → Resultado 160s → Tarjeta → Corregir 155s | Blanca | 1 |
| E | 120s | pos. 5 | AP → Llamar → Resultado 90s → Tarjeta | Roja (black-out, dist. 30s) | 2 |

El atleta E es el último → desencadena `CompetenciaFinalizada` → `CalcularRanking` (política P-08).

**Orden de grilla STA** (mayor AP primero): A(300s) → B(240s) → C(180s) → D(150s) → E(120s).

**Ranking esperado post-ejecución:**
| Posición | Atleta | RP | Tarjeta | En podio |
|----------|--------|----|---------|----------|
| 1 | A | 300s | Blanca | ✅ |
| 2 | D | 155s | Blanca | ✅ |
| 3 | C | 180s | Blanca | ✅ |
| — | B | DNS | — | ❌ |
| — | E | 90s | Roja | ❌ |

> Nota: C(180s blanca) > D(155s blanca) → posiciones: A=1, C=2, D=3.

---

## Capa 1 — Tests Automatizados

**Archivos:**
```
tests/integration/competencia/test_flujo_e2e_inc21.py
tests/integration/competencia/test_competencia_finalizada_integration.py
tests/integration/resultados/test_calcular_ranking_integration.py
```

**Ejecutar:**
```bash
pytest tests/integration/competencia/test_flujo_e2e_inc21.py \
       tests/integration/competencia/test_competencia_finalizada_integration.py \
       tests/integration/resultados/test_calcular_ranking_integration.py -v
```

| ID | Archivo | Qué verifica |
|----|---------|--------------|
| UAT-1.1 | test_flujo_e2e_inc21.py::test_grilla_generada_con_orden_correcto_sta | Grilla STA ordenada mayor AP primero |
| UAT-1.2 | test_flujo_e2e_inc21.py::test_ots_calculados_con_intervalo_correcto | OT = OT_inicio + (pos-1) × intervalo |
| UAT-1.3 | test_flujo_e2e_inc21.py::test_juez_avanza_grilla_atleta_por_atleta_con_adapter_real | Grilla → confirmar → iniciar → llamar ×3, adapter REAL |
| UAT-1.4 | test_competencia_finalizada_integration.py | CompetenciaFinalizada automático al registrar última tarjeta |
| UAT-1.5 | test_calcular_ranking_integration.py | Ranking calculado con posiciones, podio y empates |

**Criterio de aceptación Capa 1:** todos PASSED, 0 FAILED.

---

## Capa 2 — Verificación HTTP

**Setup:**
```bash
# 1. Sembrar flujo parcial en DB real (hasta GenerarGrilla, antes de confirmar)
uv run python tests/uat/sp2/seed_competencia.py

# 2. Levantar servidor (en otra terminal)
uv run fastapi dev src/app.py
```

El seed escribe los IDs en `quality/reports/uat/SP2/uat_ids.json`.

| ID | Endpoint | Método | Verificación | Resultado esperado |
|----|----------|--------|--------------|-------------------|
| UAT-2.1 | `/health` | GET | Status + body | `200 {"status": "ok"}` |
| UAT-2.2 | `/competencia/{id}/estado` | GET | Pre-confirmar | `grilla_confirmada=false, estado=configurada` |
| UAT-2.3 | `/competencia/{id}/grilla` | GET | 5 entradas ordenadas | posicion 1→5, A en pos.1 |
| UAT-2.4 | `/competencia/{id}/confirmar-grilla` | POST | 204 No Content | GrillaConfirmada en Event Store |
| UAT-2.5 | `/competencia/{id}/estado` | GET | Post-confirmar | `grilla_confirmada=true` |
| UAT-2.6 | `/competencia/{id}/iniciar` | POST | 204 No Content | CompetenciaIniciada en Event Store |
| UAT-2.7 | `/competencia/{id}/estado` | GET | Post-iniciar | `estado=en_ejecucion` |
| UAT-2.8 | `/competencia/{id}/andariveles` | GET | Durante ejecución (seed fase 2) | andariveles 1, 2, 3 con atletas asignados |
| UAT-2.9 | `/competencia/{id}/events` | GET | Tipos de performance presentes | APRegistrado, AtletaLlamado, ResultadoRegistrado, TarjetaAsignada, DNSRegistrado, ResultadoCorregido |
| UAT-2.10 | `/competencia/{id}/progreso` | GET | Contadores finales | `total=5, ejecutadas=4, dns_count=1` |
| UAT-2.11 | `/resultados/{id}/ranking` | GET | Ranking calculado | 5 entradas, A pos.1, E tarjeta roja al final |

**Criterio de aceptación Capa 2:** 11/11 con status esperado y valores correctos.

---

## Invariantes verificados end-to-end

| Invariante | Descripción | Cómo se verifica |
|------------|-------------|------------------|
| INV-C-01 | GrillaDeSalidaGenerada solo si IntervaloOTConfigurado previo | Flujo secuencial seed |
| INV-C-02 | GrillaConfirmada solo si grilla generada; irreversible | UAT-2.4 → UAT-2.5 |
| INV-C-03 | CompetenciaIniciada solo si grilla confirmada | UAT-2.6 |
| INV-C-04 | LlamarAtleta solo si Competencia en ejecución | UAT-1.3, seed fase 2 |
| INV-C-05 | Máximo N atletas en paralelo = andariveles configurados | UAT-2.8 |
| P-08 | CompetenciaFinalizada → CalcularRanking automático | UAT-1.4, UAT-2.7 (estado=Finalizada), UAT-2.11 |

---

## Ejecución automatizada

El script `tests/uat/sp2/run_uat.sh` orquesta Capa 1 + seed + Capa 2 y deposita
todos los artefactos en `quality/reports/uat/SP2/`.

```bash
bash tests/uat/sp2/run_uat.sh
```

---

## Artefactos generados

| Archivo | Contenido |
|---------|-----------|
| `design.md` | Este documento |
| `uat_ids.json` | IDs generados por el seed (competencia + atletas) |
| `capa1-pytest.txt` | Salida completa de pytest -v |
| `capa2-http.json` | Respuestas JSON de los 11 endpoints |
| `report.md` | Reporte de ejecución con resultado final |
