Feature: Edicion completa del torneo

  Background:
    Given el sistema tiene una base de datos limpia de torneos

  Scenario: El organizador edita el nombre y sede de un torneo en CREADO
    Given existe un torneo "Buenos Aires Open 2025" en estado CREADO
    When el organizador actualiza el torneo con nombre "BA Open 2025 Corregido" y ciudad "Mar del Plata"
    Then el torneo tiene nombre "BA Open 2025 Corregido"
    And la sede del torneo tiene ciudad "Mar del Plata"

  Scenario: El organizador edita un torneo en INSCRIPCION_ABIERTA
    Given existe un torneo "Torneo Inscripcion" en estado INSCRIPCION_ABIERTA
    When el organizador actualiza el torneo con nombre "Torneo Inscripcion Corregido" y ciudad "Rosario"
    Then el torneo tiene nombre "Torneo Inscripcion Corregido"
    And la sede del torneo tiene ciudad "Rosario"

  Scenario: No se puede editar un torneo en EJECUCION
    Given existe un torneo "Torneo En Ejecucion" en estado EJECUCION
    When el organizador intenta actualizar el torneo con nombre "Nombre Nuevo"
    Then la respuesta es 409 con detalle sobre estado invalido

  Scenario: La edicion no afecta las disciplinas del torneo
    Given existe un torneo "Torneo Con Disciplinas" en estado CREADO con disciplinas STA y DNF
    When el organizador actualiza el torneo con nombre "Torneo Renombrado" y ciudad "Cordoba"
    Then el torneo tiene nombre "Torneo Renombrado"
    And las disciplinas STA y DNF permanecen sin cambios
