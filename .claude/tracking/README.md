# Sistema de Tracking — Documentación Técnica

Módulo de tracking automático de tiempo usado por el skill `/implement-us`.
Los archivos `*-tracking.json` en este directorio son generados automáticamente — no editar a mano.

---

## Componentes

| Archivo | Rol |
|---------|-----|
| `time_tracker.py` | Clase `TimeTracker` — lógica central de tracking |
| `tracker_cli.py` | CLI para operaciones desde `/implement-us` |
| `commands.py` | Comandos de alto nivel |
| `reports.py` | Generación de reportes de tiempo |
| `*-tracking.json` | Datos persistidos por US (generados automáticamente) |

---

## Uso desde /implement-us

El skill `/implement-us` inicializa y gestiona el tracker automáticamente en cada fase.
No requiere intervención manual del usuario.

```python
from tracking import TimeTracker

tracker = TimeTracker(us_id="US-1.2.1", us_title="...", us_points=3, producto="ataraxiadive")
tracker.start_tracking()
tracker.start_phase(0, "Validación de Contexto")
# ... trabajo ...
tracker.end_phase(0)
tracker.end_tracking()
```

---

## Notas operativas

- **Bug conocido:** `tracker_cli.py` usa `glob("US-*-tracking.json")` — IDs con prefijo distinto
  a `US-` (ej: `INC-2.0`) no son encontrados. Workaround: usar prefijo `US-` para todos los IDs.
  Ver `docs/plans/WORKFLOW-DESARROLLO.md §5`.

- Los archivos JSON se acumulan indefinidamente. No hay política de archivo automático.

---

*Actualizado: SP-ADJ-5.5 (2026-04-04) — eliminadas referencias a docs/skills inexistentes*
