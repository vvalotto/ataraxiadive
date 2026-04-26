# Hallazgos UAT — Portal Atleta + Declaración de AP
## INC-5.5 · US-5.5.1 (reimplementación) + US-5.5.2

**Fecha:** 2026-04-26
**Contexto:** UAT funcional del portal del atleta completo — flujo inscripción, declaración de AP
y vista organizador de inscriptos (`INC-5.5`, rama `feature-US-5.5.2-inscriptos-ap`, post-merge).
**Servidores usados:** backend `http://127.0.0.1:8000` · frontend `http://127.0.0.1:5173`
**Usuario UAT:** `uat.atleta@test.com` / `Atleta2026!` (rol: atleta)
**Atleta:** Victor Valotto · `atleta_id = aaaaaaaa-0000-0000-0000-000000000099`

---

## Resumen ejecutivo

Se identificaron **13 hallazgos** durante la sesión UAT. Todos fueron corregidos en la misma
sesión. Ninguno bloqueó permanentemente la operación del torneo, pero varios habrían impedido
el uso del portal sin intervención técnica.

La causa raíz más recurrente fue la **confusión de identidades cross-BC** (`usuario_id` del
BC Identidad usado incorrectamente como `atleta_id` del BC Registro). Este defecto se replicó
en múltiples páginas del portal.

---

## Tabla de hallazgos

| ID | Área | Severidad | Estado |
|----|------|-----------|--------|
| H-01 | Portal home — BC Identidad/Registro mismatch | Alta | Cerrado |
| H-02 | Inscripción — BC Identidad/Registro mismatch | Alta | Cerrado |
| H-03 | Portal home — categoría muestra código interno | Baja | Cerrado |
| H-04 | Inscripción — MASTER no puede seleccionar SENIOR | Media | Cerrado |
| H-05 | Torneos — torneo ya inscripto sigue visible | Media | Cerrado |
| H-06 | Declarar AP — botón inactivo sin retroalimentación | Baja | Cerrado |
| H-07 | Declarar AP — placeholder vacío en distancia | Baja | Cerrado |
| H-08 | Declarar AP — validación no rechaza valor 0 | Baja | Cerrado |
| H-09 | Declarar AP — error `[object Object]` al guardar | Alta | Cerrado |
| H-10 | Declarar AP — unidad enviada en mayúsculas | Alta | Cerrado |
| H-11 | Portal home — AP "Sin declarar" tras guardar exitosamente | Alta | Cerrado |
| H-12 | Declarar AP — import faltante en router backend (500) | Alta | Cerrado |
| H-13 | Declarar AP — campo prerellenado muestra 0 en vez de AP guardado | Media | Cerrado |

---

## Detalle de hallazgos

---

### H-01 — Portal home no carga: BC Identidad/Registro mismatch

**Síntoma:**
Al ingresar al portal del atleta se muestra: _"No se pudo cargar el portal del atleta."_

**Causa raíz:**
El frontend usaba `userId` obtenido de `useAuthStore` (proveniente del JWT `sub`) como
`atleta_id` para llamar a `listarInscripcionesDeAtleta`. Sin embargo, son UUIDs distintos:
`usuario_id` pertenece al BC Identidad y `atleta_id` pertenece al BC Registro.
Que ambos sean UUIDs no implica que sean iguales — el BC Registro genera su propio ID al
crear el perfil de atleta.

**Archivos afectados:**
- `frontend/src/pages/atleta/portalData.ts` — `loadAtletaPortalSnapshot()`

**Corrección aplicada:**
Se creó el endpoint `GET /registro/atletas/me` en el BC Registro que resuelve el `atleta_id`
correcto a partir del `email` incluido en el JWT. El frontend ahora llama a `fetchAtletaMe()`
para obtener el atleta antes de cualquier consulta de inscripciones.

**Archivos modificados:**
- `src/registro/api/router.py` — nuevo endpoint `/atletas/me`
- `frontend/src/api/registro.ts` — nueva función `fetchAtletaMe()`
- `frontend/src/pages/atleta/portalData.ts` — `loadAtletaPortalSnapshot()` usa `fetchAtletaMe()`

**Patrón emergente:** Toda página del portal atleta que necesite `atleta_id` debe usar
`fetchAtletaMe()` — nunca `userId` del auth store directamente para llamadas a BC Registro.

---

### H-02 — Formulario de inscripción no carga: mismo mismatch

**Síntoma:**
Al navegar a inscripción de torneo: _"No se pudo preparar el formulario de inscripción."_

**Causa raíz:** Idéntica a H-01. `AtletaInscripcionPage` usaba `userId` como `atleta_id`.

**Archivos afectados:**
- `frontend/src/pages/atleta/AtletaInscripcionPage.tsx`

**Corrección aplicada:**
Se reemplazó el uso de `userId` por `fetchAtletaMe()` en `loadInscripcionContext()`.
El `atletaId` ahora proviene de `atleta.atleta_id`.

---

### H-03 — Categoría muestra código interno en el portal

**Síntoma:**
En el portal home, la categoría del atleta aparecía como `MASTER_MASCULINO` en lugar
de "Master Masculino".

**Causa raíz:**
Se renderizaba directamente el valor del dominio sin función de formateo.

**Archivos afectados:**
- `frontend/src/pages/atleta/AtletaHomePage.tsx`

**Corrección aplicada:**
Se agregó `formatCategoria()` en `portalData.ts` con el diccionario `CATEGORIA_LABELS`
y se usó en `AtletaHomePage`.

---

### H-04 — Inscripción: atleta MASTER no puede seleccionar categoría SENIOR

**Síntoma:**
El formulario de inscripción mostraba la categoría como campo de solo lectura para todos
los atletas, sin permitir la selección MASTER → SENIOR que el reglamento permite.

**Regla de dominio:**
Un atleta MASTER puede optar por competir en la categoría SENIOR correspondiente
(MASTER_MASCULINO → SENIOR_MASCULINO; MASTER_FEMENINO → SENIOR_FEMENINO).
Esta es la única variación de doble elección en el modelo de inscripción.

**Corrección aplicada:**
Para atletas MASTER, el campo de categoría se convierte en `<select>` con las dos opciones
habilitadas. Para el resto de categorías, sigue siendo `<input>` readonly.

---

### H-05 — Torneo ya inscripto sigue apareciendo en "Inscripciones abiertas"

**Síntoma:**
PM2026, torneo en el que Victor Valotto ya estaba inscripto, seguía apareciendo en la
sección "Inscripciones abiertas" de `AtletaTorneosPage`.

**Causa raíz:**
`loadTorneos()` filtraba los torneos del atleta, pero usaba `userId` (incorrecto) para
obtener inscripciones, entonces la lista de inscripciones resultaba vacía y el torneo
no se filtraba.

**Corrección aplicada:**
Se incorporó `fetchAtletaMe()` en `loadTorneos()` para obtener el `atleta_id` correcto
y filtrar los torneos ya inscriptos correctamente del listado de disponibles.

---

### H-06 — Botón "Guardar AP" inactivo sin retroalimentación clara

**Síntoma:**
Al navegar a "Declarar AP" en un torneo sin competencia configurada, el botón
"Guardar AP" aparecía deshabilitado sin explicación visible.

**Causa raíz:**
La condición `!query.data.competencia` deshabilitaba el botón cuando no existe
una `Competencia` creada en el BC Competencia para esa disciplina del torneo.
En el entorno de prueba, la competencia no había sido creada por el organizador.

**Corrección aplicada:**
Se agregó un bloque de advertencia en color ámbar que explica al atleta que el
organizador aún no configuró la competencia y que el AP estará disponible cuando
la grilla sea publicada.

**Nota:** Este hallazgo también expuso una dependencia de configuración: el atleta no
puede declarar AP hasta que el organizador haya creado la competencia. Es un comportamiento
correcto del dominio, pero la UX no lo comunicaba.

---

### H-07 — Placeholder de distancia anunciada vacío

**Síntoma:**
El campo de input para el AP mostraba un placeholder vacío en lugar de `"0"`.

**Corrección aplicada:**
Se cambió `placeholder=""` a `placeholder="0"` en `AtletaDeclararAPPage`.

---

### H-08 — Validación no rechaza AP con valor cero

**Síntoma:**
El botón "Guardar AP" no estaba deshabilitado cuando el usuario dejaba el campo en 0.

**Corrección aplicada:**
La condición de `disabled` del botón pasó de `!valorApValue` a
`!(parseFloat(valorApValue) > 0)`, garantizando que solo valores positivos mayores que cero
habiliten el guardado.

---

### H-09 — Error `[object Object]` al intentar guardar AP

**Síntoma:**
Al hacer clic en "Guardar AP" con un valor válido, se mostraba el error `[object Object]`
en la pantalla.

**Causa raíz:**
FastAPI devuelve errores de validación de Pydantic con `detail` como array de objetos
(`[{"loc": [...], "msg": "...", "type": "..."}]`). La función `parseResponse` en
`competencia.ts` solo manejaba `detail` de tipo string, resultando en `[object Object]`
al intentar interpolarlo.

**Corrección aplicada:**
Se agregó manejo de los tres casos posibles en `parseResponse`:
- `string` → usar directamente
- `array` → mapear a `e.msg ?? JSON.stringify(e)` y unir con `'; '`
- `object` → `JSON.stringify`

---

### H-10 — Unidad enviada al backend en mayúsculas incorrectas

**Síntoma:**
Incluso corregido H-09, el backend devolvía error de validación al guardar AP.

**Causa raíz:**
`getUnidadEsperada()` retornaba `'METROS'`/`'SEGUNDOS'` (mayúsculas), pero el backend
espera `'Metros'`/`'Segundos'` (title case) según el modelo Pydantic `Unidad`.

**Corrección aplicada:**
- `portalData.ts`: `getUnidadEsperada()` devuelve `'Metros' | 'Segundos'`
- `competencia.ts`: `RegistrarAPPayload.unidad` tipado como `'Metros' | 'Segundos'`

---

### H-11 — Portal home muestra "Sin AP" después de declarar AP exitosamente

**Síntoma:**
Tras guardar AP (50 m en DNF en PM2026), el portal home seguía mostrando "Sin AP declarado".

**Causa raíz:**
El AP se almacena en el Event Store del BC Competencia (stream
`performance-{competencia_id}-{atleta_id}-{disciplina}`). Sin embargo, `loadAtletaPortalSnapshot`
leía el AP desde la grilla (`fetchGrillaCompetencia`). Si `generar-grilla` no fue ejecutado
por el organizador, la grilla devuelve `[]` y el AP no es visible desde ese read model.

**Corrección aplicada:**
1. **Nuevo endpoint backend:** `GET /competencia/{competencia_id}/ap/{atleta_id}?disciplina=`
   Lee directamente el Event Store, reconstituye el aggregate `Performance` y retorna
   `ap_declarado` y `unidad`. Devuelve `{ap_declarado: null, unidad: null}` si no hay eventos.
2. **Frontend:** En `loadAtletaPortalSnapshot`, cuando el atleta no está en la grilla y el
   torneo está abierto, se llama a `fetchApAtleta` como fallback para obtener el AP declarado.

**Archivos modificados:**
- `src/competencia/api/router.py` — nuevo endpoint `GET /{competencia_id}/ap/{atleta_id}`
- `frontend/src/api/competencia.ts` — nueva función `fetchApAtleta` e interfaz `ApAtletaDto`
- `frontend/src/pages/atleta/portalData.ts` — fallback `fetchApAtleta` en snapshot builder

---

### H-12 — Import faltante en router del backend (500 Internal Server Error)

**Síntoma:**
El nuevo endpoint `GET /competencia/{id}/ap/{atleta_id}` devolvía HTTP 500 con
`NameError: name 'Performance' is not defined`.

**Causa raíz:**
Se usó `Performance.reconstitute(events)` en el handler sin importar el aggregate.

**Corrección aplicada:**
Se agregó `from competencia.domain.aggregates.performance import Performance` en
`src/competencia/api/router.py`.

---

### H-13 — Modificar AP preexistente muestra 0 en lugar del valor guardado

**Síntoma:**
Al volver a la página "Declarar AP" tras haber guardado un AP, el campo de input
mostraba `0` en lugar del valor previamente declarado (ej. `50`).

**Causa raíz:**
`loadApContext` en `AtletaDeclararAPPage` leía `ap_declarado` solo desde la grilla
(`athleteEntry?.ap_declarado`). Si la grilla está vacía (mismo caso que H-11), el
valor retornado era `null` y el input quedaba vacío.

**Corrección aplicada:**
Se incorporó el mismo patrón de fallback de H-11: si `athleteEntry` es `null` y existe
una `competencia`, se llama a `fetchApAtleta` para recuperar el AP actual del event store.
El valor se devuelve como `apActual` y se usa como valor por defecto del input.

---

## Hallazgos de proceso / observaciones

### OBS-01 — Dependencia de datos: competencia debe existir antes del AP

El flujo del portal asume que el organizador ya creó la `Competencia` en el BC Competencia
antes de que el atleta pueda declarar AP. Si la competencia no existe, el botón queda
deshabilitado. Esto es correcto por dominio, pero el flujo del organizador (INC-5.5.2)
debe asegurarse de que el atleta reciba retroalimentación clara sobre este estado.

### OBS-02 — Patrón cross-BC establecido

El endpoint `/registro/atletas/me` consolidó un patrón: el BC Registro resuelve la
identidad del atleta a partir del email del JWT, sin requerir que el BC Identidad exponga
internamente el `atleta_id`. Esto mantiene el aislamiento de BCs.

### OBS-03 — Event Store como read model de AP

La creación del endpoint `GET /ap/{atleta_id}` estableció que el Event Store puede
consultarse directamente para obtener el estado actual de AP sin necesitar la grilla.
Esto introduce un segundo read path para el AP que coexiste con la grilla; deberá
considerarse en refactors futuros (ej. proyección explícita de AP).

---

## Correcciones aplicadas — resumen por capa

| Capa | Archivo | Cambio |
|------|---------|--------|
| Backend API | `src/registro/api/router.py` | Endpoint `GET /atletas/me` |
| Backend API | `src/competencia/api/router.py` | Endpoint `GET /{id}/ap/{atleta_id}` · import Performance |
| Frontend API | `frontend/src/api/registro.ts` | `fetchAtletaMe()` |
| Frontend API | `frontend/src/api/competencia.ts` | `fetchApAtleta()` · `parseResponse` array detail · tipo unidad |
| Frontend Page | `frontend/src/pages/atleta/portalData.ts` | `fetchAtletaMe()` · fallback AP · `formatCategoria()` · tipo `getUnidadEsperada` |
| Frontend Page | `frontend/src/pages/atleta/AtletaHomePage.tsx` | Usar `formatCategoria()` |
| Frontend Page | `frontend/src/pages/atleta/AtletaInscripcionPage.tsx` | `fetchAtletaMe()` · select MASTER/SENIOR |
| Frontend Page | `frontend/src/pages/atleta/AtletaTorneosPage.tsx` | `fetchAtletaMe()` · filtro torneos inscriptos |
| Frontend Page | `frontend/src/pages/atleta/AtletaDeclararAPPage.tsx` | placeholder · validación > 0 · fallback AP · warning sin competencia |

---

*Generado: 2026-04-26 · Sesión UAT funcional INC-5.5 post-reimplementación*
