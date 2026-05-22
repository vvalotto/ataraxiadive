---
title: "Entidad Organizadora"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/torneo.md
  - docs/architecture/11-bc-torneo.md
---

# Entidad Organizadora

Value Object del aggregate [[torneo]] que identifica al organismo o institución responsable de organizar el evento competitivo.

## Estructura

| Campo | Descripción |
|-------|-------------|
| `nombre` | Nombre de la entidad (ej: "FAAS — Federación Argentina de Actividades Subacuáticas") |
| `tipo` | Tipo de organismo (federación, club, asociación, etc.) |

## Persistencia

`EntidadOrganizadora` se persiste **embebida como JSON** en la fila del aggregate `Torneo` en `torneo.db`. No tiene identidad propia fuera del torneo.

## Distinción con el rol Organizador

`EntidadOrganizadora` es el **organismo institucional** que avala el evento.
El [[roles|rol Organizador]] es la **persona** (usuario del sistema) que gestiona operativamente el torneo en la plataforma.

Un torneo tiene una `EntidadOrganizadora` (ej: FAAS) y puede tener uno o varios usuarios con rol Organizador operando en él — son conceptos distintos.

## Relación con el tipo de reglamento

El tipo de `EntidadOrganizadora` puede estar asociado al reglamento aplicable en la competencia (FAAS, AIDA, CMAS). El algoritmo de [[ranking]] varía según el reglamento.

## BC propietario

[[torneo]] — campo de datos del aggregate `Torneo`.

## Conceptos relacionados

- [[torneo]] — el aggregate que contiene la entidad organizadora
- [[sede]] — la ubicación física del torneo
- [[roles]] — el rol Organizador (persona), diferente de la entidad organizadora (institución)
- [[ranking]] — el algoritmo de ranking puede depender del tipo de reglamento de la entidad
