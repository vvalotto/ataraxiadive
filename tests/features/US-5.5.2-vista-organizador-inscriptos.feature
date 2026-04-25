Feature: US-5.5.2 — Vista del organizador con inscriptos y estado AP

  Background:
    Given el torneo "BA Open 2026" tiene inscriptos activos con datos completos
    And la atleta "ana@email.com" esta inscripta en DNF y STA con nombre "Garcia, Ana"
    And el atleta "carlos@email.com" esta inscripto en DYN con nombre "Lopez, Carlos"
    And existe una inscripcion CANCELADA de "pepe@email.com"

  Scenario: organizador obtiene lista enriquecida de inscriptos
    Given el organizador esta autenticado
    When realiza GET /registro/torneos/{id}/inscriptos-detalle
    Then el sistema responde 200
    And la respuesta contiene a "Garcia" con disciplinas DNF y STA
    And la respuesta contiene a "Lopez" con disciplinas DYN
    And la respuesta no contiene la inscripcion CANCELADA

  Scenario: inscripcion cancelada no aparece en la lista
    Given el organizador esta autenticado
    When realiza GET /registro/torneos/{id}/inscriptos-detalle
    Then la respuesta no incluye inscripciones con estado CANCELADA

  Scenario: acceso sin rol organizador es rechazado
    Given el usuario esta autenticado con rol ATLETA
    When realiza GET /registro/torneos/{id}/inscriptos-detalle
    Then el sistema responde 403

  Scenario: torneo sin inscriptos devuelve lista vacia
    Given existe el torneo "Torneo Vacio" sin inscriptos activos
    And el organizador esta autenticado
    When el organizador realiza GET /registro/torneos/{id-vacio}/inscriptos-detalle
    Then el sistema responde 200
    And la respuesta es una lista vacia
