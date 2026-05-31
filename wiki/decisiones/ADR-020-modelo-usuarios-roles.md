---
title: "ADR-020: Modelo de usuarios con múltiples roles y perfiles por rol"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-020-modelo-usuarios-roles.md
estado: Aceptada
fecha: 2026-05-16
bcs_afectados: [identidad, registro]
rnf_refs:
  - RNF-05-seguridad-auditoria-inalterable
---

# ADR-020: Modelo de usuarios con múltiples roles y perfiles por rol

## Decisión

`Usuario` pasa de `rol: Rol` (único) a `roles: list[Rol]` (JSON array en SQLite). El JWT lleva el rol elegido al momento del login como string único. Cada rol funcional tiene una entidad de perfil propia en BC Registro.

## Por qué

Un juez-atleta —caso real y frecuente en apnea local y regional— necesitaba dos cuentas con emails distintos. Inaceptable en producción.

## Modelo de perfiles en BC Registro

| Entidad | Campos obligatorios | Campos opcionales |
|---------|--------------------|--------------------|
| `Atleta` | documento_tipo, documento_numero, telefono, fecha_nacimiento | club, categoria, brevet |
| `Juez` | documento_tipo, documento_numero, telefono, numero_licencia | federacion |
| `Organizador` | telefono | nombre_organizacion |

`Atleta` existía. `Juez` y `Organizador` son entidades nuevas con tablas propias en la DB de BC Registro.

## Flujo de login

- **1 rol:** acceso directo al portal correspondiente.
- **N roles:** selector de rol antes de acceder. El JWT lleva el rol elegido.

Para cambiar de portal hay que volver a loguearse — limitación asumida conscientemente (alternativa JWT multi-rol fue descartada por complejidad innecesaria para la etapa actual).

## Reglas de roles

- Un usuario no puede tener el mismo rol dos veces (invariante del aggregate).
- Nuevos roles se agregan desde "Mis Datos" en cualquier portal.
- `JUEZ` y `ORGANIZADOR` se pueden quitar; `ATLETA` no — el historial de competencias queda vinculado al perfil.
- `ADMIN` no se asigna desde la UI — solo desde la DB directamente.

## Consecuencias vigentes

- Columna `roles TEXT NOT NULL` (JSON array) reemplaza `rol TEXT NOT NULL` en `usuarios`.
- Migración de DB necesaria.
- Los guards de autorización (`require_rol`) no cambian de interfaz.
- La `categoria` del atleta es autodeclarada; el sistema no la valida contra criterios federativos.
- `ADMIN` es superrol interno — no aparece en el registro público.

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — separación Identidad/Registro que fundamenta tener perfiles en BC Registro
- [[ADR-019-politica-contrasenas]] — política aplicada en el flujo de registro
- [[ADR-006-estructura-bc-first]] — la estructura de BCs donde viven estas entidades
