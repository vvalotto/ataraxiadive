# AtaraxiaDive

Plataforma web para gestión de torneos de apnea (freediving).

Repositorio del experimento IEDD + Software Limpio aplicado a un producto real.

## Estado del Proyecto

| Subproyecto | Estado | Baseline |
|-------------|--------|----------|
| SP1 — La Performance | ✅ Cerrado | BL-001 |
| SP2 — La Competencia | ✅ Cerrado | BL-002 |
| SP3 — El Torneo | 🔄 Implementación funcional completa, cierre formal pendiente | BL-003 |
| SP4 — La Plataforma | 🔲 Pendiente | BL-004 |
| SP5 — La Puesta en Marcha | 🔲 Pendiente | BL-005 |

SP3 ya dejó implementados `Torneo`, `Registro`, `Identidad`, auth por rol y el flujo de overall por torneo (`US-3.5.1` a `US-3.5.3`).

## Stack

- **Backend:** FastAPI + SQLite
- **Frontend:** React PWA (offline-first para interfaz del juez)
- **Arquitectura:** Hexagonal + Event Sourcing en BCs que lo requieren

## Documentación

- [Architecture Decision Records](docs/adr/)
- [Estrategia de Desarrollo](docs/plans/)
- [Gestión de la Configuración](.cm/)

## Desarrollo

```bash
uv run fastapi dev src/app.py
./.venv/bin/pytest
```

Ver [CLAUDE.md](CLAUDE.md) para convenciones completas.
