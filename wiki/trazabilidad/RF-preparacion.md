---
title: "RF — Preparación de Competencias"
type: trazabilidad-rf
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
us_refs:
  - US-1.2.1
  - US-2.1.1
  - US-2.1.2
  - US-2.1.3
  - US-2.3.1
  - US-4.1.4
  - US-ADJ-4.2
---

# RF — Preparación de Competencias

Requerimientos funcionales del área de preparación. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-PR-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID | Requerimiento | Respuesta / Regla |
|----|--------------|-------------------|
| RF-PR-01 | ¿Qué es un anuncio (AP)? | Marca que el atleta declara que intentará lograr. AP = Announced Performance. |
| RF-PR-02 | ¿Hay valores mínimos/máximos para anuncios? | No se permiten valores 0 o negativos. |
| RF-PR-03 | ¿Un atleta puede modificar su anuncio? | **No.** Una vez registrado, es definitivo. |
| RF-PR-04 | ¿Qué pasa si un atleta no registra su anuncio? | **No compite.** |
| RF-PR-05 | ¿Cómo se determina el orden de salida? | Depende de la [[disciplina]]: **por distancia → menor a mayor; por tiempo → mayor a menor.** |
| RF-PR-06 | ¿Pueden competir varios atletas simultáneamente? | **Sí,** mediante andariveles (líneas de competencia). |
| RF-PR-07 | ¿El organizador puede modificar el orden manualmente? | **Sí.** |
| RF-PR-08 | ¿Qué es la "duración de cada performance"? | Tiempo entre Tiempos Oficiales (OT = Official Top). Lo determina el juez por prueba. |

## Reglas de negocio clave

- **AP (Announced Performance):** el [[anuncio]] es definitivo — no se puede modificar.
- **Atleta sin anuncio = no compite.** No hay excepción.
- **Orden de la [[grilla]]:** distancia → menor a mayor; tiempo → mayor a menor.
- **OT (Official Top):** intervalo entre atletas en la grilla — lo define el juez, no el organizador.
- Los valores de anuncio deben ser **mayores que cero** (sin límite superior).
- El [[roles|Organizador]] puede **ajustar manualmente** el orden de la grilla generada.

## BCs que implementan esta área

- [[competencia]] — generación de grillas, gestión de anuncios
- [[torneo]] — apertura del período de preparación y notificación a atletas
