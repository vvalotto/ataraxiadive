---
title: "Impacto: AtletaNombrePort / registro.db cross-BC"
type: impacto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/context-map.md
  - wiki/arquitectura/competencia.md
  - wiki/arquitectura/resultados.md
  - wiki/arquitectura/registro.md
componente: AtletaNombrePort
riesgo: medio
bcs_afectados: [registro, competencia, resultados]
tipo: interfaz
---

# Impacto: `AtletaNombrePort` / `registro.db` cross-BC

## Qué es

`AtletaNombrePort` es el puerto de dominio en BC Competencia que resuelve el nombre completo de un atleta dado su ID. Definido en `competencia/domain/ports/atleta_nombre_port.py`.

```python
class AtletaNombrePort(ABC):
    async def get_nombre(self, atleta_id: UUID) -> str: ...
```

La implementación concreta (`AtletaNombreAdapter`, en `competencia/infrastructure/repositories/`) consulta `registro.db` directamente vía `aiosqlite`.

**BC Resultados** tiene un patrón análogo (`AtletaInfoAdapter`) que también consulta `registro.db` para obtener `nombre_completo`, `categoria` y `club`. Ambas son deudas técnicas conocidas respecto al modelo de integración formal.

## BCs afectados

| BC | Rol | Tipo de acceso |
|----|-----|---------------|
| [[arquitectura/registro]] | Propietario de `registro.db` y del aggregate `Atleta` | Upstream implícito (sin evento de salida formal) |
| [[arquitectura/competencia]] | Consumidor — `AtletaNombreAdapter` → `registro.db` | Lectura directa de DB cross-BC |
| [[arquitectura/resultados]] | Consumidor — `AtletaInfoAdapter` → `registro.db` | Lectura directa de DB cross-BC (nombre, categoria, club) |

## Contrato actual (deuda técnica)

Los adaptadores acceden directamente a `registro.db` con una query SQL hardcodeada:

```sql
-- Competencia (AtletaNombreAdapter)
SELECT nombre, apellido FROM atletas WHERE atleta_id = ?

-- Resultados (AtletaInfoAdapter)  
SELECT nombre, apellido, categoria, club FROM atletas WHERE atleta_id = ?
```

Esto viola el principio de aislamiento entre BCs (un BC no accede a la DB de otro — [[arquitectura/context-map]] sección "Principios de integración"). El patrón de puerto/adaptador **contiene** el acoplamiento en la capa de infraestructura, pero no lo elimina.

**Evolución objetivo:** reemplazar por evento `AtletaInscripto` + ACL formal en cada BC consumidor ([[arquitectura/context-map]] sección "Registro → Competencia").

## Riesgo de cambio: medio

### Cambiar el esquema de la tabla `atletas` en Registro

Afecta **ambos adaptadores** (`AtletaNombreAdapter` y `AtletaInfoAdapter`). Un renombrado de columna `nombre`/`apellido`/`categoria`/`club` requiere actualizar las queries SQL en infraestructura de Competencia y Resultados.

### Mover o renombrar `registro.db`

La ruta al archivo se lee de la variable de entorno `REGISTRO_DB_PATH`. Un cambio de ruta requiere actualizar la config de despliegue — no requiere cambios de código.

### Cambiar el tipo de `atleta_id`

Si cambia de UUID a otro tipo, impacta los tres BCs (Registro como propietario + ambos consumidores). Todos usan `str(atleta_id)` en la query.

### Remover un campo consultado (`categoria`, `club`) del aggregate Atleta

Afecta `AtletaInfoAdapter` en Resultados — campo ausente genera error en runtime, no en tiempo de compilación.

## Qué NO se ve afectado

- El BC Identidad y el BC Torneo — no tienen adaptadores que lean `registro.db`.
- El BC Notificaciones — consume eventos de Registro, no lee su DB.
- Los contratos HTTP de Registro — los adaptadores de los BCs consumidores no pasan por la API de Registro.
- El event store de Competencia — `AtletaNombrePort` resuelve solo el nombre para read models; no escribe eventos.

## Cuándo se invoca

`AtletaNombreAdapter.get_nombre()` se invoca en `ObtenerGrillaHandler` de Competencia, que necesita el nombre del atleta para construir el read model de la grilla. Es una consulta de enriquecimiento — no valida lógica de negocio.

## Recorrido en el wiki

```
[[arquitectura/context-map]] sección "Registro → Competencia"
  → [[arquitectura/competencia]] sección "Integraciones"
  → [[arquitectura/registro]]
  → [[arquitectura/resultados]]
  → [[ADR-006-estructura-bc-first]] (regla de imports cross-BC)
```

## ADRs relacionados

- [[ADR-006-estructura-bc-first]] — la única excepción cross-BC permitida es `shared/domain/`; los adaptadores de DB directa son deuda técnica documentada
- [[ADR-007-sqlite-persistencia-bc]] — un SQLite por BC como frontera física; la lectura cross-BC viola esta frontera físicamente
