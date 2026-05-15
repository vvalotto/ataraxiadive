# Plan de Implementación — US-ADJ-10.3

**US:** Email de bienvenida y auto-login post-registro  
**Branch:** `feature/US-ADJ-10.3-email-autologin`  
**Estimación total:** 45 min  

---

## Contexto técnico

| Elemento | Estado actual | Cambio requerido |
|---|---|---|
| `RegistrarUsuarioHandler` | No usa EmailPort | Inyectar EmailPort, invocar best-effort |
| `router.py POST /auth/registro` | No pasa email_sender | Agregar Depends(get_email_sender) |
| `RegistroPage.tsx onSuccess` | Redirige a `/login?registered=1` | Auto-login + redirect a portal |
| `portalPorRol` | Definida localmente en LoginPage | Usar `HOME_BY_ROL` de `utils/auth.ts` |

**Patrón de referencia:** `solicitar_reset_password.py` — try/except sin re-raise.  
**EmailPort interface:** `enviar(destinatario: Destinatario, contenido: ContenidoEmail) -> str | None`  
**`HOME_BY_ROL`:** `utils/auth.ts` — mapea `RolUsuario` (lowercase) a ruta de portal.

---

## Tareas

### T1 — Backend: `RegistrarUsuarioHandler` invoca `EmailPort` (15 min)

**Archivo:** `src/identidad/application/commands/registrar_usuario.py`

```python
# Handler.__init__ agrega email_sender opcional
def __init__(
    self,
    repo: UsuarioRepositoryPort,
    password_hasher: PasswordHashingPort,
    email_sender: EmailPort | None = None,
) -> None:
    ...
    self._email_sender = email_sender

# handle(): después de repo.save(usuario), antes de return:
if self._email_sender is not None:
    try:
        await self._email_sender.enviar(
            Destinatario(email=usuario.email, nombre=f"{usuario.nombre} {usuario.apellido}".strip()),
            ContenidoEmail(
                asunto="Bienvenido/a a AtaraxiaDive",
                cuerpo_texto=(
                    f"Hola {usuario.nombre},\n"
                    "Tu cuenta en AtaraxiaDive fue creada exitosamente.\n"
                    "Ya podés acceder a tu portal."
                ),
            ),
        )
    except Exception:
        import logging
        logging.getLogger(__name__).warning(
            "No se pudo enviar email de bienvenida a %s", usuario.email
        )
```

**Invariante cubierto:** INV-ADJ-10.3-01 (best-effort, sin re-raise).

---

### T2 — Backend: `router.py` inyecta `EmailPort` en POST /auth/registro (5 min)

**Archivo:** `src/identidad/api/router.py`

Agregar dependencia al endpoint:
```python
@router.post("/registro", status_code=201)
async def registrar_usuario(
    body: RegistroRequest,
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    password_hasher: Annotated[PasswordHashingPort, Depends(get_password_hasher)],
    email_sender: Annotated[EmailPort, Depends(get_email_sender)],   # <-- nuevo
) -> JSONResponse:
    handler = RegistrarUsuarioHandler(repo, password_hasher, email_sender)  # <-- pasa email_sender
```

---

### T3 — Frontend: `RegistroPage.tsx` auto-login post-registro (20 min)

**Archivo:** `frontend/src/pages/RegistroPage.tsx`

Cambios:
1. Importar `loginApi` desde `../api/auth`
2. Importar `useAuthStore` (ya importado) y `HOME_BY_ROL` desde `../utils/auth`
3. Importar `RolUsuario` desde `../types/auth`
4. Modificar `mutation.onSuccess` para ejecutar auto-login:

```tsx
const login = useAuthStore((s) => s.login)

const mutation = useMutation({
  mutationFn: crearUsuario,
  onSuccess: async (_data, variables) => {
    try {
      const tokenData = await loginApi(variables.email, variables.password)
      login(tokenData.access_token)
      const rolPortal = variables.rol.toLowerCase() as RolUsuario
      navigate(HOME_BY_ROL[rolPortal] ?? '/atleta', { replace: true })
    } catch {
      navigate('/login', { replace: true, state: { autologinFailed: true } })
    }
  },
  // onError: sin cambios
})
```

5. Eliminar la redirección a `/login?registered=1`.

**INV cubiertos:**
- INV-ADJ-10.3-02: password tomado de `variables.password` (en memoria, no persiste)
- INV-ADJ-10.3-03: catch → `/login` con state
- INV-ADJ-10.3-04: `HOME_BY_ROL[rol]` — destino por rol

---

### T4 — Frontend: LoginPage muestra mensaje de fallback (5 min)

**Archivo:** `frontend/src/pages/LoginPage.tsx`

Agregar lectura del state de navegación para mostrar mensaje cuando `autologinFailed`:
```tsx
import { useLocation } from 'react-router-dom'
const location = useLocation()
const autologinFailed = (location.state as { autologinFailed?: boolean } | null)?.autologinFailed
```

Y en el JSX, junto a `{registered ?...}`:
```tsx
{autologinFailed ? (
  <p ...>Tu cuenta fue creada. Por favor ingresá manualmente.</p>
) : null}
```

---

## Archivos a modificar

| Archivo | Tipo | Cambio |
|---|---|---|
| `src/identidad/application/commands/registrar_usuario.py` | Backend | Agregar EmailPort best-effort |
| `src/identidad/api/router.py` | Backend | Inyectar email_sender en endpoint |
| `frontend/src/pages/RegistroPage.tsx` | Frontend | Auto-login + redirect portal |
| `frontend/src/pages/LoginPage.tsx` | Frontend | Mensaje fallback autologin |

## Tests a crear/modificar

| Archivo | Tests nuevos |
|---|---|
| `tests/unit/identidad/application/test_handlers.py` | 2 tests para `RegistrarUsuarioHandler` con email_sender |
| `tests/unit/identidad/api/test_registro_usuario.py` | 1 test que verifica el email_sender se pasa al handler |
| `tests/integration/identidad/` | 1 test integración registro + email best-effort |
| `tests/features/steps/email_autologin_steps.py` | Steps BDD para los 5 escenarios |

---

*Estimación: T1 15min + T2 5min + T3 20min + T4 5min = 45 min*
