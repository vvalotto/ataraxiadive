# Reporte de Implementacion — US-ADJ-3.6
## `TokenServicePort` + `PasswordHashingPort` en Identidad

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se desacoplo el BC `identidad` de implementaciones concretas de autenticacion
y hashing.

La capa `application/` ya no importa `bcrypt` ni `JWTService` concretos. En su
lugar, depende de `TokenServicePort` y `PasswordHashingPort` definidos en
dominio.

Ademas, `get_current_user()` y el router de auth dejaron de instanciar
`JWTService()` inline por request y pasaron a resolver dependencias por
providers reutilizables configurables desde el composition root.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/identidad/domain/ports/token_service_port.py` | Dominio | Puerto para generar y verificar tokens |
| `src/identidad/domain/ports/password_hashing_port.py` | Dominio | Puerto para hashing y verificacion de contrasenas |
| `src/identidad/infrastructure/bcrypt_password_hasher.py` | Infraestructura | Adapter concreto para bcrypt |
| `src/identidad/infrastructure/jwt_service.py` | Infraestructura | `JWTService` ahora implementa `TokenServicePort` |
| `src/identidad/application/commands/autenticar_usuario.py` | Aplicacion | Handler desacoplado de `bcrypt` y de `JWTService` concreto |
| `src/identidad/application/commands/registrar_usuario.py` | Aplicacion | Handler desacoplado de `bcrypt` |
| `src/identidad/api/dependencies.py` | API | Providers configurables para token service, hasher y repo |
| `src/identidad/api/router.py` | API | Router actualizado para construir handlers via providers |
| `src/app.py` | Composition root | Wiring inicial de dependencias de identidad |
| `docs/plans/sp-adj-03/US-ADJ-3.6-bdd-skip.md` | Plan | Constancia de omision explicita de BDD nueva |
| `docs/plans/sp-adj-03/US-ADJ-3.6-integration-skip.md` | Plan | Constancia de omision explicita de integracion nueva |
| `docs/plans/sp-adj-03/US-ADJ-3.6-plan.md` | Plan | Plan tecnico aprobado |
| `quality/reports/codeguard/US-ADJ-3.6-application-quality.txt` | Quality gate | Evidencia de CodeGuard sobre application |
| `quality/reports/codeguard/US-ADJ-3.6-api-quality.txt` | Quality gate | Evidencia de CodeGuard sobre API |
| `quality/reports/codeguard/US-ADJ-3.6-infra-quality.txt` | Quality gate | Evidencia de CodeGuard sobre infra y ports |

---

## Decisiones Tecnicas

### Puertos en dominio

Se introdujeron:

- `TokenServicePort`
- `PasswordHashingPort`

Con esto, `application/` expresa capacidades necesarias del BC sin conocer
detalles tecnicos de JWT o bcrypt.

### Infraestructura como adapters

`JWTService` sigue siendo el adapter concreto para JWT, pero ahora implementa
el puerto del dominio.

`BcryptPasswordHasher` concentra toda la dependencia a `bcrypt`, dejando esa
decision fuera de `application/`.

### Wiring configurable

`identidad/api/dependencies.py` incorpora providers reutilizables y
`configure_identity_dependencies(...)`.

`src/app.py` inicializa esas dependencias cuando `IDENTIDAD_JWT_SECRET` esta
disponible, evitando construccion inline por request.

---

## Invariantes Verificadas

| ID | Descripcion | Estado |
|----|-------------|--------|
| `INV-ADJ-3.6-1` | `autenticar_usuario.py` no importa `bcrypt` | ✅ |
| `INV-ADJ-3.6-2` | `registrar_usuario.py` no importa `bcrypt` | ✅ |
| `INV-ADJ-3.6-3` | `application/commands/` no importa `identidad.infrastructure` | ✅ |
| `INV-ADJ-3.6-4` | login y registro siguen funcionando igual | ✅ |
| `INV-ADJ-3.6-5` | la suite existente de identidad sigue pasando | ✅ |

---

## Validacion Ejecutada

| Suite / Gate | Resultado |
|-------------|-----------|
| `tests/unit/identidad/application/test_handlers.py` | ✅ 12/12 |
| `tests/unit/identidad/api/test_dependencies.py` | ✅ 9/9 |
| `tests/features/steps/identidad_jwt_steps.py` | ✅ 7/7 |
| `py_compile` sobre archivos impactados | ✅ |
| `git diff --check` | ✅ |
| `CodeGuard` application | ✅ 0 errores, 0 warnings |
| `CodeGuard` API | ✅ 0 errores, 0 warnings |
| `CodeGuard` infra + ports | ✅ 0 errores, 0 warnings |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/identidad/application/test_handlers.py -q
./.venv/bin/pytest tests/unit/identidad/api/test_dependencies.py -q
./.venv/bin/pytest tests/features/steps/identidad_jwt_steps.py -q
./.venv/bin/python -m py_compile src/identidad/domain/ports/token_service_port.py src/identidad/domain/ports/password_hashing_port.py src/identidad/infrastructure/bcrypt_password_hasher.py src/identidad/infrastructure/jwt_service.py src/identidad/application/commands/autenticar_usuario.py src/identidad/application/commands/registrar_usuario.py src/identidad/api/dependencies.py src/identidad/api/router.py src/app.py tests/unit/identidad/application/test_handlers.py
git diff --check
```

---

## Observaciones metodologicas

- La Fase 1 se ejecuto como skip documentado por decision explicita del sprint
  de ajuste.
- La Fase 5 tambien quedo documentada como skip explicito porque no hubo cambio
  de persistencia ni de repositorios; la validacion observable se cubrio con la
  suite HTTP/BDD existente de identidad.

---

## Resultado

`US-ADJ-3.6` queda cerrada funcional y metodologicamente dentro del pipeline,
lista para commit dentro de `SP-ADJ-03`.
