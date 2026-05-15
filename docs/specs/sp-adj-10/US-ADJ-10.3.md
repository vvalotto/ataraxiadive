# US-ADJ-10.3: Email de bienvenida y auto-login post-registro — H-01-03/H-01-04 UAT SP6

**Estado**: `Implementada`
**Iteracion / Sprint**: SP-ADJ-10
**Tipo**: fix funcional backend + UX frontend
**Agregado principal afectado**: `Usuario`
**Bounded Context**: `identidad` + frontend

---

## Descripcion (lenguaje de negocio)

Como **usuario nuevo**,
quiero recibir un email de bienvenida al registrarme y ser dirigido directamente a mi
portal sin tener que loguear manualmente
para tener una experiencia de incorporación completa desde el primer uso.

---

## Contexto del dominio

### Problema

`RegistrarUsuarioHandler` no invoca `EmailPort` — el usuario no recibe bienvenida al
registrarse (H-01-03). Tras el registro exitoso, `RegisterPage` redirige a
`/login?registered=1` obligando al usuario a hacer login manual en lugar de entrar
directamente a su portal (H-01-04, F-01).

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Handler | `RegistrarUsuarioHandler` | Crear usuario y disparar efectos post-registro |
| Port | `EmailPort` | Enviar email de bienvenida |
| Page | `RegisterPage` | Formulario de registro en frontend |
| Helper | `portalPorRol(rol)` | Ruta del portal correspondiente al rol del usuario |

---

## Especificacion del comportamiento

### Precondicion

El usuario completa el formulario de registro con email, contraseña y rol válidos.
El servicio de email puede estar disponible o no.

### Postcondicion

- Se envía un email de bienvenida al email registrado (best-effort).
- El usuario queda autenticado y es redirigido al portal correspondiente a su rol.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-10.3-01 | El registro no falla si el servicio de email no está disponible — el envío es best-effort. |
| INV-ADJ-10.3-02 | El auto-login usa las mismas credenciales ingresadas en el formulario — no se persiste la contraseña en ningún estado de la aplicación. |
| INV-ADJ-10.3-03 | Si el auto-login falla por error de red u otro, el usuario llega a `/login` con mensaje informativo — el registro ya se completó. |
| INV-ADJ-10.3-04 | La redirección post-login usa `portalPorRol(rol)` — el destino depende del rol registrado. |

---

## Criterios de aceptacion

```gherkin
Feature: Email de bienvenida y auto-login post-registro

  Scenario: Usuario nuevo recibe email de bienvenida al registrarse
    Given el servicio de email está disponible
    When un nuevo usuario se registra con email "nuevo@ejemplo.com"
    Then se invoca EmailPort.enviar_bienvenida con "nuevo@ejemplo.com"

  Scenario: El registro no falla si el email no se puede enviar
    Given el servicio de email no está disponible
    When un nuevo usuario completa el formulario de registro
    Then el usuario queda registrado correctamente
    And el sistema registra el error de email en el log
    And no muestra error al usuario por el email fallido

  Scenario: Auto-login redirige al portal correcto tras registro como atleta
    Given un usuario se registra con rol ATLETA
    When el registro es exitoso
    Then el sistema ejecuta login automático
    And el usuario es redirigido al portal del atleta sin pasar por /login

  Scenario: Auto-login redirige al portal correcto tras registro como organizador
    Given un usuario se registra con rol ORGANIZADOR
    When el registro es exitoso
    Then el usuario es redirigido al portal del organizador sin pasar por /login

  Scenario: Fallback a /login si el auto-login falla
    Given el registro es exitoso pero el auto-login falla por error de red
    When el formulario de registro recibe el error
    Then el usuario es redirigido a /login
    And ve un mensaje indicando que debe ingresar manualmente
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — el `EmailPort` ya existe y tiene patrón establecido en `solicitar_reset_password.py`.
  El auto-login en frontend es un `POST /auth/login` programático dentro del handler del formulario.

**Capa(s) afectadas:**
- [x] Application — `RegistrarUsuarioHandler` invoca `EmailPort`.
- [x] Frontend — `RegisterPage` ejecuta auto-login y redirige.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `src/identidad/application/registrar_usuario.py` | Invocar `EmailPort.enviar_bienvenida(email, nombre)` tras persistir el usuario. |
| `frontend/src/pages/RegisterPage.tsx` (o equivalente) | Tras `201`, ejecutar `POST /auth/login`, guardar token en `useAuthStore`, redirigir a `portalPorRol(rol)`. Eliminar redirección a `/login?registered=1`. |

---

## Notas de implementacion

1. Seguir el patrón de `solicitar_reset_password.py` para la invocación del `EmailPort`:
   try/except con log del error, sin relanzar la excepción.
2. El auto-login hace dos requests secuenciales en el submit del formulario:
   `POST /auth/register` → `POST /auth/login`. No introduce estado inconsistente.
3. No persistir la contraseña en ningún store ni variable de módulo — usar directamente
   el valor del input dentro del handler del formulario y descartarlo.
4. El fallback a `/login` debe mostrar un mensaje claro, por ejemplo:
   "Tu cuenta fue creada. Por favor ingresá manualmente."

---

*Spec creada: 2026-05-14 — hallazgos H-01-03 y H-01-04 UAT SP6 F-01*
