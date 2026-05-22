---
title: "Sede"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/arquitectura/torneo.md
  - docs/architecture/11-bc-torneo.md
---

# Sede

Value Object del aggregate [[torneo]] que representa la ubicación física donde se realiza el evento competitivo.

## Estructura

| Campo | Descripción |
|-------|-------------|
| `nombre` | Nombre del lugar (ej: "Club Náutico del Puerto") |
| `ciudad` | Ciudad donde se realiza |
| `pais` | País |

## Persistencia

`Sede` se persiste **embebida como JSON** dentro de la fila del aggregate `Torneo` en `torneo.db`. No tiene tabla propia ni identidad independiente — es parte del torneo.

## Relevancia

La sede aparece en la publicación de resultados y en la exportación CSV/JSON del torneo. El BC [[resultados]] la consume read-only para enriquecer los reportes.

## BC propietario

[[torneo]] — campo de datos del aggregate `Torneo`.

## Conceptos relacionados

- [[torneo]] — el aggregate que contiene la sede
- [[entidad-organizadora]] — la organización responsable del torneo, distinta de la sede física
