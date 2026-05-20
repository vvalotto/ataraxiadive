---
title: "RF — Integración con Sistemas Externos"
type: trazabilidad
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
---

# RF — Integración con Sistemas Externos

Requerimientos funcionales del área de integración. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-IG-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Contexto

El sistema menciona una base de datos externa de atletas (posiblemente de la FAAS — Federación Argentina de Actividades Subacuáticas). La integración fue elicitada pero quedó pendiente de definición en todos sus aspectos técnicos.

## Requerimientos — todos pendientes de definición

| ID | Pregunta | Estado |
|----|---------|--------|
| RF-IG-01 | ¿La BD externa es de la FAAS? ¿Qué formato/protocolo? | **Pendiente** |
| RF-IG-02 | ¿La consulta es solo lectura o también escritura? | **Pendiente** |
| RF-IG-03 | ¿Qué pasa si la BD externa no está disponible? | **Pendiente** |
| RF-IG-04 | ¿Se exportan resultados a sistemas externos (AIDA/CMAS)? | **Pendiente** |

## Implicación arquitectónica

Toda el área de integración externa quedó sin definir en la elicitación inicial. La decisión arquitectónica tomada fue aislar la consulta a BD externa detrás de un puerto (ver BC [[registro]]), permitiendo que la integración se defina e implemente sin afectar el núcleo de dominio.

La situación actual del atleta en el sistema (auto-registro + consulta opcional a BD externa) convive con la indefinición de este punto.

## BCs relacionados

- [[registro]] — BC donde se materializa la integración cuando esté definida
