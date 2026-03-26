# ADR-013: Organización y jerarquía de excepciones de dominio

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-03-26 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-012 (RFC 7807 — mapeo HTTP), ADR-006 (estructura BC-first) |

---

## Contexto

Durante SP1 las excepciones de dominio se definieron en el mismo archivo del
aggregate (`performance.py`). Al cerrar Inc 2.1 se detectó que:

1. `performance.py` contenía 7 clases de excepción junto al aggregate — mezcla
   responsabilidades y contribuye al tamaño del archivo.
2. No existía una jerarquía base que permitiera al API layer capturar excepciones
   de dominio de forma genérica (ADR-012 lo asumía pero no estaba formalizado).
3. El patrón iba a replicarse en cada aggregate sin una guía explícita.

ADR-012 ya decidió que el mapeo HTTP vive en `<bc>/api/exception_handlers.py`
y referenció `competencia.domain.exceptions` como origen. Este ADR formaliza
el lado del dominio: dónde se definen, cómo se organizan y cómo se tipan.

## Opciones Consideradas

**Opción A — Excepciones en el mismo archivo del aggregate (estado actual):**
Simple de encontrar, pero mezcla la definición del aggregate con sus contratos
de error. Escala mal: a medida que crecen los aggregates, el archivo crece con
ellos por dos razones independientes.

**Opción B — Un `exceptions.py` por BC bajo `domain/`:**
`competencia/domain/exceptions.py` concentra todas las excepciones del BC.
Separa claramente el aggregate de sus contratos de error. Es el origen que
ADR-012 ya anticipó.

**Opción C — Un `exceptions.py` por aggregate:**
`domain/exceptions/performance_exceptions.py`, `competencia_exceptions.py`, etc.
Más granular, pero agrega navegación sin beneficio real: las excepciones de un BC
son pocas y conviven bien en un archivo plano.

## Decisión

Se adopta **Opción B**: un archivo `domain/exceptions.py` por BC, con una
jerarquía mínima de dos niveles.

### Jerarquía de excepciones

```python
# competencia/domain/exceptions.py

class DomainError(Exception):
    """Base de todas las excepciones de dominio del BC Competencia.

    Permite al API layer capturar cualquier error de dominio con un
    handler único (ver ADR-012) sin conocer cada subclase.
    """

# ── Violaciones de invariantes de Performance ─────────────────────────────
class EstadoInvalidoParaLlamar(DomainError): ...
class EstadoInvalidoParaRegistrarResultado(DomainError): ...
class EstadoInvalidoParaRegistrarDNS(DomainError): ...
class EstadoInvalidoParaAsignarTarjeta(DomainError): ...
class EstadoInvalidoParaCorregirResultado(DomainError): ...
class MotivoObligatorio(DomainError): ...
class DistanciaBlackoutObligatoria(DomainError): ...

# ── Violaciones de invariantes de Competencia ─────────────────────────────
class EstadoInvalidoParaGenerarGrilla(DomainError): ...
class GrillaYaConfirmada(DomainError): ...
# ... (crece con cada aggregate)
```

### Categorías de excepción de dominio

| Categoría | Ejemplos | HTTP (ADR-012) |
|-----------|----------|----------------|
| Transición de estado inválida | `EstadoInvalidoParaLlamar` | 409 |
| Invariante de datos violado | `MotivoObligatorio`, `DistanciaBlackoutObligatoria` | 422 |
| Entidad no encontrada | `PerformanceNoEncontrada` | 404 |
| Regla de negocio cross-aggregate | `GrillaYaConfirmada` | 409 |

### Reglas de ubicación

```
<bc>/domain/exceptions.py     ← ÚNICA fuente de excepciones del dominio del BC
<bc>/application/             ← NO define excepciones propias; deja pasar DomainError
<bc>/infrastructure/          ← puede definir excepciones técnicas (ej: EventStoreError)
                                 que NO heredan de DomainError
<bc>/api/exception_handlers.py ← mapea DomainError (y subclases) a RFC 7807 (ADR-012)
```

**El dominio no importa nada de infraestructura** — esta regla (CLAUDE.md §6) se mantiene.
Las excepciones de infraestructura (`EventStoreError`, `ConnectionError`) no cruzan
hacia el dominio; el application layer las captura y las convierte si corresponde.

### Handler genérico en el API layer

```python
# competencia/api/exception_handlers.py
from competencia.domain.exceptions import DomainError

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Captura genérica — mapea cualquier DomainError a HTTP 422.
    Para excepciones específicas (404, 409) registrar handlers más específicos
    que tienen prioridad sobre este handler genérico.
    """
    return JSONResponse(status_code=422, content={
        "type": "https://ataraxiadive.com/errors/domain-error",
        "title": "Error de dominio",
        "status": 422,
        "detail": str(exc),
    })
```

Los handlers específicos (404 para not-found, 409 para conflictos de estado)
se registran adicionalmente cuando el BC los necesita.

## Consecuencias

**Positivas:**
- Aggregate raíz limpio — solo contiene estado, invariantes y comandos de dominio.
- `domain/exceptions.py` como inventario explícito de todos los contratos de error
  del BC — fácil de auditar y documentar.
- El API layer puede capturar `DomainError` genéricamente sin importar cada subclase
  (complementa ADR-012).
- Consistente con la regla de capas de ADR-006: las excepciones de dominio no
  dependen de nada fuera de `domain/`.

**Negativas / trade-offs:**
- Requiere un pequeño refactor en SP1 (mover 7 excepciones de `performance.py`).
- Al crecer el BC, `exceptions.py` puede volverse largo. Si supera ~80 excepciones
  se puede dividir en `exceptions/performance.py`, `exceptions/competencia.py` etc.
  Por ahora un archivo plano es suficiente.

**No resuelto por este ADR:**
- Internacionalización de mensajes de error (diferido a SP4 con el frontend).
- Excepciones de validación de Pydantic en el API layer — ya manejadas por
  FastAPI nativamente con HTTP 422 en formato RFC 7807.
