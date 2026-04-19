# Reporte de Implementacion: US-ADJ-7.1

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-07 |
| **Tipo** | Fix de dominio |
| **Branch** | `feature/US-ADJ-7.1-corregir-dns` |
| **Estado** | Implementada |
| **Fecha** | 2026-04-19 |

---

## Resumen

Se agrego la transicion explicita `DNS -> ResultadoRegistrado` para corregir un DNS
registrado por error. El nuevo comando emite `ResultadoCorregidoTrasDNS` con motivo
obligatorio y deja la `Performance` apta para continuar con `AsignarTarjeta`.

La politica P-08 no se dispara desde este comando; sigue limitada a los handlers que
cierran performances (`RegistrarDNSHandler` y `AsignarTarjetaHandler`).

---

## Componentes modificados

- `src/competencia/domain/events/resultado_corregido_tras_dns.py`
  - Nuevo evento de dominio auditable.

- `src/competencia/domain/aggregates/performance.py`
  - Nuevo metodo `corregir_resultado_tras_dns()`.
  - Validacion de estado `DNS`, motivo obligatorio y `valor_rp >= 0`.

- `src/competencia/domain/aggregates/performance_events.py`
  - Factory `crear_resultado_corregido_tras_dns()`.

- `src/competencia/domain/aggregates/performance_state.py`
  - Replay del evento hacia `ResultadoRegistrado`.

- `src/competencia/application/commands/corregir_resultado_tras_dns.py`
  - Command y handler de aplicacion.

- `src/competencia/api/router.py`
  - Endpoint `POST /competencia/{competencia_id}/performances/{performance_id}/corregir-resultado-tras-dns`.

---

## Tests y validaciones

| Validacion | Resultado |
|------------|-----------|
| `pytest tests/unit/competencia/domain/test_performance_corregir_dns.py tests/unit/competencia/application/test_corregir_resultado_tras_dns_handler.py tests/integration/competencia/test_corregir_resultado_tras_dns_integration.py` | 17 passed |
| `pytest tests/features/steps/corregir_resultado_tras_dns_steps.py tests/unit/competencia/domain/test_performance_corregir_dns.py tests/unit/competencia/application/test_corregir_resultado_tras_dns_handler.py tests/integration/competencia/test_corregir_resultado_tras_dns_integration.py` | 22 passed · 2 warnings pytest-bdd |
| `black` sobre archivos tocados | passed |
| `codeguard` sobre componentes modificados/agregados | errors=0 · warnings=0 |
| Cobertura focalizada de US | total domain/application 73.85% · archivos US no API 83.72% |

Reporte de calidad:
`quality/reports/codeguard/US-ADJ-7.1-quality.json`

Evidencias de quality gate:
- `quality/reports/codeguard/US-ADJ-7.1-codeguard-raw.json`
- `quality/reports/codeguard/US-ADJ-7.1-coverage.json`

Observacion de quality gate: `codeguard` se ejecuto sobre los componentes
modificados/agregados por la US y no reporta errores ni warnings. La cobertura
queda documentada como `CON_WARNINGS`: el total `domain+application` incluye deuda
previa de modulos fuera de alcance, y los archivos tocados arrastran cobertura baja
preexistente en `Performance` y replay state.

Observacion BDD: se agrego el cableado de steps
`tests/features/steps/corregir_resultado_tras_dns_steps.py` para ejecutar el feature
`tests/features/US-ADJ-7.1-corregir-resultado-tras-dns.feature`. Las warnings son de
`pytest-bdd`/`gherkin` y del tag no registrado `@US-ADJ-7.1`; no bloquean la US.

---

## Criterios de aceptacion

- [x] Corrige una performance en `DNS` y la deja en `ResultadoRegistrado`.
- [x] Emite `ResultadoCorregidoTrasDNS` con `valor_rp`, `unidad`, `registrado_por` y `motivo_correccion`.
- [x] Rechaza correcciones desde `Ejecutada` y `Llamada`.
- [x] Rechaza motivo vacio.
- [x] El replay reconstruye el estado `ResultadoRegistrado`.
- [x] El flujo `DNS -> correccion -> tarjeta blanca` finaliza en `Ejecutada`.
- [x] El endpoint HTTP retorna `204` en camino feliz y `409` en estado invalido.
