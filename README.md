# AtaraxiaDive

Plataforma web para gestión de torneos de apnea (freediving).

> **Inicio rápido:** Lee [CLAUDE.md](CLAUDE.md) para contexto operativo y decisiones del proyecto.  
> **Navegación documental:** Consulta [Mapa de documentación](docs/inventario/DOCUMENTATION-MAP.md).

## Estado Actual

| Subproyecto | Tag | Estado |
|---|---|---|
| SP1–SP5 (Fases 1-5) | v0.2.0–v0.6.0 | ✅ Completadas |
| **SP6** (Validación, Ajustes, Despliegue) | v1.0.0 | ⏳ En definición |

**Última versión estable:** v0.6.0 (`main` branch) · SP5 completó ciclo funcional.  
**Próxima entrega:** SP6 — validación funcional E2E, ajustes de defectos, despliegue.

## Stack

- **Backend:** Python + FastAPI · SQLite (modelo: BC por archivo)
- **Frontend:** React 19 + TypeScript + Vite 6 + Tailwind v4 · PWA offline-first
- **Arquitectura:** Hexagonal + Event Sourcing (Competencia, Notificaciones)
- **Validación:** pytest + pytest-bdd · cobertura ≥ 90% (domain/ + application/)

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

## Documentación

- [Contexto operativo y decisiones → CLAUDE.md](CLAUDE.md)
- [Mapa de navegación documental](docs/inventario/DOCUMENTATION-MAP.md)
- [Arquitectura vigente](docs/design/architecture.md)
- [Decisiones arquitectónicas](docs/adr/)
- [Trazabilidad RF → US](docs/traceability/matrix.md)
- [Baselines y CM](.cm/baselines/)
