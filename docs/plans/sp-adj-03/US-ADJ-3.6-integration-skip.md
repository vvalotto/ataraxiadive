# Fase 5 — US-ADJ-3.6
## Tests de integracion

Para `US-ADJ-3.6` no se agregan ni se ejecutan tests de integracion nuevos del
tipo repositorio/infraestructura persistente.

Motivo:

- el refactor no modifica `SQLiteUsuarioRepository`
- no altera schema ni persistencia
- el riesgo principal esta en wiring de autenticacion, no en acceso a datos

Cobertura equivalente elegida:

- tests unitarios de handlers desacoplados
- tests unitarios de dependencias/API
- validacion HTTP observable en la Fase 6 usando la suite existente de
  identidad JWT
