---
title: "RF — Ejecución de Competencias"
type: trazabilidad-rf
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
us_refs:
  - US-1.2.1
  - US-1.2.2
  - US-1.2.3
  - US-1.2.4
  - US-1.2.5
  - US-1.2.6
  - US-1.3.1
  - US-1.4.1
  - US-1.4.2
  - US-2.2.1
  - US-2.2.2
  - US-3.4.1
  - US-4.3.2
  - US-4.3.3
  - US-4.3.5
---

# RF — Ejecución de Competencias

Requerimientos funcionales del área de ejecución. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-EJ-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID | Requerimiento | Respuesta / Regla |
|----|--------------|-------------------|
| [[RF-EJ-01]] | ¿Puede haber más de un juez por disciplina? | **Sí.** Juez principal, jueces de línea, safety divers. |
| [[RF-EJ-02]] | ¿Qué pasa si un atleta no se presenta (DNS)? | **Descalificación inmediata.** Sin tiempo de espera. |
| [[RF-EJ-03]] | ¿Hay tarjeta amarilla (penalización parcial)? | **Sí.** Reglas de negocio configurables. |
| [[RF-EJ-04]] | ¿Cuáles son los códigos de penalización? | **Pendiente.** Posiblemente AIDA/CMAS. |
| [[RF-EJ-05]] | ¿El cronometraje lo hace el sistema? | **No.** El juez toma el tiempo manualmente e ingresa el valor. |
| [[RF-EJ-06]] | ¿Un juez puede corregir un resultado ya registrado? | **Sí.** Con período de protesta. |
| [[RF-EJ-07]] | ¿Qué se registra en un black-out? | Black-out (no back-out): se registra la distancia alcanzada también. |
| [[RF-EJ-08]] | ¿Las distancias usan decimales? | **Sí.** Metros con decimales. |
| [[RF-EJ-09]] | ¿El protocolo de superficie (SP) lo evalúa el sistema? | **No.** |
| [[RF-EJ-10]] | ¿Se registra el SP por separado o solo su efecto? | **Solo el resultado** (tarjeta blanca/amarilla/roja). |

## Reglas de negocio clave

- **DNS (Did Not Start):** descalificación inmediata, sin tiempo de espera al llamado.
- **Black-out** (no "back-out"): el atleta pierde el conocimiento. Se registra el hecho *y* la distancia alcanzada.
- **Cronómetro manual:** el [[roles|Juez]] toma el tiempo; el sistema registra el valor que él ingresa.
- **Corrección de resultados:** posible, con período de protesta.
- **Tarjeta amarilla:** existe y tiene reglas configurables (ver [[ADR-014-penalizaciones-acumulables]]).
- **Distancias:** metros con decimales.
- **SP (Surface Protocol):** el sistema registra solo el resultado (tarjeta), no la evaluación del protocolo.

## Pendientes en elicitación

| ID | Pendiente | Clasificación |
|----|-----------|---------------|
| [[RF-EJ-04]] | Códigos de penalización específicos (AIDA/CMAS u otro reglamento) | **Backlog activo** — la infraestructura técnica existe; solo falta definir los códigos |

## Estado de implementación (lint-001)

RF-EJ-04 no tiene US asociada, pero la infraestructura para penalizaciones está implementada:
- El modelo `PenalizacionTecnica` (código + deducción) existe en [[competencia]]
- Los códigos son configurables como datos ([[ADR-004-reglas-como-datos]] — `card_rule_config`)
- El concepto está documentado en [[penalizacion]]

**Lo que falta:** definir y cargar los códigos de penalización AIDA/CMAS/FAAS en `card_rule_config`. No requiere cambio de código — solo de configuración. Candidato a US en SP8.

## BCs que implementan esta área

- [[competencia]] — registro de performances, tarjetas, penalizaciones
