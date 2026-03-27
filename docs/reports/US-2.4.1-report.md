# Reporte Final — US-2.4.1: Competencia Finalizada (automático)

**Fecha:** 2026-03-27
**Branch:** feature/US-2.4.1-competencia-finalizada
**Incremento:** Inc 2.4 — El Ranking
**Estado:** ✅ COMPLETA

---

## Resumen

Implementación de la política P-08: detección automática del fin de todas las
performances de una disciplina y emisión del evento `CompetenciaFinalizada`.

El sistema detecta el cierre automáticamente cuando `AsignarTarjetaHandler` o
`RegistrarDNSHandler` persisten su evento y, consultando `PerformancesEstadoPort`,
comprueban que ejecutadas + dns_count == total. Si la condición se cumple, carga
el aggregate `Competencia`, llama a `finalizar()` y persiste `CompetenciaFinalizada`.

---

## Artefactos generados

### Nuevos archivos
| Archivo | Descripción |
|---------|-------------|
| `src/competencia/domain/events/competencia_finalizada.py` | Evento de dominio |
| `src/competencia/domain/ports/performances_estado_port.py` | Puerto + DTO |
| `src/competencia/application/_p08_finalizacion.py` | Helper P-08 compartido |
| `src/competencia/infrastructure/repositories/performances_estado_adapter.py` | Adapter |
| `tests/unit/competencia/domain/test_competencia_finalizar.py` | 6 tests unitarios |
| `tests/unit/competencia/application/test_p08_finalizacion.py` | 8 tests de handlers |
| `tests/integration/competencia/test_competencia_finalizada_integration.py` | 4 tests integración |
| `tests/features/US-2.4.1-competencia-finalizada.feature` | 5 escenarios BDD |
| `tests/features/steps/competencia_finalizada_steps.py` | Step definitions |

### Archivos modificados
| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/exceptions.py` | + `CompetenciaNoFinalizable` |
| `src/competencia/domain/aggregates/competencia.py` | + `finalizar()` + `_apply_competencia_finalizada` |
| `src/competencia/application/commands/asignar_tarjeta.py` | + P-08 (port opcional) |
| `src/competencia/application/commands/registrar_dns.py` | + P-08 (port opcional) |
| `src/competencia/api/router.py` | + `get_performances_estado_adapter` dep |
| `docs/traceability/matrix.md` | US-2.4.1 → ✅ Done |

---

## Métricas

| Métrica | Valor |
|---------|-------|
| Tests unitarios totales | 281 |
| Tests integración totales | 79 |
| Tests BDD (escenarios US-2.4.1) | 5 |
| Cobertura domain + application | 98.2% |
| Umbral mínimo | 85% |
| CodeGuard errores | 0 |
| CodeGuard warnings | 2 (pre-existentes) |

---

## Decisiones técnicas

### Helper P-08 extraído a módulo separado
`_p08_finalizacion.py` evita duplicación entre `asignar_tarjeta.py` y
`registrar_dns.py`, y evita el anti-patrón de importar desde otro módulo de
comandos. El prefijo `_` indica que es un detalle de implementación interna
del paquete `application`, no un contrato público.

### Port opcional (backward compat)
`performances_estado: PerformancesEstadoPort | None = None` en ambos handlers.
Patrón idéntico al adoptado en US-2.3.1 para AndarivelesActivosPort: los 15+
test files existentes no requieren modificación.

### INV-C-04 implementado en el aggregate
La verificación `pendientes > 0 → raise CompetenciaNoFinalizable` vive en
`Competencia.finalizar()`, no en el handler. El aggregate es el guardián de
sus invariantes.

---

## Invariantes cubiertos

| Invariante | Descripción | Test |
|-----------|-------------|------|
| INV-C-04 | CompetenciaFinalizada solo cuando TODAS en Ejecutada/DNS | `test_finalizar_rechaza_si_quedan_pendientes` |
| P-08 auto | Disparo automático post-TarjetaAsignada y post-DNSRegistrado | integración |
| Backward compat | Sin port → sin verificación P-08 | `test_sin_port_no_emite_*` |
