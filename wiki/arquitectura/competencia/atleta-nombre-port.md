---
title: "Competencia — Port AtletaNombrePort"
type: arquitectura-componente
bc: competencia
capa: domain
tipo_componente: port
responsabilidad: "Resolución de nombre completo de un atleta por ID — lectura cross-BC desde Registro"
interfaces_out:
  - AtletaNombreAdapter
adr_refs: [ADR-005, ADR-007]
last_updated: "2026-05-23"
sources:
  - src/competencia/domain/ports/atleta_nombre_port.py
  - src/competencia/infrastructure/repositories/atleta_nombre_adapter.py
---

# Port AtletaNombrePort

## Responsabilidad

Puerto ABC para resolver el **nombre completo de un atleta** dado su `atleta_id`. Permite que el read model de la grilla muestre nombres legibles en lugar de UUIDs, sin acoplar el BC Competencia al modelo interno del BC Registro.

## Contrato

```python
async def get_nombre(atleta_id: UUID) -> str
```

Retorna `"{nombre} {apellido}"` o un fallback `"Atleta-{id[:8]}"` si no se encuentra.

## Consumidor

`ObtenerGrillaHandler` — al construir el read model de la grilla necesita el nombre del atleta para cada entrada.

## Implementación concreta: AtletaNombreAdapter

Lee directamente `registro.db` (SQLite del BC Registro) via `aiosqlite`:

```sql
SELECT nombre, apellido FROM atletas WHERE atleta_id = ?
```

**Patrón de acceso:** lectura directa de DB cross-BC. Configurado por variable de entorno `REGISTRO_DB_PATH`. Este acoplamiento estructural está documentado como riesgo medio en [[atleta-nombre-port]] (wiki/impacto/).

## Riesgo de cambio

Si la tabla `atletas` en `registro.db` cambia de nombre de columna (`nombre`, `apellido`), este adapter se rompe silenciosamente (devuelve fallback). Riesgo catalogado en [[atleta-nombre-port]].

## Relaciones

**Contenedor:** [[arquitectura/competencia]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/competencia/domain/ports/atleta_nombre_port.py` | Puerto abstracto AtletaNombrePort |
| `src/competencia/infrastructure/repositories/atleta_nombre_adapter.py` | Adapter — lee registro.db via aiosqlite |

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — justifica la separación Registro/Competencia
- [[ADR-007-sqlite-persistencia-bc]] — cada BC tiene su propia DB
