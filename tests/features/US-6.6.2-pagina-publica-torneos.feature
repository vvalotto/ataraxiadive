Feature: US-6.6.2 — Página pública de torneos

  Scenario: Visitante sin login accede a /torneos via endpoint publico
    Given no hay token de autenticacion en el sistema
    When se consulta GET /torneos
    Then la respuesta es 200
    And cada torneo tiene nombre, fecha_inicio, sede y estado

  Scenario: Torneos CANCELADOS no aparecen en la lista publica
    Given existe un torneo con estado CANCELADO
    When se consulta GET /torneos
    Then ese torneo no aparece en la lista

  Scenario: Torneo en INSCRIPCION_ABIERTA aparece en la lista publica
    Given existe un torneo con estado INSCRIPCION_ABIERTA
    When se consulta GET /torneos
    Then ese torneo aparece en la lista con su estado
