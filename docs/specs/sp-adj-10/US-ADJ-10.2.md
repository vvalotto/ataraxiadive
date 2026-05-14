# US-ADJ-10.2: Página "Mis Datos" del atleta — H-01-06 UAT SP6

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-10
**Tipo**: fix funcional backend + frontend
**Agregado principal afectado**: `Atleta`
**Bounded Context**: `registro` + frontend atleta

---

## Descripcion (lenguaje de negocio)

Como **atleta**,
quiero poder ver y editar mis datos personales (nombre, apellido, categoría, club)
desde mi portal
para mantener mi perfil actualizado sin depender de una inscripción activa.

---

## Contexto del dominio

### Problema

Al auto-registrarse, el atleta llega al portal con perfil vacío. Los datos personales
solo se completan al hacer la primera inscripción en un torneo, en el wizard de inscripción.
No existe endpoint `PATCH /registro/atletas/me` ni una pantalla de edición de perfil
independiente del flujo de inscripción (H-01-06, F-01).

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Atleta` | Datos de perfil del atleta (nombre, categoría, club) |
| Command | `ActualizarAtletaCommand` | Actualizar campos del perfil |
| Handler | `ActualizarAtletaHandler` | Cargar atleta por user_id, aplicar cambios y persistir |
| Endpoint | `PATCH /registro/atletas/me` | Actualización parcial del perfil del atleta autenticado |
| Page | `AtletaMisDatosPage` | Formulario de edición de perfil en el portal atleta |

---

## Especificacion del comportamiento

### Precondicion

El atleta está autenticado. Puede tener perfil vacío (sin inscripciones previas) o
con datos ya existentes.

### Postcondicion

Los campos actualizados quedan persistidos. El portal refleja los nuevos datos.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-10.2-01 | Los campos `nombre`, `apellido`, `categoria` y `club` son todos opcionales en el request — los no provistos conservan su valor actual (semántica PATCH). |
| INV-ADJ-10.2-02 | La categoría debe ser un valor válido del enum (`JUNIOR_F`, `JUNIOR_M`, `SENIOR_F`, `SENIOR_M`, `MASTER_F`, `MASTER_M`). |
| INV-ADJ-10.2-03 | El endpoint opera sobre el atleta del usuario autenticado — no acepta `atleta_id` externo. |
| INV-ADJ-10.2-04 | Si el atleta no tiene perfil en `registro.db`, el endpoint retorna 404. |

---

## Criterios de aceptacion

```gherkin
Feature: Edición de perfil del atleta

  Scenario: El atleta actualiza su nombre y club
    Given el atleta está autenticado y tiene perfil en registro
    When navega a "Mis Datos" y actualiza nombre a "Juan" y club a "Club Atlético"
    And guarda los cambios
    Then el portal muestra "Juan" como nombre y "Club Atlético" como club

  Scenario: El atleta corrige su categoría
    Given el atleta tiene categoría SENIOR_M
    When navega a "Mis Datos" y selecciona MASTER_M
    And guarda los cambios
    Then el portal muestra MASTER en la card de perfil del home

  Scenario: La actualización parcial no borra campos no provistos
    Given el atleta tiene nombre "María", apellido "González", categoría SENIOR_F, club "Poseidón"
    When el request PATCH incluye solo club "Neptuno"
    Then el nombre, apellido y categoría permanecen sin cambios
    And el club queda como "Neptuno"

  Scenario: Atleta sin perfil recibe 404
    Given el usuario autenticado no tiene perfil de atleta en registro
    When llama a PATCH /registro/atletas/me
    Then recibe 404

  Scenario: Acceso a "Mis Datos" desde el portal
    Given el atleta está autenticado
    When navega al portal del atleta
    Then existe un acceso visible a "Mis Datos"
    When accede a "Mis Datos"
    Then ve el formulario pre-rellenado con sus datos actuales
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — sigue el mismo patrón de comando/handler/endpoint ya establecido en el BC `registro`.

**Capa(s) afectadas:**
- [x] Application — `ActualizarAtletaCommand` + `ActualizarAtletaHandler`.
- [x] API — `PATCH /registro/atletas/me`.
- [x] Frontend — `AtletaMisDatosPage` + enlace en `AtletaShell`.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/registro/application/actualizar_atleta.py` | Nuevo `ActualizarAtletaCommand` + `ActualizarAtletaHandler`. |
| `src/registro/api/router.py` | Endpoint `PATCH /registro/atletas/me`. |
| `frontend/src/api/registro.ts` | Función `actualizarAtletaMe(data)` que llama `PATCH`. |
| `frontend/src/pages/atleta/AtletaMisDatosPage.tsx` | Nueva página con formulario: nombre, apellido, categoría (selector), club. |
| `frontend/src/components/atleta/AtletaShell.tsx` | Enlace a `/atleta/mis-datos` en navegación. |
| `frontend/src/App.tsx` | Ruta `/atleta/mis-datos`. |

---

## Notas de implementacion

1. `categoria` y `club` se actualizan independientemente de inscripciones activas — el atleta
   puede corregir su perfil en cualquier momento, incluso durante torneos en curso.
2. El género está embebido en la categoría (`JUNIOR_F` → femenino) — no se expone como campo
   independiente en el formulario.
3. El formulario carga el perfil actual con `fetchAtletaMe()` y pre-rellena todos los campos;
   si el perfil está vacío (campos null), los inputs quedan en blanco.
4. Mostrar confirmación visual al guardar exitosamente; mostrar error si el PATCH falla.

---

*Spec creada: 2026-05-14 — hallazgo H-01-06 UAT SP6 F-01*
