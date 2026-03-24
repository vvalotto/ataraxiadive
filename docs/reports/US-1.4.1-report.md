# Reporte de Implementación: US-1.4.1

**Historia de Usuario:** US-1.4.1 — Black-out con Distancia
**Fecha:** 2026-03-23
**Branch:** feature/US-1.4.1-blackout-con-distancia
**BC:** competencia (domain)

---

## Resumen

| Métrica | Valor |
|---|---|
| Tests totales | 189 (+15 nuevos) |
| Coverage | 97.57% |
| Pylint BC competencia | 9.53/10 |
| DesignReviewer CRITICAL | 0 |
| BDD escenarios | 4 (nuevos) |
| Tiempo real (tracker) | ~15 min |
| Estimado | 22 min |

---

## Artefactos creados

| Artefacto | Path |
|---|---|
| US-IEDD | `docs/specs/sp1/US-1.4.1.md` |
| Plan | `docs/plans/sp1/US-1.4.1-plan.md` |
| BDD feature | `tests/features/US-1.4.1-blackout-con-distancia.feature` |
| BDD steps | `tests/features/steps/blackout_con_distancia_steps.py` |
| Quality report | `quality/reports/codeguard/US-1.4.1-quality.json` |

## Artefactos modificados

| Artefacto | Cambio |
|---|---|
| `domain/aggregates/performance.py` | Nueva excepción + campo + propiedad + invariante en `asignar_tarjeta()` |
| `domain/events/tarjeta_asignada.py` | Campo `distancia_blackout: str \| None` |
| `application/commands/asignar_tarjeta.py` | Campo `distancia_blackout` en command y handler |
| `tests/features/US-1.2.4-asignar-tarjeta.feature` | Motivo "black-out" → "tiempo excedido" (regresión) |
| `tests/unit/.../test_performance.py` | +8 tests de dominio, fix motivo regresión |
| `tests/unit/.../test_asignar_tarjeta_handler.py` | +2 tests de handler, fix motivo regresión |
| `tests/integration/.../test_asignar_tarjeta_integration.py` | +2 tests, fix motivo regresión |
| `pyproject.toml` | max_wmc 36→44, max_god_object_lines 380→400 |

---

## Decisiones de diseño

1. **Sin nuevo comando**: black-out es una variante de `AsignarTarjeta`, no un comando separado. La convención `motivo="black-out"` + `distancia_blackout` es suficiente para SP1.

2. **Invariante en el aggregate**: la validación de `distancia_blackout` vive en `Performance.asignar_tarjeta()`, no en el handler — consistente con el resto de invariantes de dominio.

3. **`distancia_blackout` como `str | None` en el evento**: el evento serializa a JSON; se almacena como string para consistencia con otros campos Decimal (`valor_ap`, `valor_rp`).

4. **Ajuste de umbrales**: `max_wmc` y `max_god_object_lines` ajustados al inicio de Inc 1.4 para el crecimiento proyectado del aggregate (política documentada en HITO-4).

---

## Hallazgo: tests existentes con motivo "black-out"

US-1.2.4 tenía 5 tests y 1 feature scenario usando `motivo="black-out"` como string de prueba genérico. Al implementar el invariante RF-EJ-07, estos fallaron. Todos corregidos a `"tiempo excedido"`. Sin impacto en lógica de negocio.

---

*Generado: 2026-03-23 — /implement-us US-1.4.1*
