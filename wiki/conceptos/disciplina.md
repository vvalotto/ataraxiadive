---
title: "Disciplina"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Disciplina

Modalidad de apnea dentro de un [[torneo]]. Define el tipo de prueba y cómo se mide el resultado.

## Tipos de medición

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Por tiempo** | Se mide cuánto tiempo el atleta sostiene la apnea | SYNB, DNF estático |
| **Por distancia** | Se mide la distancia recorrida bajo el agua | DYN, DNF |

El tipo de medición determina cómo se registra el valor de la [[performance]] al finalizar.

## Configuración de una disciplina (etapa Preparación)

El [[roles|Organizador]] define para cada disciplina:
- **Horario de inicio** de la competencia.
- **Número de andariveles** (líneas de competencia simultáneas).
- **Duración por performance** (intervalo entre atletas).

Con estos parámetros se genera la [[grilla]] de salida.

## Relaciones

- Un [[torneo]] selecciona las disciplinas que se realizarán.
- Un [[atleta]] puede inscribirse en múltiples disciplinas del mismo torneo.
- Cada disciplina tiene su propia [[grilla]] de salida.
- Cada disciplina produce [[performance|performances]] independientes.
- El ranking final se calcula por disciplina y categoría.
