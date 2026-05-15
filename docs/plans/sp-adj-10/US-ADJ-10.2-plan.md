# Plan de Implementación: US-ADJ-10.2 — Página "Mis Datos" del atleta

**Patrón:** Hexagonal DDD + BC
**Producto:** registro + frontend atleta
**Estimación Total:** 1h 5min

---

## Componentes a Implementar

### 1. Domain — Atleta (hexagonal/domain)
- [ ] `src/registro/domain/aggregates/atleta.py` — agregar método `actualizar()` (10 min)
  - Parámetros opcionales: `nombre`, `apellido`, `categoria`, `club`
  - Muta solo los campos provistos (semántica PATCH)
  - Re-ejecuta validaciones de dominio tras la mutación

### 2. Application — Command + Handler (hexagonal/application)
- [ ] `src/registro/application/commands/actualizar_atleta.py` (10 min)
  - `ActualizarAtletaCommand`: dataclass frozen con campos `Optional`
  - `ActualizarAtletaHandler`: carga atleta por email, aplica `actualizar()`, persiste

### 3. API — Endpoint PATCH (hexagonal/api)
- [ ] `src/registro/api/router.py` — agregar `PATCH /registro/atletas/me` (10 min)
  - Request body: `ActualizarAtletaMeRequest` (campos opcionales)
  - Carga atleta por email del usuario autenticado (`AtletaDep`)
  - Retorna 200 con perfil actualizado · 404 si no existe

### 4. Frontend — API client
- [ ] `frontend/src/api/registro.ts` — agregar `actualizarAtletaMe(data)` (5 min)
  - Llama `PATCH /registro/atletas/me`
  - Payload: campos opcionales del perfil

### 5. Frontend — Nueva página
- [ ] `frontend/src/pages/atleta/AtletaMisDatosPage.tsx` (20 min)
  - Carga perfil actual con `fetchAtletaMe()` al montar
  - Formulario pre-rellenado: nombre, apellido, categoría (selector enum), club
  - Submit llama `actualizarAtletaMe()` y muestra confirmación/error
  - Usa `AtletaShell` como layout

### 6. Integración — Navegación y rutas
- [ ] `frontend/src/components/atleta/AtletaShell.tsx` — agregar tab "Mis Datos" (5 min)
  - Nuevo item en `TABS`: `{ label: 'Mis Datos', to: '/atleta/mis-datos' }`
  - Cambiar `grid-cols-4` → `grid-cols-5`
- [ ] `frontend/src/App.tsx` — agregar ruta `/atleta/mis-datos` (5 min)
  - `<RequireRole role="atleta"><AtletaMisDatosPage /></RequireRole>`

---

## Invariantes a garantizar

| INV | Dónde se verifica |
|-----|-------------------|
| INV-ADJ-10.2-01: campos opcionales (PATCH) | Domain `actualizar()` + Handler |
| INV-ADJ-10.2-02: categoría válida | Pydantic validator en request schema |
| INV-ADJ-10.2-03: opera sobre atleta propio | Handler usa email de `AtletaDep` |
| INV-ADJ-10.2-04: 404 si sin perfil | Handler retorna → endpoint → 404 |

---

**Estado:** 0/6 tareas completadas
