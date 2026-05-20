---
title: "Tarjeta"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Tarjeta

Indicador del resultado de validez de una [[performance]]. Emitida por el [[roles|Juez]] al finalizar la actuación del [[atleta]].

## Tipos

| Tarjeta | Significado | Efecto |
|---------|-------------|--------|
| **Blanca** | Performance válida | El valor registrado (tiempo o distancia) es oficial y cuenta para el ranking |
| **Roja** | Descalificación | La performance no computa. Se registra el código de la falta. |

## Tarjeta Roja — Descalificación

Cuando el [[roles|Juez]] emite tarjeta roja debe indicar:
- **Código de penalización:** identifica la causa de la descalificación según el reglamento.

Los atletas descalificados aparecen al final del ranking de su [[disciplina]] y categoría.

## Nota sobre penalizaciones acumulables

Las penalizaciones en AtaraxiaDive son acumulables (ver [[ADR-014-penalizaciones-acumulables]]). La tarjeta roja no es binaria — el sistema puede registrar múltiples penalizaciones para una performance.

## Relaciones

- Una tarjeta es el resultado de una [[performance]].
- La tarjeta blanca habilita que el valor de la performance integre el ranking en [[resultados]].
- La tarjeta roja se registra con su código en el BC [[competencia]].
