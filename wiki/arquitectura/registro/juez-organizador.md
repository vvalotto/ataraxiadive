---
title: "Registro — Aggregates Juez y Organizador"
type: arquitectura-componente
bc: registro
capa: domain
tipo_componente: aggregate
responsabilidad: "Perfiles deportivos del Juez y del Organizador — nuevas entidades de SP-ADJ-11 (modelo multi-rol)"
interfaces_out:
  - JuezRepositoryPort
  - OrganizadorRepositoryPort
adr_refs: [ADR-020, ADR-007]
last_updated: "2026-05-23"
sources:
  - src/registro/domain/aggregates/juez.py
  - src/registro/domain/aggregates/organizador.py
---

# Aggregates Juez y Organizador

## Contexto

Entidades creadas en **SP-ADJ-11** (ADR-020) al introducir el modelo multi-rol. Antes solo existía `Atleta`. Ahora cada rol funcional tiene su entidad de perfil propia en BC Registro.

---

## Aggregate Juez

### Campos

| Campo | Obligatorio | Invariante |
|-------|:-----------:|-----------|
| `juez_id` | ✅ | UUID — coincide con `usuario_id` de Identidad |
| `email` | ✅ | Formato válido (INV-11.4-01) |
| `numero_licencia` | — | No vacío si presente (INV-11.4-03) |
| `federacion` | — | No vacío si presente (INV-11.4-04) |

### Operaciones
- `actualizar(numero_licencia, federacion)` — actualiza campos opcionales

---

## Aggregate Organizador

### Campos

| Campo | Obligatorio | Invariante |
|-------|:-----------:|-----------|
| `organizador_id` | ✅ | UUID — coincide con `usuario_id` de Identidad |
| `email` | ✅ | Formato válido (INV-11.5-01) |
| `nombre_organizacion` | — | No puede ser string vacío si presente (INV-11.5-03); `None` es válido |

### Operaciones
- `actualizar(nombre_organizacion)` — `None` limpia el campo explícitamente

---

## Notas comunes

Ambos son `@dataclass` sin Event Sourcing. La creación de perfiles está orquestada por [[perfil-registro-adapter]], que los instancia cuando un usuario de BC Identidad tiene los roles `JUEZ` u `ORGANIZADOR`.

## Relaciones

**Contenedor:** [[arquitectura/registro]]

- `juez_id` / `organizador_id` = `usuario_id` del BC [[identidad]]
- Son creados vía [[perfil-registro-adapter]] al registrarse un nuevo usuario con esos roles
- Sus repositorios son [[juez-repository-port]] y [[organizador-repository-port]]

## Código fuente

| Archivo | Descripción |
|---|---|
| `src/registro/domain/aggregates/juez.py` | Aggregate Juez — perfil deportivo del juez |
| `src/registro/domain/aggregates/organizador.py` | Aggregate Organizador — perfil deportivo del organizador |
