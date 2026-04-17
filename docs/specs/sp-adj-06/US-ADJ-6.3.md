# US-ADJ-6.3: OCP — Eliminar `inspect.signature` en `_p08_finalizacion.py`

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-06
**Agregado principal afectado**: Política `_p08_finalizacion`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **equipo de desarrollo**,
quiero unificar la firma del callback `on_finalizada` en la política de finalización
para eliminar el uso de reflexión (`inspect.signature`) que viola el Principio
Open/Closed y hace el contrato del callback invisible al sistema de tipos.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Política de aplicación | `_p08_finalizacion` | Orquesta el cierre de una competencia: calcula hash SHA-256, emite `CompetenciaCerrada`, dispara callback de notificación |

### Hallazgo que origina esta US

La revisión SOLID pre-BL-004 (`04-revision-solid.md`, OCP-01) identificó:

```python
# _p08_finalizacion.py — líneas 73-77
sig = inspect.signature(on_finalizada)
params = list(sig.parameters.values())
if len(params) == 1:
    await on_finalizada(competencia_id)
else:
    await on_finalizada(competencia_id, hash_sha256)
```

El código usa reflexión en tiempo de ejecución para detectar cuántos parámetros acepta
el callback y ramifica su comportamiento. Esta es una violación OCP:

- Cualquier cambio en el contrato del callback (agregar un parámetro) obliga a modificar
  `_p08_finalizacion.py`
- El sistema de tipos no puede verificar en compilación que el callback tiene la firma correcta
- El `import inspect` en código de dominio/aplicación es inusual y señala un diseño incorrecto

### Causa del problema

El callback `on_finalizada` tiene dos implementaciones en uso con firmas distintas:
- Una versión `(competencia_id)` — sin hash
- Una versión `(competencia_id, hash_sha256)` — con hash (agregado en INC-4.6)

En lugar de unificar la firma, se usó reflexión para mantener compatibilidad.

---

## Especificación del comportamiento

### Precondición

`_p08_finalizacion.py` usa `inspect.signature(on_finalizada)` para determinar
la firma del callback antes de invocarlo.

### Cambio propuesto

Unificar la firma del callback para que siempre reciba ambos parámetros:

```python
# Tipo del callback unificado
OnFinalizadaCallback = Callable[[CompetenciaId, str], Awaitable[None]]

# _p08_finalizacion.py — sin inspect
await on_finalizada(competencia_id, hash_sha256)
```

Los llamadores que no usan `hash_sha256` lo reciben igualmente e ignoran el parámetro:

```python
# Ejemplo de llamador que no necesita el hash
async def on_finalizada_sin_hash(competencia_id: CompetenciaId, _hash: str) -> None:
    await notificar_cierre(competencia_id)
```

### Postcondición

- `_p08_finalizacion.py` no importa `inspect`
- El callback siempre se llama con `(competencia_id, hash_sha256)` sin condicional
- El tipo `OnFinalizadaCallback` (o equivalente) está definido y documentado
- Todos los llamadores aceptan la firma unificada
- Los tests de finalización de competencia siguen pasando

---

## Criterios de aceptación

```gherkin
Feature: Política de finalización con contrato de callback explícito

  Scenario: Cerrar una competencia invoca el callback con ambos parámetros
    Given una competencia en estado Ejecutando con todas las performances completadas
    When se ejecuta el comando CerrarCompetencia
    Then el callback on_finalizada recibe (competencia_id, hash_sha256)
    And hash_sha256 es una cadena hexadecimal de 64 caracteres

  Scenario: El módulo _p08_finalizacion no usa reflexión
    Given el módulo _p08_finalizacion está cargado
    Then no hay import de inspect en el módulo
    And on_finalizada se invoca siempre con dos parámetros

  Scenario: La política funciona con un callback que ignora el hash
    Given un callback registrado que solo usa competencia_id
    When se cierra una competencia
    Then el callback se ejecuta sin error
    And la competencia queda en estado Cerrada
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — es un refactor de interfaz dentro de la misma capa de aplicación

**Capa(s) afectadas:**
- [x] Application (`competencia/application/_p08_finalizacion.py`)
- [x] Application (llamadores que pasan el callback — verificar en `app.py` y en handlers)

---

## Notas de implementación

1. Buscar todos los lugares donde se define o pasa `on_finalizada` con grep.
2. El type hint del callback puede definirse como `Callable[[CompetenciaId, str], Awaitable[None]]`
   o como `Protocol` si hay múltiples implementaciones.
3. Eliminar `import inspect` del módulo.
4. Ejecutar `pytest tests/unit/competencia/` y `pytest tests/integration/competencia/`
   para confirmar que el cierre de competencia sigue funcionando.

---

*Spec creada: 2026-04-16 — OCP-01 de revisión SOLID pre-BL-004*
