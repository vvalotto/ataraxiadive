# AtaraxiaDive

Plataforma web para gestión de torneos de apnea (freediving).

## Estado del Proyecto

| Subproyecto | Estado | Baseline |
|-------------|--------|----------|
| SP1 — La Performance | 🔲 Pendiente | BL-001 |
| SP2 — La Competencia | 🔲 Pendiente | BL-002 |
| SP3 — El Torneo | 🔲 Pendiente | BL-003 |
| SP4 — La Plataforma | 🔲 Pendiente | BL-004 |
| SP5 — La Puesta en Marcha | 🔲 Pendiente | BL-005 |

## Stack

- **Backend:** FastAPI + PostgreSQL
- **Frontend:** React PWA (offline-first para interfaz del juez)
- **Arquitectura:** Hexagonal + Event Sourcing (fase de competencia)

## Documentación

- [Architecture Decision Records](docs/adr/)
- [Estrategia de Desarrollo](docs/plans/)
- [Gestión de la Configuración](.cm/)

## Desarrollo

```bash
docker-compose up
pytest
```

Ver [CLAUDE.md](CLAUDE.md) para convenciones completas.
