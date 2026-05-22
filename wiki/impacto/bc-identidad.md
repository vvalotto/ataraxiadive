---
title: "Impacto: BC Identidad — dependencia transversal de auth"
type: impacto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/identidad.md
  - wiki/decisiones/ADR-020-modelo-usuarios-roles.md
  - wiki/arquitectura/context-map.md
componente: BC Identidad (JWT / claims)
riesgo: muy-alto
bcs_afectados: [torneo, registro, competencia, identidad]
---

# Impacto: BC Identidad — dependencia transversal de auth

## Qué es

BC Identidad es el **Generic Domain** que provee autenticación y roles al sistema. Su output es un JWT con un contrato de claims que todos los BCs funcionales consumen con patrón Conformist.

**Contrato de salida del JWT:**

```json
{
  "sub":      "uuid",
  "email":    "...",
  "nombre":   "...",
  "apellido": "...",
  "rol":      "ATLETA | JUEZ | ORGANIZADOR | ADMIN",
  "exp":      1234567890
}
```

Los guards de autorización (`AtletaDep`, `JuezDep`, `OrganizadorDep`) se definen en `identidad/api/dependencies.py` y se re-exportan desde `shared/api/dependencies.py` para uso transversal en todos los BCs.

## BCs afectados

| BC | Rol | Tipo de dependencia |
|----|-----|-------------------|
| [[arquitectura/identidad]] | Emisor del JWT — propietario del contrato | — |
| [[arquitectura/torneo]] | Conformist | Valida JWT en cada request via `OrganizadorDep` |
| [[arquitectura/registro]] | Conformist | Valida JWT en cada request via `AtletaDep`, `JuezDep`, `OrganizadorDep` |
| [[arquitectura/competencia]] | Conformist | Valida JWT en cada request via `JuezDep`, `OrganizadorDep` |
| [[arquitectura/notificaciones]] | Sin dependencia directa | Downstream de eventos, no de requests de usuario |
| [[arquitectura/resultados]] | Sin dependencia directa | Lee resultados calculados; no requiere auth propia |

**Nota:** Notificaciones y Resultados no consumen JWT — son BCs downstream de eventos y consultas, no de acciones autenticadas del usuario.

## Riesgo de cambio: muy alto

### Cambiar los claims del JWT

Es el cambio de mayor impacto en el sistema. Los tres BCs Conformist (`torneo`, `registro`, `competencia`) aceptan el contrato sin negociar — un cambio de schema en el token los impacta a todos simultáneamente.

**Casos de impacto:**

| Cambio | BCs afectados | Severidad |
|--------|--------------|-----------|
| Renombrar `userId` → `sub` (ya fue hecho) | Torneo, Registro, Competencia | Alto — requiere actualización coordinada |
| Agregar un claim nuevo | Ninguno en operación normal | Bajo — claims adicionales son ignorados |
| Eliminar `rol` del token | Torneo, Registro, Competencia | Muy alto — los guards dependen de `rol` para autorizar |
| Cambiar `rol` de string a array | Torneo, Registro, Competencia | Muy alto — cambio de tipo en el contrato |
| Cambiar la duración de expiración | — | Bajo — solo config de `JWTService` |

**Patrón de propagación:** los BCs no consultan a Identidad en runtime — trabajan con claims locales. Un token emitido antes del cambio sigue siendo válido hasta expirar. El rollout de un cambio de claims requiere sincronizar la emisión (Identidad) con la validación (tres BCs) — o implementar doble validación durante la transición.

### Cambiar los roles disponibles (agregar/eliminar un `Rol`)

Impacta:
- `identidad/domain/value_objects/rol.py` — definición del enum
- Los guards del BC que usa ese rol (`JuezDep`, `OrganizadorDep`, `AtletaDep`)
- BC Registro — las entidades de perfil (`Atleta`, `Juez`, `Organizador`) están acopladas a roles específicos ([[ADR-020-modelo-usuarios-roles]])
- Los tests BDD que asumen roles fijos

### Cambiar la firma del JWT (algoritmo o secreto)

Todos los tokens en circulación quedan inválidos. Impacta a todos los usuarios activos. Requiere rotación coordinada de secreto en las variables de entorno de todos los BCs (`JWT_SECRET`).

### Cambiar la interfaz de `AtletaDep` / `JuezDep` / `OrganizadorDep`

Estos guards se re-exportan desde `shared/api/dependencies.py`. Un cambio de firma (parámetros, tipo de retorno) impacta cada endpoint que los usa en los tres BCs Conformist.

## Qué NO cambia al modificar Identidad

- El event store de Competencia — la autenticación no está en el dominio de la competencia.
- Los rankings calculados en Resultados — no requieren auth para ser leídos.
- Los eventos de dominio inter-BC — viajan sin JWT (son internos al sistema).

## Mecánica de la dependencia Conformist

Los BCs downstream no consultan a Identidad en runtime para validar tokens — usan el secreto compartido `JWT_SECRET` para verificar la firma localmente. Identidad no es un punto de fallo en runtime de cada request — solo lo es en el flujo de login.

```
Request con JWT → BC Torneo/Registro/Competencia
                   └→ verifica firma con JWT_SECRET (local, sin llamada a Identidad)
                   └→ extrae claims: sub, email, nombre, apellido, rol
                   └→ aplica guard de rol (AtletaDep / JuezDep / OrganizadorDep)
```

## Recorrido en el wiki

```
[[arquitectura/identidad]]
  → [[ADR-020-modelo-usuarios-roles]] (multi-rol + perfiles en Registro)
  → [[arquitectura/context-map]] sección "Identidad → Torneo, Registro, Competencia"
  → [[arquitectura/torneo]] / [[arquitectura/registro]] / [[arquitectura/competencia]]
    (cada uno, sección "Auth / Restricciones")
```

## ADRs relacionados

- [[ADR-020-modelo-usuarios-roles]] — `roles: list[Rol]`; JWT lleva el rol elegido al login; perfiles por rol en Registro
- [[ADR-019-politica-contrasenas]] — política de contraseñas aplicada en Identidad
- [[ADR-005-bounded-contexts-ddd-estrategico]] — separación Identidad/Registro; Identidad como Generic Domain reemplazable
