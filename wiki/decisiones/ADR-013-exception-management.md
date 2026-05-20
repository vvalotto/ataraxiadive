---
title: "ADR-013: Jerarquía de excepciones de dominio"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-013-exception-management.md
estado: Aceptada
fecha: 2026-03-26
bcs_afectados: [todos]
---

# ADR-013: Jerarquía de excepciones de dominio

## Decisión

Un archivo `domain/exceptions.py` por BC con jerarquía de dos niveles: `DomainError` como base + subclases específicas por invariante.

## Estructura vigente

```python
# <bc>/domain/exceptions.py
class DomainError(Exception): ...          # base del BC

class EstadoInvalidoParaLlamar(DomainError): ...
class MotivoObligatorio(DomainError): ...
class DistanciaBlackoutObligatoria(DomainError): ...
# ... (crece con cada aggregate)
```

## Reglas de ubicación

| Capa | Excepciones |
|------|------------|
| `<bc>/domain/exceptions.py` | ÚNICA fuente de excepciones de dominio del BC |
| `<bc>/application/` | No define excepciones propias; deja pasar `DomainError` |
| `<bc>/infrastructure/` | Puede definir excepciones técnicas que **no** heredan de `DomainError` |
| `<bc>/api/exception_handlers.py` | Mapea `DomainError` → RFC 7807 (ver [[ADR-012-rfc7807-errores-http]]) |

## Por qué un archivo por BC (no por aggregate)

Las excepciones de un BC son pocas y conviven bien en un archivo plano. Separar por aggregate agrega navegación sin beneficio real. Si supera ~80 excepciones se puede dividir en `exceptions/performance.py` etc.

## Consecuencias vigentes

- El aggregate queda limpio — solo contiene estado, invariantes y comandos.
- `domain/exceptions.py` es el inventario explícito de todos los contratos de error del BC.
- El API layer captura `DomainError` genéricamente sin importar cada subclase.
- Las excepciones de infraestructura (`EventStoreError`) no cruzan hacia el dominio.

## ADRs relacionados

- [[ADR-012-rfc7807-errores-http]] — el mapeo HTTP de estas excepciones
- [[ADR-006-estructura-bc-first]] — la capa `domain/` donde viven estas excepciones
