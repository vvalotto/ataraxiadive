---
title: "Anuncio"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Anuncio

Declaración anticipada de la marca que un [[atleta]] planea alcanzar en una [[disciplina]]. Se registra durante la etapa de Preparación del [[torneo]].

## Propósito

El anuncio permite al [[roles|Organizador]] construir la [[grilla]] de salida antes de que comience la ejecución. Los atletas se ordenan en la grilla según sus anuncios.

## Flujo

1. El [[roles|Organizador]] abre la etapa de Preparación y notifica a los atletas.
2. El sistema envía un mail a cada [[atleta]] inscripto indicándole que declare sus anuncios.
3. El atleta declara su marca esperada para cada [[disciplina]] en la que se inscribió.
4. Con los anuncios recibidos, el Organizador genera la [[grilla]].

## Naturaleza del anuncio

- Es una **declaración definitiva** — no puede modificarse una vez registrado.
- El valor debe ser **mayor que cero** (no se permiten valores 0 o negativos).
- **Atleta sin anuncio dentro del plazo = no compite.** Sin excepciones.
- La [[performance]] real puede ser mayor, menor o igual al anuncio.
- En apnea competitiva, superar el anuncio en exceso puede generar penalización según reglamento.

## Relaciones

- Un anuncio pertenece a un [[atleta]] y a una [[disciplina]] dentro de un [[torneo]].
- Es prerequisito para la construcción de la [[grilla]].
- No debe confundirse con el resultado de la [[performance]].
