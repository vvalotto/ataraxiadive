# US-ADJ-10.1: Edición completa del torneo — H-02-06 UAT SP6

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-10
**Tipo**: fix funcional backend + frontend
**Agregado principal afectado**: `Torneo`
**Bounded Context**: `torneo` + frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero poder editar el nombre, sede, fechas y categorías de un torneo ya creado
para corregir errores de configuración sin necesidad de cancelarlo y crearlo de nuevo.

---

## Contexto del dominio

### Problema

La pantalla de edición del torneo lleva el título "Editar disciplinas" y solo permite
modificar las disciplinas seleccionadas. Los demás campos (nombre, sede, fechas, categorías)
están deshabilitados. No existe un endpoint `PUT /torneos/{id}` ni un comando de dominio
para actualizar los metadatos del torneo.

Si el organizador seleccionó categorías incorrectas al crear el torneo, no tiene forma de
corregirlas desde la UI (H-02-06, F-02).

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Torneo` | Ciclo de vida del torneo y sus metadatos |
| Command | `ActualizarTorneoCommand` | Actualizar nombre, sede, fechas y categorías |
| Handler | `ActualizarTorneoHandler` | Cargar, aplicar cambios y persistir |
| Endpoint | `PUT /torneos/{torneo_id}` | Punto de entrada HTTP para la edición |
| Page | `CrearTorneoPage` | Formulario de creación — debe operar en modo edición |

---

## Especificacion del comportamiento

### Precondicion

El torneo existe y su estado es `CREADO` o `INSCRIPCION_ABIERTA`.

### Postcondicion

Los metadatos del torneo (nombre, sede, fechas, categorías) quedan actualizados con
los valores provistos. Las disciplinas no se ven afectadas por esta operación.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-10.1-01 | Solo se pueden editar torneos en estado `CREADO` o `INSCRIPCION_ABIERTA`. |
| INV-ADJ-10.1-02 | La edición de metadatos no afecta las disciplinas configuradas — tienen endpoint propio. |
| INV-ADJ-10.1-03 | Si el estado no permite edición, el endpoint retorna error y la UI no ofrece el botón. |
| INV-ADJ-10.1-04 | Todos los campos editables son obligatorios — no se admite actualización parcial de metadatos. |

---

## Criterios de aceptacion

```gherkin
Feature: Edición completa del torneo

  Scenario: El organizador edita el nombre y sede de un torneo en CREADO
    Given existe un torneo "Buenos Aires Open 2025" en estado CREADO
    When el organizador abre "Editar torneo" y cambia el nombre a "BA Open 2025 Corregido"
    And cambia la ciudad de sede a "Mar del Plata"
    And guarda los cambios
    Then el panel del torneo muestra "BA Open 2025 Corregido" como nombre
    And la sede muestra "Mar del Plata"

  Scenario: El organizador corrige las categorías de un torneo en INSCRIPCION_ABIERTA
    Given existe un torneo con solo SENIOR seleccionado en estado INSCRIPCION_ABIERTA
    When el organizador abre "Editar torneo"
    Then el formulario tiene todos los campos habilitados y pre-rellenados
    When agrega JUNIOR y MASTER y guarda
    Then el panel del torneo muestra JUNIOR, SENIOR y MASTER

  Scenario: No se puede editar un torneo en EJECUCION
    Given existe un torneo en estado EJECUCION
    When el organizador intenta acceder a "Editar torneo"
    Then el botón de edición no está disponible
    And el endpoint PUT retorna 409 si se invoca directamente

  Scenario: La edición no afecta las disciplinas del torneo
    Given existe un torneo con disciplinas STA y DNF
    When el organizador edita el nombre del torneo
    Then las disciplinas STA y DNF permanecen sin cambios
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — sigue el mismo patrón de comando/handler/endpoint ya establecido en el BC `torneo`.

**Capa(s) afectadas:**
- [x] Domain — método `actualizar()` en aggregate `Torneo`.
- [x] Application — `ActualizarTorneoCommand` + `ActualizarTorneoHandler`.
- [x] API — `PUT /torneos/{torneo_id}`.
- [x] Frontend — `CrearTorneoPage` en modo edición + ruta `/organizador/torneos/:id/editar`.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/torneo/domain/torneo.py` | Agregar método `actualizar(nombre, sede, fecha_inicio, fecha_fin, categorias)` con precondición de estado. |
| `src/torneo/application/actualizar_torneo.py` | Nuevo `ActualizarTorneoCommand` + `ActualizarTorneoHandler`. |
| `src/torneo/api/router.py` | Endpoint `PUT /torneos/{torneo_id}`. |
| `frontend/src/api/torneo.ts` | Función `actualizarTorneo(id, data)` que llama `PUT`. |
| `frontend/src/pages/organizador/CrearTorneoPage.tsx` | Modo dual: carga datos si recibe `torneoId`, llama `PUT` en lugar de `POST`. |
| `frontend/src/pages/organizador/DetalleTorneoPage.tsx` | Botón "Editar torneo" (visible si estado permite); renombrar el link actual. |
| `frontend/src/App.tsx` | Ruta `/organizador/torneos/:torneoId/editar`. |

---

## Notas de implementacion

1. La precondición de estado se valida tanto en dominio (método `actualizar`) como en frontend
   (el botón solo se muestra si `estado` es `CREADO` o `INSCRIPCION_ABIERTA`).
2. El formulario de edición reutiliza `CrearTorneoPage` en modo dual — evita duplicación de lógica
   de validación y layout.
3. La sede se edita como objeto completo (`nombre`, `ciudad`, `pais`) — mismo schema que la creación.
4. No se toca el flujo de asignación de disciplinas: tiene su propio endpoint y pantalla.

---

*Spec creada: 2026-05-14 — hallazgo H-02-06 UAT SP6 F-02*
