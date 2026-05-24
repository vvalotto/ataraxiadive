---
us_id: US-ADJ-12.4
rf_ids: []
type: fix-frontend
---

# US-ADJ-12.4 — Frontend: portal atleta — precarga y sincronización de datos

| Campo | Valor |
|-------|-------|
| **ID** | US-ADJ-12.4 |
| **Sprint** | SP-ADJ-12 |
| **Tipo** | fix frontend |
| **Issue** | #200 |
| **Prioridad** | Alta |
| **Área** | `frontend` — `AtletaInscripcionPage.tsx` · `AtletaHomePage.tsx` |

---

## Descripción

Al inscribirse en un torneo, el portal atleta no precarga el documento (DNI) ni el teléfono desde el perfil del atleta ya registrado, forzando al usuario a reingresar datos que ya proporcionó en Mis Datos.
Adicionalmente, el campo Club en la home del atleta muestra vacío cuando el atleta no tiene club registrado, y los datos de Mis Datos no se sincronizan post-inscripción.

---

## Precondición

- El atleta tiene un perfil en BC Registro (`AtletaDto`) con campos `dni` y `telefono` (pueden ser `null`).
- El atleta navega al wizard de inscripción.

## Postcondición

- El paso 1 del wizard muestra `documentoNumero` y `telefono` precargados desde el perfil.
- La home del atleta muestra `'—'` cuando el campo Club está vacío.
- Al completar la inscripción, el cache de `atleta-mis-datos` se invalida para reflejar datos actualizados.

## Invariantes

- La precarga no bloquea la edición: el usuario puede modificar los valores precargados.
- Si el perfil no tiene `dni` o `telefono`, los campos quedan vacíos (no hay fallback inventado).
- La invalidación de `atleta-mis-datos` ocurre solo en el `onSuccess` de la mutation.

---

## Criterios de Aceptación

1. **Precarga documento y teléfono:** Al abrir el wizard, si el atleta tiene `dni` / `telefono` en su perfil, los campos del paso 1 aparecen precargados con esos valores.
2. **Club con fallback:** En `AtletaHomePage`, el campo Club muestra `'—'` cuando `atleta.club` es falsy.
3. **Invalidación post-inscripción:** Tras `onSuccess` de la mutation de inscripción, se llama `queryClient.invalidateQueries({ queryKey: ['atleta-mis-datos'] })`.

---

## Implementación

### 1. `AtletaInscripcionPage.tsx`

Agregar valores computados con fallback desde el perfil del atleta:

```tsx
const documentoNumeroValue = documentoNumero || atleta?.dni || ''
const telefonoValue = telefono || atleta?.telefono || ''
```

Usar estas variables en los inputs del paso 1 en lugar de los estados crudos:
- Input Documento: `value={documentoNumeroValue}`, `onChange` sigue actualizando `setDocumentoNumero`
- Input Teléfono: `value={telefonoValue}`, `onChange` sigue actualizando `setTelefono`

En `nextStep()` (validación paso 1), usar los valores computados:
```tsx
if (!nombreCompletoValue || !fechaNacimientoValue || !documentoNumeroValue || !telefonoValue) {
```

En `onSuccess` de la mutation, agregar invalidación:
```tsx
queryClient.invalidateQueries({ queryKey: ['atleta-mis-datos'] })
```

Agregar `useQueryClient` al import de `@tanstack/react-query`.

### 2. `AtletaHomePage.tsx`

```tsx
<dd className="mt-1 font-semibold text-white">{query.data.atleta.club || '—'}</dd>
```

---

## Tests

Esta US es frontend-only (fix visual + sincronización de cache). No requiere tests unitarios de backend.

**Validación:** `npm run build` sin errores en `frontend/`.

---

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `frontend/src/pages/atleta/AtletaInscripcionPage.tsx` | Precarga doc/tel + invalidación cache post-inscripción |
| `frontend/src/pages/atleta/AtletaHomePage.tsx` | Club con fallback `'—'` |
