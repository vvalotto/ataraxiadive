---
title: "Categoria"
type: concepto
last_updated: "2026-05-22"
sources:
  - wiki/decisiones/ADR-022-categoria-shared.md
  - wiki/arquitectura/registro.md
---

# Categoria

Value Object compartido (`StrEnum`) que clasifica a un [[atleta]] según criterios reglamentarios (edad, género u otro). Es el único elemento del modelo de dominio que vive en `shared/` por ser importado por múltiples BCs.

## Decisión de ubicación

Originalmente definido en `registro/domain/value_objects/categoria.py`. Movido a `shared/domain/value_objects/categoria.py` en SP6 ([[ADR-022-categoria-shared]]) porque era importado por tres BCs distintos, introduciendo acoplamiento indebido.

**Regla resultante:** Todo import de `Categoria` usa `shared.domain.value_objects.categoria`. No puede importarse desde `registro`.

## Usos por BC

| BC | Para qué usa `Categoria` |
|----|--------------------------|
| [[registro]] | Clasificar al atleta en el momento del registro; dato autodeclarado |
| [[competencia]] | Filtrar performances por categoría en consultas y proyecciones |
| [[resultados]] | Agrupar entradas del ranking overall por categoría |

## Invariante notable

`ADMIN` no puede asignarse desde la UI — solo por acceso directo a la base de datos. Es una categoría de superusuario técnica, no deportiva.

## Relación con rankings

La [[categoria]] del atleta determina en qué grupo aparece en el ranking overall. El algoritmo FAAS/CMAS/AIDA puede definir categorías distintas (ver [[ranking]]).

## ADRs relacionados

- [[ADR-022-categoria-shared]] — decisión de mover `Categoria` a `shared/`
- [[ADR-006-estructura-bc-first]] — la regla que permite imports desde `shared/domain/` como única excepción cross-BC
- [[ADR-005-bounded-contexts-ddd-estrategico]] — el mapa de BCs que dependen de este VO
