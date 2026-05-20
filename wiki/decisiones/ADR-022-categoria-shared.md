---
title: "ADR-022: Ubicación del Value Object Categoria en shared/"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-022-categoria-shared.md
estado: Aceptada
fecha: 2026-05-02
bcs_afectados: [registro, competencia, resultados]
---

# ADR-022: Ubicación del Value Object `Categoria` en `shared/`

## Decisión

`Categoria` (StrEnum) se mueve de `registro/domain/value_objects/categoria.py` a `shared/domain/value_objects/categoria.py`. Refactor aplicado en SP6.

## Por qué

`Categoria` era importado por múltiples BCs (registro, competencia, resultados), introduciendo acoplamiento de BC Registro hacia BCs que no dependen de él conceptualmente. Un value object transversal del dominio pertenece a `shared/`, no al BC donde fue creado originalmente. Consistente con la regla de [[ADR-006-estructura-bc-first]] que permite imports desde `shared/domain/` como única excepción cross-BC.

## Consecuencias vigentes

- Todo código que importaba `registro.domain.value_objects.categoria` debe usar `shared.domain.value_objects.categoria`.
- El refactor se aplicó en SP6 como tarea única — mover archivo + actualizar imports (tests incluidos).
- `ADMIN` no se puede asignar desde la UI — solo desde la DB directamente.

## ADRs relacionados

- [[ADR-006-estructura-bc-first]] — la regla de imports cross-BC que fundamenta esta decisión
- [[ADR-005-bounded-contexts-ddd-estrategico]] — el mapa de BCs que comparten `Categoria`
