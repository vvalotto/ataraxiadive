# Reporte de Ejecución UAT — SP1 "La Performance"

| Campo | Valor |
|-------|-------|
| **Fecha ejecución** | 2026-03-24 |
| **Ejecutado por** | Victor Valotto |
| **Branch** | develop |
| **Commit** | aeea01a |
| **Diseño de referencia** | `quality/reports/uat/SP1/design.md` |

---

## Capa 1 — Tests Automatizados

**Comando ejecutado:**
```
pytest tests/integration/competencia/test_flujo_e2e.py -v
```

| ID | Test | Resultado |
|----|------|-----------|
| UAT-1.1 | test_get_events_retorna_traza_completa | PASSED |
| UAT-1.2 | test_get_events_orden_de_secuencia | PASSED |
| UAT-1.3 | test_get_events_campos_obligatorios | PASSED |
| UAT-1.4 | test_get_events_incluye_tipos_esperados | PASSED |
| UAT-1.5 | test_progreso_consistente_con_event_store | PASSED |
| UAT-1.6 | test_blackout_con_distancia_en_event_store | PASSED |
| UAT-1.7 | test_get_events_sin_eventos_retorna_lista_vacia | PASSED |

**Resultado Capa 1:** 7/7 PASSED — 2.30s

Ver evidencia completa: `capa1-pytest.txt`

---

## Capa 2 — Verificación HTTP

**competencia_id usado:** `50b9b02e-6cd3-48a5-a12f-8a04ee553a66`

| ID | Endpoint | Status | Valores observados | Resultado |
|----|----------|--------|--------------------|-----------|
| UAT-2.1 | GET /health | 200 | `{"status": "ok"}` | ✅ |
| UAT-2.2 | GET /competencia/{id}/events | 200 | total_events=20, secuencia 1→20, 6 tipos presentes | ✅ |
| UAT-2.3 | GET /competencia/{id}/progreso | 200 | total=5, ejecutadas=4, dns_count=1, completadas=5 | ✅ |
| UAT-2.4 | GET /competencia/{id}/performance/proximas | 200 | `[]` | ✅ |

**Resultado Capa 2:** 4/4 OK

Ver evidencia completa: `capa2-http.json`

---

## Observaciones de la ejecución

- El Event Store generó **20 eventos** (el diseño estimaba ≥18): los 5 APRegistrado +
  los 15 eventos del flujo de ejecución.
- La secuencia es estrictamente creciente (1→20), confirmando el orden de inserción.
- El evento `ResultadoCorregido` del Atleta D contiene `valor_rp_anterior="55"`
  y `valor_rp_nuevo="53"`, evidenciando la trazabilidad completa de la corrección.
- El evento `TarjetaAsignada` del Atleta E contiene `distancia_blackout="45"`,
  confirmando INV-P-10 serializado correctamente.
- `GET /performance/proximas` retorna `[]` al final del flujo — todos los atletas
  completados, ninguno en estado AnunciadaAP.

---

## DoD SP1 — Verificación Final

- [x] 5 performances ejecutadas (A, B, C, D, E)
- [x] Al menos 1 DNS registrado (Atleta B — evento DNSRegistrado en sequence 10)
- [x] Al menos 1 corrección de resultado (Atleta D: 55m → 53m — sequence 17)
- [x] `GET /events` retorna ≥15 eventos en orden de secuencia (20 eventos, seq 1→20)
- [x] `GET /progreso` retorna `total=5, ejecutadas=4, dns_count=1`
- [x] Los 6 tipos de evento presentes: APRegistrado, AtletaLlamado, ResultadoRegistrado, TarjetaAsignada, DNSRegistrado, ResultadoCorregido
- [x] 0 CRITICAL DesignReviewer (verificado en Inc 1.4 — PR #22)

---

## Resultado Final

**UAT SP1: APROBADO**
