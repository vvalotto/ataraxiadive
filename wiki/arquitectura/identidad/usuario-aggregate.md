---
title: "Identidad — Aggregate Usuario"
type: arquitectura-componente
bc: identidad
capa: domain
tipo_componente: aggregate
responsabilidad: "Perfil de acceso al sistema: credenciales, lista de roles, estado activo — modelo multi-rol (ADR-020)"
interfaces_out:
  - UsuarioRepositoryPort
adr_refs: [ADR-019, ADR-020]
last_updated: "2026-05-23"
sources:
  - src/identidad/domain/aggregates/usuario.py
  - src/identidad/domain/value_objects/rol.py
---

# Aggregate Usuario

## Responsabilidad

Modela la **identidad de acceso** de una persona al sistema. No contiene datos deportivos (esos viven en BC Registro). Controla las invariantes sobre credenciales y roles.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario_id` | UUID | Autogenerado |
| `nombre` | str | No vacío (INV-ID-01) |
| `apellido` | str | No vacío (INV-ID-01) |
| `email` | str | Único en el sistema |
| `password_hash` | str | Hash bcrypt — nunca plain text |
| `roles` | `list[Rol]` | Al menos uno; sin duplicados |
| `activo` | bool | Default `True` |

## Invariantes

| Inv | Descripción |
|-----|-------------|
| INV-ID-01 | `nombre` y `apellido` no vacíos (se trimean) |
| RolesVacios | `roles` no puede ser lista vacía |
| RolDuplicado | No puede haber dos entradas del mismo rol |

## Value Object: Rol

```python
class Rol(StrEnum):
    ORGANIZADOR = "ORGANIZADOR"
    JUEZ        = "JUEZ"
    ATLETA      = "ATLETA"
    ADMIN       = "ADMIN"
```

Un usuario puede tener **múltiples roles** simultáneamente (ADR-020). El JWT lleva **un único rol activo** — elegido al hacer login o auto-seleccionado si el usuario tiene solo uno.

## Modelo multi-rol (ADR-020)

El campo `roles: list[Rol]` reemplazó al campo `rol: Rol` anterior. La migración fue parte de SP-ADJ-11. El repositorio mantiene retrocompatibilidad vía `_migrate_rol_to_roles`.

**Regla clave**: `ADMIN` no puede registrarse via API pública (`RolNoPermitido`). Se crea directamente en DB.

## Relaciones

- Persiste en `identidad.db` via [[sqlite-usuario-repository]]
- El `usuario_id` es el anchor que correlaciona con `atleta_id` / `juez_id` / `organizador_id` en BC Registro (correlación por email en la práctica)
- Al crear un usuario, [[command-handlers-identidad]] llama a [[perfil-registro-adapter]] para crear los perfiles deportivos correspondientes
