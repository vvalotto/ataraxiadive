---
title: "Performance"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Performance

La actuación de un [[atleta]] en una [[disciplina]] dentro de una [[competencia]]. Es la unidad central de registro del sistema.

## Ciclo de una performance

```
Llamada al atleta → Confirmación de presencia → Inicio (cronómetro) → Finalización → Resultado
```

## Tipos de finalización

| Tipo | Descripción |
|------|-------------|
| **Performance válida** | El atleta completa la prueba. Se registra el valor (distancia o tiempo). [[tarjeta]] blanca. |
| **Black-out** | El atleta pierde el conocimiento. Se registra el hecho *y* la distancia alcanzada. |
| **DNS (Did Not Start)** | El atleta no se presenta al llamado. Descalificación inmediata, sin tiempo de espera. |
| **Descalificación** | El atleta incurre en una falta. [[tarjeta]] roja. Lleva código de penalización. |

> **Nota:** El término correcto es **black-out** (pérdida de consciencia), no "back-out". El black-out registra también la distancia alcanzada.

## Valor de la performance

Depende del tipo de [[disciplina]]:
- **Por tiempo:** el [[roles|Juez]] toma el tiempo manualmente e ingresa el valor (el sistema no cronometra).
- **Por distancia:** el Juez ingresa los metros con decimales al finalizar.

## Responsabilidades del Juez

- Llama al atleta, confirma su presencia.
- Confirma el inicio → arranca el cronómetro.
- Confirma la finalización → registra el resultado.
- Emite [[tarjeta]] (blanca o roja) y penalización si corresponde.

## Relaciones

- Una performance pertenece a un [[atleta]] y a una [[disciplina]].
- El resultado de una performance integra el ranking final por disciplina y categoría.
- Ver [[tarjeta]] para los posibles estados de validez.
- Ver [[anuncio]] para la marca previa que el atleta declara antes de competir.
