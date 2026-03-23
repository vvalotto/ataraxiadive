# Plan de Implementación: US-1.4.1 — Black-out con Distancia

| Campo | Valor |
|-------|-------|
| **US** | US-1.4.1 |
| **Branch** | feature/US-1.4.1-blackout-con-distancia |
| **Fecha** | 2026-03-23 |
| **Estimado total** | 22 min |

---

## Contexto

Extensión de `AsignarTarjeta` (US-1.2.4) para soportar la variante black-out.
Cuando `motivo == "black-out"`, `distancia_blackout` es obligatoria y debe ser > 0 (RF-EJ-07).
No se introducen nuevos puertos, handlers ni endpoints.

---

## Tareas

| # | Tarea | Archivo | Estimado |
|---|-------|---------|----------|
| 1 | Nueva excepción `DistanciaBlackoutObligatoria` | `domain/aggregates/performance.py` | 2 min |
| 2 | Campo `_distancia_blackout` en `Performance.__init__()` | `domain/aggregates/performance.py` | 2 min |
| 3 | Propiedad `distancia_blackout` en `Performance` | `domain/aggregates/performance.py` | 1 min |
| 4 | Extender `asignar_tarjeta()` con param + invariante | `domain/aggregates/performance.py` | 5 min |
| 5 | Extender `_apply_stored()` para leer `distancia_blackout` | `domain/aggregates/performance.py` | 2 min |
| 6 | Campo `distancia_blackout` en `TarjetaAsignada` evento | `domain/events/tarjeta_asignada.py` | 3 min |
| 7 | Campo `distancia_blackout` en `AsignarTarjetaCommand` | `application/commands/asignar_tarjeta.py` | 2 min |
| 8 | Pasar `distancia_blackout` en `AsignarTarjetaHandler.handle()` | `application/commands/asignar_tarjeta.py` | 2 min |
| 9 | US-IEDD spec `docs/specs/sp1/US-1.4.1.md` | `docs/specs/sp1/` | 3 min |

---

## Invariantes nuevos

- `distancia_blackout` obligatoria si `motivo == "black-out"` (RF-EJ-07)
- `distancia_blackout > 0` si presente
- Tarjeta roja sin black-out: sin cambio (INV-P-11 sigue aplicando)

---

## Sin cambios en

- Puertos (`EventStorePort`)
- Infraestructura (`SQLiteEventStore`)
- Router API (`competencia/api/router.py`)
- Otros comandos del dominio
