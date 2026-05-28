---
title: "RF — Inscripción de Atletas"
type: trazabilidad-rf
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
us_refs:
  - US-3.2.2
  - US-3.2.3
  - US-3.3.2
  - US-ADJ-4.4
---

# RF — Inscripción de Atletas

Requerimientos funcionales del área de inscripción. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-IN-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID           | Requerimiento                                                        | Respuesta / Regla                                                 |
| ------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [[RF-IN-01]] | ¿Las categorías son fijas o configurables?                           | Hoy fijas; debería ser configurable (ej: senior masculino 18-50). |
| [[RF-IN-02]] | ¿El brevet es obligatorio?                                           | **No.**                                                           |
| [[RF-IN-03]] | ¿Hay límite de atletas por torneo o disciplina?                      | **No.**                                                           |
| [[RF-IN-04]] | ¿Un atleta puede cancelar su inscripción?                            | **Sí,** hasta el día anterior a la competencia.                   |
| [[RF-IN-05]] | ¿Se requiere apto médico?                                            | **Sí.**                                                           |
| [[RF-IN-06]] | ¿La inscripción tiene costo?                                         | **Sí.** Se pide constancia de pago (no gestión de pagos).         |
| [[RF-IN-07]] | ¿Cómo se resuelve un conflicto con datos de BD externa?              | **Pendiente de definición.**                                      |
| [[RF-IN-08]] | ¿El género tiene efecto más allá de la categoría?                    | **Solo categoría.**                                               |
| [[RF-IN-09]] | ¿Un atleta puede inscribirse en categorías distintas por disciplina? | **No.** Una categoría por torneo.                                 |
| [[RF-IN-10]] | ¿El club del atleta es obligatorio?                                  | **Sí.** Debe reflejarse en grillas y reportes.                    |

## Reglas de negocio clave

- El **apto médico** es requisito de inscripción — el sistema lo registra.
- Se pide **constancia de pago**, pero el sistema no gestiona pagos directamente.
- El **club es obligatorio** y aparece en grillas y reportes.
- El **brevet no es obligatorio**.
- La **categoría** es única por atleta dentro de un torneo (no varía por disciplina).
- Un atleta puede **cancelar hasta el día antes** de competir.

## Pendientes en elicitación

| ID | Pendiente | Clasificación |
|----|-----------|---------------|
| [[RF-IN-07]] | Resolución de conflictos entre datos ingresados y BD externa de atletas | **Indefinido** — depende de definir RF-IG-01 (¿existe BD externa FAAS? ¿qué protocolo?) |

## Estado de implementación (lint-001)

RF-IN-07 no tiene US asociada. La indefinición es de negocio, no técnica: la integración con BD externa está en el área RF-IG sin definir desde la elicitación inicial (feb 2026).

**Acción si se planea SP8:** definir primero el área RF-IG completa antes de derivar US para RF-IN-07.

## BCs que implementan esta área

- [[registro]] — gestión de la inscripción de atletas
- [[identidad]] — datos de identidad del atleta como usuario
