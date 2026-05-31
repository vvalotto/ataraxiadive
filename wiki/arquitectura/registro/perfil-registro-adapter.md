---
title: "Registro — PerfilRegistroAdapter"
type: arquitectura-componente
bc: registro
capa: infrastructure
tipo_componente: adapter
responsabilidad: "Puente entre BC Identidad y BC Registro — crea perfiles deportivos cuando se registra un nuevo usuario"
interfaces_out: []
adr_refs: [ADR-020, ADR-005]
last_updated: "2026-05-23"
sources:
  - src/registro/infrastructure/perfil_registro_adapter.py
---

# PerfilRegistroAdapter

## Responsabilidad

Implementa `PerfilRegistroPort` (definido en BC Identidad) para crear los perfiles deportivos correspondientes cuando BC Identidad registra un nuevo usuario. Es el punto de integración del modelo multi-rol (ADR-020).

## Flujo

```
BC Identidad → RegistrarUsuarioHandler
    → PerfilRegistroPort.crear_perfiles(usuario_id, roles, ...)
        → PerfilRegistroAdapter.crear_perfiles()
            ├── Si Rol.ATLETA → RegistrarAtletaHandler.handle(...)
            ├── Si Rol.JUEZ   → RegistrarJuezHandler.handle(...)
            └── Si Rol.ORGANIZADOR → RegistrarOrganizadorHandler.handle(...)
```

## Implementación

```python
class PerfilRegistroAdapter(PerfilRegistroPort):
    async def crear_perfiles(
        self,
        usuario_id: UUID,
        nombre: str,
        apellido: str,
        email: str,
        roles: list[Rol],
        numero_licencia: str | None = None,
        federacion: str | None = None,
        nombre_organizacion: str | None = None,
    ) -> None:
```

- **Idempotente**: si el perfil ya existe (`AtletaYaRegistrado`, `JuezYaRegistrado`, `OrganizadorYaRegistrado`), la excepción se silencia — la operación es segura de reintentar
- Cada rol es creado de forma independiente: un usuario puede ser atleta y juez simultáneamente
- `usuario_id` no se usa en la creación actual (el ID del perfil se genera en el handler); la correlación se logra por `email`

## Nota de diseño (ADR-020)

La identidad entre `atleta_id` / `juez_id` / `organizador_id` y `usuario_id` de BC Identidad se documenta en el aggregate como invariante pero **no** se enforza por FK — la correlación real es por `email`. Esto es una decisión pragmática del CRUD: los perfiles se buscan siempre por email del JWT, no por ID directo cross-BC.

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- Implementa `PerfilRegistroPort` definido en [[identidad]] (`identidad/domain/ports/perfil_registro_port.py`)
- Orquesta los handlers de BC Registro: [[command-handlers-registro]]
- Instancia [[atleta]], [[juez-organizador]] a través de sus respectivos handlers y repositorios [[sqlite-repositories-registro]]
- Registrado en el contenedor de dependencias de FastAPI al inicializar BC Identidad

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/infrastructure/perfil_registro_adapter.py` | Adapter: crea perfil deportivo al registrar usuario en Identidad |
