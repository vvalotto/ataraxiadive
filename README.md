# AtaraxiaDive

Plataforma web para gestión de torneos de apnea (freediving).

Repositorio del experimento IEDD + Software Limpio aplicado a un producto real.

## Estado del Proyecto

| Subproyecto | Estado | Baseline |
|-------------|--------|----------|
| SP1 — La Performance | ✅ Cerrado | BL-001 |
| SP2 — La Competencia | ✅ Cerrado | BL-002 |
| SP3 — El Torneo | ✅ Cerrado | BL-003 |
| SP4 — La Plataforma | ✅ Cerrado | BL-004 |
| SP5 — La Puesta en Marcha | 🔄 En construcción | BL-005 draft |

SP4 transformó el sistema de API-only a plataforma completa: frontend React PWA
offline-first para jueces, BC Notificaciones con email real, auditoría con hash
SHA-256 y exportación CSV/JSON. Cerrado el 2026-04-18 con tag `v0.5.0`.

SP5 está en curso con objetivo MVP Demo (`v1.0.0` planificado): ciclo completo
crear torneo → inscribir atletas → generar grilla → ejecutar disciplina →
publicar resultados y podios. El alcance vigente está en
[`docs/plans/sp5/PLAN-SP5.md`](docs/plans/sp5/PLAN-SP5.md) y el estado operativo
en [`.cm/baselines/BL-005-draft.md`](.cm/baselines/BL-005-draft.md).

## Stack

- **Backend:** FastAPI + SQLite
- **Frontend:** React PWA (offline-first para interfaz del juez)
- **Arquitectura:** Hexagonal + Event Sourcing en BCs que lo requieren

## Documentación

- [Fuentes canónicas](docs/CANONICAL-SOURCES.md)
- [Estado y baselines](.cm/baselines/)
- [Plan vigente SP5](docs/plans/sp5/PLAN-SP5.md)
- [Arquitectura vigente](docs/architecture/)
- [Architecture Decision Records](docs/adr/)
- [Estrategia de Desarrollo](docs/plans/)
- [Gestión de la Configuración](.cm/)

## Desarrollo

```bash
uv run fastapi dev src/app.py
./.venv/bin/pytest
```

Ver [CLAUDE.md](CLAUDE.md) para convenciones completas.
