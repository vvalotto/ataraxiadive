# Hallazgos — Fase F-01: Setup: Usuarios y Portal Público

## Defectos

| ID | Escenario | Descripción | Severidad | Pasos para reproducir | Estado | Fix |
|----|-----------|-------------|-----------|----------------------|--------|-----|
| H-01-01 | F01-S08 | Login con rol ADMIN lleva a página en blanco — `RolUsuario` no incluía `'admin'`, `HOME_BY_ROL['admin']` devolvía `undefined`, `RequireRole` redirigía a `undefined` | 🟡 | 1. Login como `admin@ba2025.uat` → página en blanco | Resuelto | Fix: `admin` agregado a `RolUsuario`, `HOME_BY_ROL` y `RequireRole` permite admin en cualquier ruta |
| H-01-02 | F01-S08 | No existe panel de administración ni endpoint de cambio de rol — S08 no es ejecutable | 🟡 | Login como admin → no hay sección de gestión de usuarios | Abierto | Requiere US-IEDD: panel admin con gestión de usuarios y roles |
| H-01-03 | F01-S09 | Email de bienvenida no se envía al registrar usuario — `registrar_usuario.py` no invoca ningún servicio de email | 🟡 | Registrar nuevo usuario → no llega email de confirmación | Abierto | Implementar envío de bienvenida en `RegistrarUsuarioHandler` usando `EmailPort` (patrón de `solicitar_reset_password.py`) |
| H-01-04 | F01-S09 | Post-registro no hay auto-login — app redirige a `/login?registered=1`, usuario debe loguear manualmente | ⚪ | Registrar → esperar ingreso automático al portal → no ocurre | Abierto | UX: considerar auto-login post-registro |
| H-01-05 | F01-S07 | Auto-registro de atleta no crea registro en `registro.db` — `/registro/atletas/me` devuelve 404, portal mostraba error genérico | 🔴 | 1. Registrar nuevo atleta desde UI. 2. Login. 3. Portal mostraba "No se pudo cargar el portal del atleta." | ✅ Resuelto (UX) | Portal muestra estado vacío "Aún no estás inscripto en ningún torneo". Perfil se completa al inscribirse en el primer torneo. |
| H-01-06 | F01-S07 | No existe página "Mis Datos" — el atleta no puede ver ni modificar sus datos personales (nombre, apellido, categoría, club) desde el portal | 🟡 | 1. Login como atleta. 2. Navegar por el portal del atleta. 3. No hay sección para editar perfil. | Abierto | Requiere US-IEDD: página `AtletaMisDatosPage` con formulario de edición de perfil (`nombre`, `apellido`, `categoria`, `club`) + endpoint `PATCH /registro/atletas/me` |

## Mejoras (fuera de scope UAT)

| ID | Origen | Descripción | Prioridad sugerida |
|----|--------|-------------|-------------------|
| M-01-01 | H-01-04 | Auto-login post-registro — redirigir al portal automáticamente tras completar el registro exitoso, sin requerir login manual | Media |
