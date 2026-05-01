# Specs IEDD

> **Estado documental:** indice de vigencia para especificaciones. Las specs
> preservan el contrato usado para implementar cada US en su momento; no todas
> describen el estado actual del producto.

## Como leer esta carpeta

- `sp1/`, `sp2/`, `sp3/` y `sp4/`: historico cerrado. Usar para trazabilidad,
  auditoria de decisiones y reconstruccion de comportamiento implementado.
- `sp5/`: specs del subproyecto vigente. Las US ya mergeadas son historicas de
  cierre; las US futuras deben contrastarse con `docs/plans/sp5/PLAN-SP5.md`.
- `sp-adj-*`: ajustes tecnicos, documentales o funcionales cerrados alrededor de
  baselines. Usar junto con `.cm/baselines/`.

## Fuentes canonicas relacionadas

- Alcance vigente SP5: `docs/plans/sp5/PLAN-SP5.md`.
- Estado por baseline: `.cm/baselines/`.
- Trazabilidad RF -> US: `docs/traceability/matrix.md`.
- Arquitectura vigente: `docs/architecture/`.

