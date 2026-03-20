# ADR-011: structlog como librería de logging estructurado

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-010 (Docker / Cloud Run) |

---

## Contexto

FastAPI + Uvicorn proveen logging básico en texto plano. Para un sistema
en producción (Cloud Run) los logs necesitan ser estructurados (JSON) para
poder ser parseados, filtrados y correlacionados en Google Cloud Logging.

En desarrollo, el formato JSON es difícil de leer. Se necesita una solución
que diferencie el formato según el entorno.

## Opciones Consideradas

**Opción A — `logging` estándar de Python con formatter JSON:**
Sin dependencias adicionales, pero requiere configuración manual del formatter
y no provee context variables (request_id, user_id) de forma ergonómica.

**Opción B — `structlog`:**
Librería especializada en logging estructurado. Integración nativa con
el `logging` estándar de Python, soporte para context variables, y
renderizado diferenciado por entorno (JSON en prod, texto legible en dev).

## Decisión

Se adopta **structlog (Opción B)**.

### Configuración por entorno

```python
# src/shared/logging.py
import structlog

def configure_logging(env: str) -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if env == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(processors=processors)
```

### Uso en handlers FastAPI

```python
import structlog

log = structlog.get_logger()

async def registrar_performance(cmd: RegistrarPerformanceCommand) -> None:
    log.info("performance.registrar", atleta_id=cmd.atleta_id, competencia_id=cmd.competencia_id)
    ...
```

### Context variables por request

```python
# middleware que agrega request_id a todos los logs del request
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    structlog.contextvars.bind_contextvars(request_id=str(uuid4()))
    response = await call_next(request)
    structlog.contextvars.clear_contextvars()
    return response
```

## Consecuencias

**Positivas:**
- Logs en JSON en producción → parseables en Google Cloud Logging
- Logs legibles en desarrollo sin configuración adicional
- Context variables (request_id, user_id) propagadas automáticamente
- Integración con el `logging` estándar de Python (captura logs de librerías)

**Negativas / trade-offs:**
- Dependencia adicional (`structlog`)
- Requiere configuración inicial en `src/shared/logging.py`
  y llamada a `configure_logging()` al arrancar la app
