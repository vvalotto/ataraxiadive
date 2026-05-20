---
title: "ADR-012: RFC 7807 como convención de errores HTTP"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-012-rfc7807-errores-http.md
estado: Aceptada
fecha: 2026-03-20
bcs_afectados: [todos]
---

# ADR-012: RFC 7807 como convención de errores HTTP

## Decisión

RFC 7807 (Problem Details for HTTP APIs) como formato estándar de errores. El mapeo HTTP vive en `<bc>/api/exception_handlers.py` — nunca en el dominio.

## Formato vigente

```json
{
  "type": "https://ataraxiadive.com/errors/atleta-no-encontrado",
  "title": "Atleta no encontrado",
  "status": 404,
  "detail": "No existe un atleta con id '...'"
}
```

## Mapeo de excepciones a status codes

| Tipo | Status |
|------|--------|
| Entidad no encontrada | 404 |
| Invariante de dominio violado | 422 |
| Transición de estado inválida | 409 |
| Error de concurrencia (optimistic) | 409 |
| No autorizado | 403 |
| Error inesperado | 500 |

## Consecuencias vigentes

- `<bc>/api/exception_handlers.py` registra handlers específicos por tipo de excepción.
- Handler genérico `DomainError` → HTTP 422 como fallback (ver [[ADR-013-exception-management]]).
- Los tipos de error son URIs descriptivas que no necesitan resolver a una URL real.

## ADRs relacionados

- [[ADR-013-exception-management]] — jerarquía de excepciones que este ADR mapea a HTTP
