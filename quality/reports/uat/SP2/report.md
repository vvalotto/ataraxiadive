# Reporte de Ejecución UAT — SP2 "La Competencia"

| Campo | Valor |
|-------|-------|
| **Fecha ejecución** | 2026-03-29 |
| **Ejecutado por** | Victor Valotto |
| **Branch** | feature/uat-sp2-la-competencia |
| **Commit** | fe27f27 |
| **Diseño de referencia** | `quality/reports/uat/SP2/design.md` |
| **competencia_id** | 889870e9-a771-451d-bea4-11d00fc2a83b |

---

## Capa 1 — Tests Automatizados

**Comandos ejecutados:**
```
pytest tests/integration/competencia/test_flujo_e2e_inc21.py
       tests/integration/competencia/test_competencia_finalizada_integration.py
       tests/integration/resultados/test_calcular_ranking_integration.py -v
```

| ID | Test | Resultado |
|----|------|-----------|
| UAT-1.1 | test_grilla_generada_con_orden_correcto_sta | PASSED |
| UAT-1.2 | test_ots_calculados_con_intervalo_correcto | PASSED |
| UAT-1.3 | test_juez_avanza_grilla_atleta_por_atleta_con_adapter_real | PASSED |
| UAT-1.3b | test_llamar_atleta_falla_si_competencia_no_iniciada | PASSED |
| UAT-1.4a | test_tarjeta_ultimo_atleta_dispara_competencia_finalizada | PASSED |
| UAT-1.4b | test_dns_ultimo_atleta_dispara_competencia_finalizada | PASSED |
| UAT-1.4c | test_sin_port_no_emite_competencia_finalizada | PASSED |
| UAT-1.4d | test_competencia_finalizada_payload_correcto | PASSED |
| UAT-1.5a | test_calcular_ranking_persiste_y_query_devuelve_orden_correcto | PASSED |
| UAT-1.5b | test_calcular_ranking_dns_va_al_final | PASSED |
| UAT-1.5c | test_calcular_ranking_tarjeta_roja_va_al_final | PASSED |
| UAT-1.5d | test_calcular_ranking_empate_posicion_compartida | PASSED |
| UAT-1.5e | test_obtener_ranking_sin_calcular_devuelve_lista_vacia | PASSED |
| UAT-1.5f | test_calcular_ranking_disciplina_dnf | PASSED |

**Resultado Capa 1:** 14/14 PASSED — 3.63s

Ver evidencia completa: `capa1-pytest.txt`

---

## Capa 2 — Verificación HTTP

**Escenario ejecutado:** STA, 3 andariveles, 5 atletas
**competencia_id:** `889870e9-a771-451d-bea4-11d00fc2a83b`

| ID | Endpoint | Status | Valores observados | Resultado |
|----|----------|--------|--------------------|-----------|
| UAT-2.1 | GET /health | 200 | `{"status": "ok"}` | ✅ |
| UAT-2.2 | GET /estado (pre-confirmar) | 200 | `grilla_confirmada=false, estado=Preparacion` | ✅ |
| UAT-2.3 | GET /grilla | 200 | 5 entradas, A pos.1 (300s), B pos.2 (240s)... | ✅ |
| UAT-2.4 | POST /confirmar-grilla | **204** | GrillaConfirmada en stream competencia | ✅ |
| UAT-2.5 | GET /estado (post-confirmar) | 200 | `grilla_confirmada=true, estado=Confirmada` | ✅ |
| UAT-2.6 | POST /iniciar | **204** | CompetenciaIniciada en stream competencia | ✅ |
| UAT-2.7 | GET /estado (post-iniciar) | 200 | `estado=EnEjecucion, grilla_confirmada=true` | ✅ |
| UAT-2.8 | GET /andariveles (post-iniciar) | 200 | 3 andariveles retornados, todos libres al inicio | ✅ |
| UAT-2.9 | GET /events (post-ejecución) | 200 | 20 eventos: 5 AP + 5 Llamado + 4 Resultado + 4 Tarjeta + 1 DNS + 1 Corrección | ✅ |
| UAT-2.10 | GET /progreso | 200 | `total=5, ejecutadas=4, dns_count=1, completadas=5` | ✅ |
| UAT-2.11 | GET /resultados/{id}/ranking | 200 | 5 entradas, A pos.1 (300s), C pos.2 (180s), D pos.3 (155s) | ✅ |

**Resultado Capa 2:** 11/11 OK

Ver evidencia completa: `capa2-http.json`

---

## Observaciones de la ejecución

### Multi-andarivel (INV-C-05)
El flujo de ejecución demostró los 3 andariveles activos simultáneamente:
- Ronda 1: A (and.1), B (and.2), C (and.3) llamados en secuencia sin bloqueo
- A se completa → libera and.1 → D entra en and.1
- B (DNS) → libera and.2 → E entra en and.2 (después de C)
- La grilla asignó andariveles rotando: pos.1→and.1, pos.2→and.2, pos.3→and.3, pos.4→and.1, pos.5→and.2

### Endpoint /events (aclaración de diseño)
El endpoint `GET /competencia/{id}/events` retorna eventos de *performances* (stream por atleta),
no los eventos del aggregate Competencia (stream `competencia-{id}`). Los eventos SP2
`GrillaConfirmada`, `CompetenciaIniciada` y `CompetenciaFinalizada` viven en el stream de
competencia y se evidencian indirectamente:
- `GrillaConfirmada` → verificado en UAT-2.5 (`grilla_confirmada=true`)
- `CompetenciaIniciada` → verificado en UAT-2.7 (`estado=EnEjecucion`)
- `CompetenciaFinalizada` + P-08 → verificado en UAT-2.11 (ranking calculado)

### P-08: CompetenciaFinalizada → CalcularRanking
La política se disparó automáticamente al asignar la tarjeta roja al último atleta (E).
El callback `on_finalizada` fue invocado y CalcularRanking persiste el evento `RankingCalculado`
en `data/resultados.db`. El ranking es consultable inmediatamente vía `GET /resultados/{id}/ranking`.

### Ranking final observado
| Posición | RP | Tarjeta | En podio |
|----------|----|---------|----------|
| 1 | 300s | Blanca | ✅ (Atleta A) |
| 2 | 180s | Blanca | ✅ (Atleta C) |
| 3 | 155s | Blanca | ✅ (Atleta D, corregido de 160s) |
| 4 | — | Roja | ❌ (Atleta E, black-out) |
| 5 | — | DNS | ❌ (Atleta B) |

La corrección de D (160s → 155s) fue respetada en el ranking — RP efectivo = 155s.

---

## DoD SP2 — Verificación Final

- [x] Grilla generada con orden correcto (STA: mayor AP primero — A 300s → E 120s)
- [x] OTs calculados correctamente (OT_inicio + (pos-1) × 9min)
- [x] 3 andariveles activos simultáneamente durante ejecución (INV-C-05)
- [x] `POST /confirmar-grilla` → 204 (nuevo SP2)
- [x] `POST /iniciar` → 204 (nuevo SP2)
- [x] `GET /estado` refleja transiciones: Preparacion → Confirmada → EnEjecucion → Finalizada
- [x] `GET /grilla` retorna 5 entradas ordenadas
- [x] `GET /andariveles` retorna 3 andariveles correctamente
- [x] DNS registrado (Atleta B — `dns_count=1` en progreso)
- [x] Corrección de resultado aplicada y reflejada en ranking (Atleta D: 160s → 155s)
- [x] `CompetenciaFinalizada` disparado automáticamente al completar última performance (P-08)
- [x] `CalcularRanking` ejecutado automáticamente vía callback P-08
- [x] `GET /resultados/{id}/ranking` retorna 5 entradas con posiciones y podio correctos
- [x] `GET /progreso` retorna `total=5, ejecutadas=4, dns_count=1, completadas=5`
- [x] 0 CRITICAL DesignReviewer (verificado en merge de SP-ADJ-02-code — PRs #36, #37, #38)

---

## Resultado Final

**UAT SP2: APROBADO**
