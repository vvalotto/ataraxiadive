# US-ADJ-6.1: Investigar y resolver import cross-BC en `exportar_resultados.py`

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-06
**Agregado principal afectado**: `ExportarResultadosHandler`
**Bounded Context**: `resultados` (posible acoplamiento con `competencia`)

---

## Descripción (lenguaje de negocio)

Como **equipo de desarrollo**,
quiero verificar si `exportar_resultados.py` importa el aggregate `Performance` de
`competencia/domain/` en runtime
para confirmar o descartar una violación de frontera entre BCs antes de cerrar BL-004.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Query Handler | `ExportarResultadosHandler` | Proyecta resultados exportables desde eventos de Competencia |

### Hallazgo que origina esta US

En la revisión SOLID pre-BL-004 (`04-revision-solid.md`, LAZY-01) se detectó:

```python
# resultados/application/queries/exportar_resultados.py
def _performance_a_resultado_final(...):
    from src.competencia.domain.aggregates.performance import Performance
```

Un import dentro del cuerpo de una función indica que hacerlo a nivel de módulo causa
un `ImportError` circular o un acoplamiento no deseado. En la arquitectura hexagonal de
este proyecto, `resultados/application/` no debería importar aggregates de `competencia/domain/`.

La comunicación entre BCs debe ocurrir a través de puertos (`domain/ports/`), no mediante
imports directos entre capas de dominio.

---

## Especificación del comportamiento

### Precondición

`_performance_a_resultado_final` en `exportar_resultados.py` contiene un lazy import de
`Performance` de `competencia/domain/aggregates/`.

### Análisis requerido

Antes de cualquier cambio, determinar qué se usa de `Performance`:

- **Opción A:** el import existe solo para type hints → mover bajo `TYPE_CHECKING` (sin ciclo real, sin cambio de comportamiento)
- **Opción B:** el import instancia `Performance` → rediseñar: proyectar los datos
  necesarios desde el event store de Competencia mediante un puerto, sin cruzar la frontera del BC
- **Opción C:** el import es un artefacto sin uso real → eliminar directamente

### Postcondición

Uno de los siguientes:
- a) El import está bajo `TYPE_CHECKING` y no genera ciclo en runtime
- b) `resultados/application/` no importa nada de `competencia/domain/` — la exportación usa el event store de Competencia como puerto opaco
- c) El import fue eliminado por innecesario

En cualquier caso: `madge src/` reporta 0 ciclos cross-BC y `architectanalyst` confirma
que no hay dependencias `resultados → competencia/domain/aggregates`.

### Invariante arquitectónico

> `resultados/application/` puede importar de `resultados/domain/` y de `shared/domain/`.
> No puede importar de `competencia/domain/aggregates/` directamente.

---

## Criterios de aceptación

```gherkin
Feature: Sin acoplamiento cross-BC en exportar_resultados

  Scenario: El módulo de exportación no importa aggregates de Competencia en runtime
    Given el módulo exportar_resultados.py está cargado
    When se ejecuta la exportación de resultados de un torneo
    Then no se importa Performance de competencia/domain/aggregates/ en runtime
    And madge src/ reporta 0 ciclos cross-BC

  Scenario: La exportación sigue funcionando correctamente
    Given un torneo con disciplinas cerradas y ranking calculado
    When se solicita exportación en formato JSON y CSV
    Then los resultados son idénticos a los producidos antes del refactor
    And el hash SHA-256 de las disciplinas cerradas está presente en el JSON
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] Posiblemente — si el import instancia `Performance`, hay que definir el puerto de acceso al event store de Competencia desde Resultados

**Capa(s) afectadas:**
- [x] Application (`resultados/application/queries/exportar_resultados.py`)
- [ ] Domain (solo si se crea un nuevo puerto)
- [ ] Infrastructure (solo si se crea un nuevo adaptador)

---

## Notas de implementación

1. Leer `_performance_a_resultado_final` completo y todas sus llamadas antes de actuar.
2. Si la solución es Opción B, el nuevo puerto debe vivir en `resultados/domain/ports/`
   y el adaptador en `resultados/infrastructure/`.
3. Ejecutar `madge src/ --circular` antes y después para confirmar la eliminación del ciclo.
4. Los tests existentes de `ExportarResultadosHandler` son la red de seguridad — deben
   seguir pasando sin modificación.

---

*Spec creada: 2026-04-16 — LAZY-01 de revisión pre-BL-004*
