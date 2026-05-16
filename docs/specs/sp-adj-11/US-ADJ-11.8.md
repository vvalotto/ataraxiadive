# US-ADJ-11.8: Frontend — Mis Datos Atleta — dni, telefono y campos opcionales

**Estado**: `Especificada`
**Iteracion / Sprint**: SP-ADJ-11
**Tipo**: refactor frontend
**Área**: `frontend/` — `AtletaMisDatosPage.tsx` · `api/registro.ts`
**Dependencias**: US-ADJ-11.3
**Track de implementación**: informal (vibe coding) — solo toca `frontend/`

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-registro-roles.md` — S-06 (Mi Perfil / Datos deportivos)
- `docs/design/ux/wireframes-atleta.md`

S-06 muestra "Datos deportivos" con club, federación y número de licencia marcados como opcionales. Esta US alinea el formulario de Atleta con los campos que el backend (US-ADJ-11.3) ahora acepta: `dni` y `telefono` (opcionales), y confirma que `club` y `categoria` también son opcionales en el payload PATCH.

---

## Descripcion

Como atleta registrado,
quiero poder ingresar y actualizar mi DNI y teléfono en Mis Datos,
para completar mi perfil con información de contacto real.

---

## Estado actual vs. estado deseado

| Elemento | Estado actual | Estado deseado |
|----------|--------------|----------------|
| `AtletaDto` en `api/registro.ts` | Sin `dni` ni `telefono` | Agrega `dni: string \| null` y `telefono: string \| null` |
| `ActualizarAtletaMePayload` | Sin `dni` ni `telefono` | Agrega `dni?: string \| null` y `telefono?: string \| null` |
| `FormState` en `AtletaMisDatosPage` | Sin `dni` ni `telefono` | Agrega `dni: string` y `telefono: string` |
| `toFormState()` en `AtletaMisDatosPage` | No mapea `dni`/`telefono` | Mapea `atleta.dni ?? ''` y `atleta.telefono ?? ''` |
| `handleSubmit` payload | Sin `dni`/`telefono` | Incluye ambos campos como `string \| undefined` (vacío → `undefined`) |
| UI del formulario | Campos: nombre, apellido, categoría, club, fecha_nacimiento, brevet | Agrega campos `DNI` y `Teléfono` con helper "Opcional" |

---

## Especificacion del comportamiento

### Precondicion

- El usuario está autenticado como ATLETA.
- El backend (US-ADJ-11.3) acepta `dni` y `telefono` en `PATCH /registro/atletas/me`.

### Postcondicion

- El perfil del atleta refleja el `dni` y `telefono` guardados.
- Si los campos se dejan vacíos, se omiten del payload (no se borran datos existentes).

### Invariantes

| ID | Invariante |
|----|------------|
| INV-11.8-01 | `dni` y `telefono` son opcionales — el formulario no valida su presencia. |
| INV-11.8-02 | Un campo vacío en el formulario se envía como `undefined` en el payload (no `null`), preservando el valor existente en el backend. |
| INV-11.8-03 | `club` y `categoria` ya son opcionales en `ActualizarAtletaMePayload` — no requieren cambio de comportamiento, solo verificar que el formulario los envíe como `undefined` si están vacíos. |

---

## Criterios de aceptacion

```gherkin
Scenario: Atleta carga la página Mis Datos — ve sus datos actuales incluyendo dni/telefono
  Given el atleta tiene dni="12345678" y telefono="1234567890" guardados
  When accede a /atleta/mis-datos
  Then los campos DNI y Teléfono muestran esos valores

Scenario: Atleta actualiza su DNI
  Given el atleta está en /atleta/mis-datos
  When ingresa "98765432" en el campo DNI y guarda
  Then el PATCH a /registro/atletas/me incluye dni="98765432"
  And el formulario refleja el valor actualizado

Scenario: Atleta deja DNI vacío — no se borra el dato existente
  Given el atleta tiene dni="12345678" guardado
  When guarda el formulario sin modificar el campo DNI
  Then el PATCH no incluye el campo dni en el payload

Scenario: Atleta con dni null — campo queda vacío en el formulario
  Given el atleta no tiene dni registrado
  When accede a /atleta/mis-datos
  Then el campo DNI aparece vacío sin error
```

---

## Artefactos a crear / modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/api/registro.ts` | `AtletaDto`: agregar `dni: string \| null` y `telefono: string \| null`. `ActualizarAtletaMePayload`: agregar `dni?: string \| null` y `telefono?: string \| null`. |
| `frontend/src/pages/atleta/AtletaMisDatosPage.tsx` | `FormState`: agregar `dni: string` y `telefono: string`. `toFormState()`: mapear `dni` y `telefono`. `handleSubmit`: incluir `dni` y `telefono` (vacío → `undefined`). UI: agregar dos `<label>`+`<input>` con placeholder y helper "Opcional". |

---

## Notas de implementacion

1. **Posición de los campos:** DNI y Teléfono se agregan al final del formulario, antes del botón guardar, para no romper el orden visual existente.

2. **Helper "Opcional":** incluir `<span className="text-xs text-slate-400 ml-1">(opcional)</span>` junto al label para claridad UX.

3. **Campo vacío → `undefined`:** el submit ya hace `form.campo.trim() || undefined` para otros campos — aplicar el mismo patrón para `dni` y `telefono`.

4. **`null` → empty string:** `toFormState` ya usa `atleta.campo ?? ''` para `brevet` — mismo patrón para `dni`/`telefono`.

---

*Spec creada: 2026-05-16 — SP-ADJ-11*
