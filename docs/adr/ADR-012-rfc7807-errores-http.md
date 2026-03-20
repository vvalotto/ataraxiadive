# ADR-012: RFC 7807 (Problem Details) como convención de errores HTTP

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-20 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-006 (estructura BC-first) |

---

## Contexto

FastAPI no impone una convención para el body de las respuestas de error.
Sin una decisión explícita, cada handler resuelve el formato de forma
distinta, lo que produce una API inconsistente y dificulta el manejo
de errores en el cliente.

## Opciones Consideradas

**Opción A — Formato propio:**
`{"error": "codigo_error", "message": "descripción"}`. Simple pero no
estándar — el cliente necesita conocer el contrato propietario.

**Opción B — Solo status code HTTP:**
Sin body de error. Mínimo, pero pierde información útil para el cliente
(¿qué campo falló? ¿qué invariante se violó?).

**Opción C — RFC 7807 (Problem Details for HTTP APIs):**
Estándar IETF. FastAPI lo soporta nativamente. Los clientes pueden
manejar errores de forma genérica o específica según el `type`.

## Decisión

Se adopta **RFC 7807 (Opción C)**.

### Estructura del body de error

```json
{
  "type": "https://ataraxiadive.com/errors/atleta-no-encontrado",
  "title": "Atleta no encontrado",
  "status": 404,
  "detail": "No existe un atleta con id '550e8400-e29b-41d4-a716-446655440000'"
}
```

### Mapeo de excepciones de dominio a HTTP

El mapeo vive en `<bc>/api/exception_handlers.py` — nunca en el dominio.

```python
# competencia/api/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from competencia.domain.exceptions import AtletaNoEncontrado, InvarianteViolado

def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(AtletaNoEncontrado)
    async def atleta_no_encontrado(request: Request, exc: AtletaNoEncontrado):
        return JSONResponse(status_code=404, content={
            "type": "https://ataraxiadive.com/errors/atleta-no-encontrado",
            "title": "Atleta no encontrado",
            "status": 404,
            "detail": str(exc),
        })

    @app.exception_handler(InvarianteViolado)
    async def invariante_violado(request: Request, exc: InvarianteViolado):
        return JSONResponse(status_code=422, content={
            "type": "https://ataraxiadive.com/errors/invariante-violado",
            "title": "Invariante de dominio violado",
            "status": 422,
            "detail": str(exc),
        })
```

### Convención de tipos de error

```
https://ataraxiadive.com/errors/{bc}-{descripcion-kebab-case}

Ejemplos:
  .../errors/atleta-no-encontrado
  .../errors/performance-ya-registrada
  .../errors/tarjeta-invalida
  .../errors/grilla-no-confirmada
```

Los tipos son URIs descriptivas — no necesitan resolver a una URL real.

### Mapeo estándar de excepciones a status codes

| Tipo de excepción | Status HTTP |
|---|---|
| Entidad no encontrada | 404 |
| Invariante de dominio violado | 422 |
| Precondición no cumplida | 409 |
| No autorizado | 403 |
| Error de concurrencia (optimistic) | 409 |
| Error inesperado | 500 |

## Consecuencias

**Positivas:**
- Formato estándar — el cliente frontend puede manejar errores de forma genérica
- `type` como discriminador permite manejo específico por tipo de error
- Consistente entre todos los BCs
- Compatible con la validación automática de Pydantic que ya usa FastAPI

**Negativas / trade-offs:**
- Requiere registrar los exception handlers en cada BC
- Las URIs de `type` son convencionales — no resuelven a documentación real
  (aceptable para v1, se puede agregar documentación de errores en SP4)
