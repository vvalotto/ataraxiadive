# ADR-020: Modelo de usuarios con múltiples roles y perfiles por rol

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-05-16 |
| **Autores** | Victor Valotto |
| **Relacionado con** | BT-001, BT-002 · `docs/USUARIO-ROLES.md` · BC Identidad · BC Registro |

---

## Contexto

El modelo original asignaba un único rol a cada `Usuario` (`rol: Rol`). Esto impedía que una persona pudiera ser simultáneamente atleta y juez — caso real y frecuente en competencias de apnea de nivel local y regional. Un juez-atleta necesitaba dos cuentas con emails distintos, lo que es inaceptable en producción.

Adicionalmente, cada rol tiene datos específicos (licencia de juez, club del atleta, organización) que el modelo original no contemplaba. BC Registro solo tenía la entidad `Atleta`; `Juez` y `Organizador` no existían como entidades persistidas.

---

## Decisiones

### 1. `Usuario` pasa a tener lista de roles

**Antes:** `rol: Rol` — un único valor del enum `ORGANIZADOR | JUEZ | ATLETA | ADMIN`  
**Después:** `roles: list[Rol]` — uno o más roles por usuario

La columna en SQLite pasa de `rol TEXT NOT NULL` a `roles TEXT NOT NULL` (JSON array).

`ADMIN` se mantiene como superrol interno: no aparece en el registro público, se asigna directamente en la base de datos.

### 2. Tres entidades de perfil en BC Registro

Cada rol funcional tiene una entidad propia en BC Registro, vinculada al `Usuario` por email:

| Entidad | Campos obligatorios                               | Campos opcionales |
|---------|---------------------------------------------------|-------------------|
| `Atleta` | documento_tipo, documento_numero, telefono, fecha_nacimiento | club, categoria (autodeclarada), brevet |
| `Juez` | documento_tipo, documento_numero, telefono, numero_licencia |  federacion |
| `Organizador` | telefono                                                  | nombre_organizacion |

`Atleta` ya existía. `Juez` y `Organizador` son entidades nuevas, cada una con su propia tabla SQLite en la misma DB de BC Registro.

### 3. JWT con rol único activo (Opción A)

El JWT lleva el rol elegido al momento del login como string simple:

```json
{ "sub": "uuid", "email": "...", "nombre": "...", "apellido": "...", "rol": "ATLETA" }
```

Para cambiar de portal el usuario vuelve a loguearse y elige otro rol. No hay `rol_activo` ni lista de roles en el token. Los guards de autorización (`require_rol`) no cambian su interfaz.

**Alternativa descartada:** JWT con `roles: list[str]` + `rol_activo`. Mejor UX (switcher sin re-login) pero complejidad innecesaria para la etapa actual.

### 4. Flujo de login según cantidad de roles

- **1 rol:** acceso directo al portal correspondiente, sin selector.
- **N roles:** el usuario elige con qué rol ingresar antes de acceder.

### 5. Agregar roles post-registro desde Mis Datos

Un usuario puede adquirir un nuevo rol desde la página "Mis Datos" de cualquier portal. Al agregar un rol, se solicitan los datos del perfil correspondiente y se crea la entidad en BC Registro. El cambio aplica en el próximo login.

### 6. Quitar roles

- **JUEZ / ORGANIZADOR:** se pueden quitar desde Mis Datos. Se elimina la entidad de perfil correspondiente.
- **ATLETA:** no se puede quitar — el historial de competencias (BC Competencia) queda asociado al perfil Atleta.

### 7. Página "Mis Datos" en cada portal

Cada portal de rol (Atleta, Juez, Organizador) incluye una página Mis Datos para editar datos comunes del `Usuario` y datos específicos del perfil de ese rol. El portal Atleta ya tiene implementación parcial que requiere revisión.

---

## Justificación

**Roles como lista en el aggregate vs. tabla de relación:**
Se eligió `roles: list[Rol]` serializado como JSON en la columna `roles TEXT`. La alternativa (tabla `usuario_roles` con FK) agrega complejidad de joins para una cardinalidad máxima de 3-4 roles por usuario. JSON en columna es suficiente y consistente con el patrón de persistencia del proyecto (SQLite por BC, sin ORM).

**Perfiles en BC Registro y no en BC Identidad:**
BC Identidad gestiona credenciales y autenticación; los datos de rol son información de negocio (resultados de atletas, competencias juzgadas). Mantener los perfiles en BC Registro preserva la separación de responsabilidades. La vinculación por email es el contrato natural entre BCs (ADR-005).

**Rol activo único en JWT vs. todos los roles:**
Consistente con el principio de menor sorpresa: el backend siempre sabe exactamente qué puede hacer el portador del token en esa sesión. Roles múltiples en el JWT requieren lógica adicional en cada guard para resolver cuál aplica en cada endpoint.

---

## Consecuencias

**Positivas:**
- Un juez-atleta usa una sola cuenta con un email.
- Los datos de perfil de cada rol quedan persistidos y editables.
- Los guards de autorización no cambian de interfaz.
- El JWT es más simple que con múltiples roles.

**Negativas:**
- Migración de DB necesaria: columna `rol` → `roles` en `usuarios`.
- Dos entidades nuevas en BC Registro (`Juez`, `Organizador`) con sus tablas.
- El flujo de registro se complejiza: un paso adicional por cada rol seleccionado.
- Para cambiar de portal hay que volver a loguearse — limitación asumida conscientemente.

## Límites del diseño

- Un usuario no puede tener el mismo rol dos veces (invariante del aggregate).
- `ADMIN` no se puede asignar desde la UI — solo desde la base de datos directamente.
- La `categoria` del atleta es autodeclarada; el sistema no la valida contra criterios federativos.
