# AtaraxiaDive

Plataforma web para gestión de torneos de apnea (freediving).

Repositorio del experimento IEDD + Software Limpio aplicado a un producto real.

## Estado del Proyecto

| Subproyecto | Tag | Estado |
|-------------|-----|--------|
| SP1 — La Performance | `v0.2.0` | ✅ Cerrado 2026-03-24 |
| SP2 — La Competencia | `v0.3.0` | ✅ Cerrado 2026-03-28 |
| SP3 — El Torneo | `v0.4.0` | ✅ Cerrado 2026-04-04 |
| SP4 — La Plataforma | `v0.5.0` | ✅ Cerrado 2026-04-18 |
| SP5 — La Puesta en Marcha | `v0.6.0` | ✅ Cerrado 2026-05-01 |
| SP6 — Validación, Ajustes y Despliegue | `v1.0.0` | ⏳ Pendiente |

SP5 completó el ciclo funcional completo: portal del organizador, portal del atleta,
algoritmo de puntaje FAAS, rankings por categoría/género con podios, inscripción
con declaración de AP y resultados provisionales en tiempo real. Cerrado con tag `v0.6.0`.

SP6 (próximo) se enfoca en validación funcional end-to-end, ajustes identificados
durante el uso real y despliegue. Tag planificado: `v1.0.0`.

## Stack

- **Backend:** Python + FastAPI + SQLite (un archivo por Bounded Context)
- **Frontend:** React 19 + TypeScript + Vite 6 + Tailwind v4 + PWA offline-first
- **Arquitectura:** Hexagonal + Event Sourcing (BCs Competencia y Notificaciones)
- **Tests:** pytest + pytest-bdd + Behave · cobertura ≥ 90% en domain/application

## Documentación

- [CLAUDE.md](CLAUDE.md) — memoria del proyecto, convenciones y estado actual
- [Architecture Decision Records](docs/adr/)
- [Arquitectura vigente](docs/architecture/)
- [Trazabilidad RF → US](docs/traceability/matrix.md)
- [Baselines y CM](.cm/baselines/)

## Desarrollo

```bash
# Backend
uv run uvicorn src.app:app --reload --env-file .env

# Frontend
cd frontend && npm run dev

# Tests
pytest tests/unit/
pytest tests/integration/
pytest tests/features/
```
