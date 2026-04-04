# Fase 1 — US-ADJ-3.6
## Generacion de escenarios BDD

Para `US-ADJ-3.6` no se generan escenarios BDD nuevos.

Motivo:

- `SP-ADJ-03` fue acordado como sprint de ajuste tecnico sin expansion de la
  capa BDD.
- La US es un refactor arquitectonico interno del BC `identidad` sin cambio de
  comportamiento observable esperado.
- La cobertura se sostendra con tests unitarios, tests de API existentes y
  validacion de calidad (`CodeGuard`).

Impacto operativo:

- Se preserva el pipeline de `implement-us`.
- La Fase 1 queda documentada como omitida explicitamente.
- No se crean `.feature` ni steps nuevos para esta US.
