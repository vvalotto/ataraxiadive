---
title: "Grilla"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Grilla

Planilla de salida que define el orden, horario y asignación de andariveles de los [[atleta|atletas]] para una [[disciplina]] específica.

## Propósito

Organizar la ejecución de la [[disciplina]] determinando quién compite, cuándo y en qué andarivel.

## Cómo se construye (etapa Preparación)

1. Los [[atleta|atletas]] declaran sus [[anuncio|anuncios]] (marcas previas). Atleta sin anuncio = no compite.
2. El [[roles|Organizador]] configura la [[disciplina]]: horario de inicio, número de andariveles.
3. El [[roles|Juez]] define el **OT (Official Top)** — intervalo entre Tiempos Oficiales de cada atleta.
4. La grilla se genera con el orden según el tipo de disciplina:
   - **Distancia:** de menor a mayor anuncio.
   - **Tiempo:** de mayor a menor anuncio.
5. El Organizador puede ajustar el orden manualmente antes de confirmar.

## Contenido de la grilla

| Campo | Descripción |
|-------|-------------|
| Atleta | Quién compite |
| Andarivel | Línea de competencia asignada |
| Horario de salida | Momento en que el atleta es llamado |
| Anuncio | Marca declarada por el atleta |

## Uso en ejecución

Durante la [[disciplina|ejecución]], el [[roles|Juez]] sigue la grilla para llamar a cada [[atleta]] en el orden y horario establecido.

## Relaciones

- Una grilla es por [[disciplina]] y por [[torneo]].
- Requiere los [[anuncio|anuncios]] de los atletas para construirse.
- Es el input principal para la fase de ejecución de la [[disciplina]].
