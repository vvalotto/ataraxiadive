# Backlog Técnico — AtaraxiaDive

Ítems identificados fuera del ciclo normal de US/SP que requieren decisión de diseño o implementación futura.

---

## BT-001 — Roles múltiples por usuario

**Descubierto:** 2026-05-15  
**Impacto:** Alto — bloquea casos reales de uso

### Problema
El modelo actual asigna un único rol a cada `Usuario` (BC Identidad). Un juez que también compite no puede registrarse con el mismo email: el campo `rol` es un enum de valor único y `email` es UNIQUE en la DB.

Hoy un juez-atleta necesitaría dos cuentas con emails distintos, lo cual es inaceptable en producción.

### Solución propuesta
Cambiar `rol: Rol` → `roles: list[Rol]` en el aggregate `Usuario`.

**Alcance del cambio:**
- BC Identidad: aggregate, DB schema (migración), JWT payload (`rol` → `roles`)
- BC Registro: flujo de inscripción detecta usuario existente y agrega rol `ATLETA` en lugar de rechazar
- Guards de autorización (backend): `RequireRole` pasa a "tiene al menos este rol"
- Frontend: guards de ruta y portales — el usuario accede al portal correspondiente a cada rol que posee

**Lo que NO cambia:** `Atleta` en BC Registro sigue siendo entidad separada vinculada por email. La separación de BCs es correcta.

---

## BT-002 — DNI y Teléfono del atleta no se persisten

**Descubierto:** 2026-05-15  
**Impacto:** Medio — datos recolectados en inscripción se descartan silenciosamente

### Problema
El formulario de inscripción (`AtletaInscripcionPage`) solicita `documento_tipo`, `documento_numero` y `telefono` al atleta, pero estos campos **no se guardan en ningún lado**. El aggregate `Atleta` y su tabla SQLite no los incluyen. Los datos se pierden al hacer submit.

### Solución propuesta
Agregar `dni: str` y `telefono: str` al aggregate `Atleta` (BC Registro):

1. Migración de DB: agregar columnas `dni TEXT` y `telefono TEXT` a la tabla `atletas`
2. Aggregate `Atleta`: campos opcionales `dni: str | None` y `telefono: str | None`
3. `CrearAtletaPayload` y `crearAtleta()`: incluir los campos (ya los recibe el frontend)
4. `ActualizarAtletaMePayload` y PATCH: exponerlos para edición en "Mis Datos"
5. Frontend "Mis Datos": agregar campos al formulario (ya iniciado con `fecha_nacimiento` y `brevet`)
6. Respuesta GET `/atletas/me`: incluir `dni` y `telefono` en `AtletaDto`

**Nota:** `fecha_nacimiento` y `brevet` ya fueron agregados al PATCH en la sesión 2026-05-15 (vibe coding SP6).

---

*Última actualización: 2026-05-15*
