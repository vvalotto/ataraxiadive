"""
tracker-cli — CLI para el sistema de tracking de /implement-us.

Permite usar TimeTracker desde Bash, invocando un comando por llamada.
Cada invocación carga el estado desde JSON, opera y persiste.

Uso en phase files:
    .venv/bin/python .claude/tracking/tracker_cli.py init US-1.2.1 "Registrar AP" 3 ataraxiadive
    .venv/bin/python .claude/tracking/tracker_cli.py start-phase 0 "Validación de Contexto"
    .venv/bin/python .claude/tracking/tracker_cli.py end-phase 0
    .venv/bin/python .claude/tracking/tracker_cli.py start-task task_001 "Crear aggregate" domain 20
    .venv/bin/python .claude/tracking/tracker_cli.py end-task task_001 src/competencia/domain/aggregates/performance.py
    .venv/bin/python .claude/tracking/tracker_cli.py end
    .venv/bin/python .claude/tracking/tracker_cli.py status
"""

import sys
import json
import os
from pathlib import Path

# Agregar el directorio padre al path para importar time_tracker
sys.path.insert(0, str(Path(__file__).parent))
from time_tracker import TimeTracker  # noqa: E402


def _find_active_us_id() -> str:
    """Busca el us_id del tracking activo (sin completed_at).

    Returns:
        us_id del tracking activo

    Raises:
        SystemExit: Si no hay tracking activo
    """
    forced_us_id = os.environ.get("TRACKER_US_ID")
    if forced_us_id:
        forced_path = Path(f".claude/tracking/{forced_us_id}-tracking.json")
        if forced_path.exists():
            return forced_us_id

    tracking_dir = Path(".claude/tracking")
    for json_file in tracking_dir.glob("US-*-tracking.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if data.get("timeline", {}).get("completed_at") is None:
                return data["metadata"]["us_id"]
        except (json.JSONDecodeError, KeyError):
            continue
    print("ERROR: No hay tracking activo. Usar 'init' primero.", file=sys.stderr)
    sys.exit(1)


def cmd_init(args: list[str]) -> None:
    """Inicializa tracking para una nueva US.

    Args: us_id us_title us_points producto
    """
    if len(args) < 4:
        print(
            "Uso: init <us_id> <us_title> <us_points> <producto>",
            file=sys.stderr,
        )
        sys.exit(1)
    us_id, us_title, us_points_str, producto = args[0], args[1], args[2], args[3]
    tracker = TimeTracker(
        us_id=us_id,
        us_title=us_title,
        us_points=int(us_points_str),
        producto=producto,
    )
    tracker.start_tracking()
    print(f"[tracking] Iniciado: {us_id} — {us_title}")


def cmd_start_phase(args: list[str]) -> None:
    """Inicia una fase.

    Args: phase_number phase_name
    """
    if len(args) < 2:
        print("Uso: start-phase <number> <name>", file=sys.stderr)
        sys.exit(1)
    us_id = _find_active_us_id()
    tracker = TimeTracker.load(us_id)
    tracker.start_phase(int(args[0]), args[1])
    print(f"[tracking] Fase {args[0]} iniciada: {args[1]}")


def cmd_end_phase(args: list[str]) -> None:
    """Finaliza una fase.

    Args: phase_number [auto_approved]
    """
    if len(args) < 1:
        print("Uso: end-phase <number> [auto_approved=true]", file=sys.stderr)
        sys.exit(1)
    us_id = _find_active_us_id()
    tracker = TimeTracker.load(us_id)
    auto_approved = args[1].lower() != "false" if len(args) > 1 else True
    tracker.end_phase(int(args[0]), auto_approved=auto_approved)
    print(f"[tracking] Fase {args[0]} completada (auto_approved={auto_approved})")


def cmd_start_task(args: list[str]) -> None:
    """Inicia una tarea dentro de la fase activa.

    Args: task_id task_name task_type estimated_minutes
    """
    if len(args) < 4:
        print(
            "Uso: start-task <task_id> <task_name> <task_type> <estimated_minutes>",
            file=sys.stderr,
        )
        sys.exit(1)
    us_id = _find_active_us_id()
    tracker = TimeTracker.load(us_id)
    tracker.start_task(
        task_id=args[0],
        task_name=args[1],
        task_type=args[2],
        estimated_minutes=float(args[3]),
    )
    print(f"[tracking] Tarea iniciada: {args[0]} — {args[1]}")


def cmd_end_task(args: list[str]) -> None:
    """Finaliza una tarea.

    Args: task_id [file_created]
    """
    if len(args) < 1:
        print("Uso: end-task <task_id> [file_created]", file=sys.stderr)
        sys.exit(1)
    us_id = _find_active_us_id()
    tracker = TimeTracker.load(us_id)
    file_created = args[1] if len(args) > 1 else None
    tracker.end_task(args[0], file_created=file_created)
    print(f"[tracking] Tarea completada: {args[0]}")


def cmd_end(_args: list[str]) -> None:
    """Finaliza el tracking de la US activa."""
    us_id = _find_active_us_id()
    tracker = TimeTracker.load(us_id)
    tracker.end_tracking()
    elapsed = tracker.completed_at - tracker.started_at  # type: ignore[operator]
    total_min = int(elapsed.total_seconds() / 60)
    print(f"[tracking] Finalizado: {us_id} — {total_min} min totales")


def cmd_status(_args: list[str]) -> None:
    """Muestra el estado del tracking activo."""
    us_id = _find_active_us_id()
    tracker = TimeTracker.load(us_id)
    status = tracker.get_status()
    elapsed_m = status["elapsed_seconds"] // 60
    phase = status.get("current_phase") or "ninguna"
    completed = status["completed_tasks"]
    total = status["total_tasks"]
    print(
        f"[tracking] {us_id} | fase: {phase} | "
        f"tareas: {completed}/{total} | {elapsed_m} min"
    )


COMMANDS = {
    "init": cmd_init,
    "start-phase": cmd_start_phase,
    "end-phase": cmd_end_phase,
    "start-task": cmd_start_task,
    "end-task": cmd_end_task,
    "end": cmd_end,
    "status": cmd_status,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(
            f"Uso: tracker_cli.py <comando> [args...]\n"
            f"Comandos: {', '.join(COMMANDS)}",
            file=sys.stderr,
        )
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
