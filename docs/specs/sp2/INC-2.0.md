# INC-2.0: Exception Management — domain/exceptions.py + exception_handlers.py

**Estado**: `Done`
**Tipo**: Incremento técnico (refactor + arquitectura)
**Incremento**: INC-2.0 — previo a Inc 2.1
**Subproyecto**: SP2 — La Competencia
**ADR que formaliza**: ADR-013 (organización y jerarquía de excepciones de dominio)
**ADR relacionado**: ADR-012 (RFC 7807 — mapeo HTTP de errores)

---

## Descripción

Incremento técnico que establece el patrón de gestión de excepciones definido
en ADR-013 y lo aplica retroactivamente al código existente de SP1/Inc 2.1.

No introduce comportamiento observable nuevo. El conjunto de tests existente
debe pasar sin modificaciones.

---

## Motivación

Las 7 excepciones de dominio de `Performance` están definidas en
`performance.py`, mezclando la definición del aggregate con sus contratos
de error. El API layer no tiene un mecanismo genérico para traducir errores
de dominio a HTTP — cada endpoint manejaría errores ad-hoc.

Este incremento establece el patrón antes de implementar US-2.1.3 y US-2.1.4,
que agregarán nuevas excepciones al dominio.

---

## Alcance

### Archivos nuevos

```
src/competencia/domain/exceptions.py
src/competencia/api/exception_handlers.py
```

### Archivos modificados

```
src/competencia/domain/aggregates/performance.py   ← eliminar 7 excepciones, actualizar imports
src/competencia/domain/aggregates/competencia.py   ← mover excepciones existentes, actualizar imports
src/app.py                                         ← registrar exception_handlers
tests/unit/competencia/domain/                     ← actualizar imports en tests afectados
tests/integration/competencia/                     ← actualizar imports en tests afectados
```

---

## Especificación

### 1. `domain/exceptions.py`

Jerarquía mínima de dos niveles (ADR-013):

```python
class DomainError(Exception):
    """Base de todas las excepciones de dominio del BC Competencia."""

# ── Performance ───────────────────────────────────────────────────────────
class EstadoInvalidoParaLlamar(DomainError): ...
class EstadoInvalidoParaRegistrarResultado(DomainError): ...
class EstadoInvalidoParaRegistrarDNS(DomainError): ...
class EstadoInvalidoParaAsignarTarjeta(DomainError): ...
class EstadoInvalidoParaCorregirResultado(DomainError): ...
class MotivoObligatorio(DomainError): ...
class DistanciaBlackoutObligatoria(DomainError): ...

# ── Competencia ───────────────────────────────────────────────────────────
class IntervaloNoConfigurado(DomainError): ...
class GrillaYaConfirmada(DomainError): ...
class EstadoInvalidoParaGenerarGrilla(DomainError): ...
```

> Las excepciones de `Competencia` ya existentes en `competencia.py` se
> mueven aquí. Si no existen aún, se agregan como placeholders vacíos
> para que US-2.1.3/2.1.4 los encuentren en su lugar correcto.

### 2. `api/exception_handlers.py`

Mapeo de `DomainError` a RFC 7807 (ADR-012):

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from competencia.domain.exceptions import DomainError

def register_exception_handlers(app: FastAPI) -> None:
    """Registra los exception handlers del BC Competencia en la aplicación."""

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "type": "https://ataraxiadive.com/errors/domain-error",
                "title": "Error de dominio",
                "status": 422,
                "detail": str(exc),
            },
        )
```

### 3. `app.py`

Registrar los handlers al construir la aplicación:

```python
from competencia.api.exception_handlers import register_exception_handlers

app = FastAPI(title="AtaraxiaDive", version="0.1.0")
app.include_router(competencia_router)
register_exception_handlers(app)
```

---

## Invariantes / contratos

- Todos los tests existentes deben pasar sin modificar su lógica de aserción.
- Solo se actualizan imports en los tests — no la lógica.
- Las excepciones conservan sus nombres y mensajes exactos.
- `DomainError` hereda de `Exception` — nada más.
- La capa `application/` no captura ni re-envuelve `DomainError` — la deja pasar.

---

## Testing

**Sin BDD** — este incremento es un refactor de organización sin comportamiento
de usuario observable.

Tests a agregar:
- `tests/unit/competencia/api/test_exception_handlers.py` — verificar que un
  endpoint que lanza `DomainError` retorna HTTP 422 con body RFC 7807 válido.

Los tests existentes de `Performance` y `Competencia` no cambian su lógica —
solo sus imports si referenciaban las excepciones directamente desde `performance.py`.

---

## Criterio de completitud (DoD)

- [ ] `domain/exceptions.py` creado con jerarquía `DomainError` + todas las excepciones existentes
- [ ] `performance.py` sin definiciones de excepción — solo imports desde `domain/exceptions`
- [ ] `competencia.py` sin definiciones de excepción — solo imports desde `domain/exceptions`
- [ ] `exception_handlers.py` creado y registrado en `app.py`
- [ ] `pytest tests/` pasa al 100% sin modificar la lógica de ningún test
- [ ] `designreviewer src/ --config pyproject.toml` — 0 CRITICAL
- [ ] `codeguard src/` — 0 warnings nuevos

---

## Referencias

- `docs/adr/ADR-013-exception-management.md` — decisión arquitectónica
- `docs/adr/ADR-012-rfc7807-errores-http.md` — mapeo HTTP de errores

---

*Redactado: 2026-03-26 — Incremento técnico pre-US-2.1.3*
