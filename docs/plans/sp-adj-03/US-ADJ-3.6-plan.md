# Plan de Implementacion — US-ADJ-3.6

## Resumen

Desacoplar el BC `identidad` de implementaciones concretas de autenticacion y
hashing para que la capa `application/` dependa de puertos del dominio, no de
`bcrypt` ni de `JWTService` concretos.

## Objetivo observable

- `AutenticarUsuarioHandler` usa `TokenServicePort` y
  `PasswordHashingPort`.
- `RegistrarUsuarioHandler` usa `PasswordHashingPort`.
- `JWTService` implementa `TokenServicePort`.
- existe `BcryptPasswordHasher` en infraestructura.
- `get_current_user()` deja de instanciar `JWTService()` inline por request.
- login y registro siguen respondiendo igual que antes.

## Alcance

- `src/identidad/domain/ports/`
- `src/identidad/application/commands/`
- `src/identidad/api/dependencies.py`
- `src/identidad/api/router.py`
- `src/identidad/infrastructure/`
- `src/app.py` si hace falta composition root para wiring compartido
- tests unitarios/API de `identidad`

No incluye:

- endpoints nuevos
- cambio de contrato HTTP
- BDD nueva
- cambio de repositorio o persistencia de usuarios

## Decisiones de diseño

1. `TokenServicePort` y `PasswordHashingPort` viven en
   `identidad/domain/ports/` porque son capacidades del BC, aunque sus
   implementaciones concretas sean técnicas.
2. `JWTService` se mantiene como adapter de infraestructura y solo pasa a
   implementar el puerto.
3. `BcryptPasswordHasher` concentra toda la dependencia a `bcrypt`.
4. `api/dependencies.py` no construira `JWTService` por request; usara una
   referencia inyectable inicializada desde composition root o desde el propio
   modulo con override explícito.
5. El router de auth dejara de instanciar servicios concretos inline; obtendra
   repo, token service y password hasher via helpers/dependencias del BC.

## Implementacion por capa

### Dominio

- crear `token_service_port.py`
- crear `password_hashing_port.py`
- exportarlos en `identidad/domain/ports/__init__.py`

### Aplicacion

- refactorizar `AutenticarUsuarioHandler` para recibir:
  - `UsuarioRepositoryPort`
  - `TokenServicePort`
  - `PasswordHashingPort`
- refactorizar `RegistrarUsuarioHandler` para recibir:
  - `UsuarioRepositoryPort`
  - `PasswordHashingPort`
- eliminar imports directos de `bcrypt` e `identidad.infrastructure`

### Infraestructura

- hacer que `JWTService` herede de `TokenServicePort`
- crear `BcryptPasswordHasher`

### API / Wiring

- introducir providers reutilizables para:
  - repositorio de usuarios
  - token service
  - password hasher
- actualizar `get_current_user()` para verificar con el servicio inyectado
- actualizar `router.py` para construir handlers desde esas dependencias
- si el wiring compartido lo necesita, registrar implementaciones en `app.py`

### Tests

- adaptar tests unitarios de handlers a dobles sobre puertos
- mantener tests de `JWTService`
- adaptar tests de dependencias/API si cambia el punto de override

## Riesgos a controlar

1. romper el login al cambiar el wiring de `get_current_user()`
2. introducir acoplamiento nuevo en `router.py` aunque se elimine de
   `application/`
3. dejar `JWTService` inaccesible en tests por requerir env vars sin fixture
4. cambiar sin querer el contrato JSON de `/auth/login` o `/auth/registro`

## Validacion prevista

- `pytest tests/unit/identidad/application/test_handlers.py -q`
- `pytest tests/unit/identidad/api/test_dependencies.py -q`
- si el router cambia de forma relevante:
  `pytest tests/features/steps/identidad_jwt_steps.py -q`
- `./.venv/bin/python -m py_compile` sobre archivos impactados
- `./.venv/bin/codeguard` sobre `src/identidad/...`
- `git diff --check`

## Artefactos esperados al cierre

- puertos nuevos en dominio
- infraestructura adaptada a puertos
- handlers y dependencias desacoplados
- evidencia de quality gates
- `docs/reports/US-ADJ-3.6-report.md`
