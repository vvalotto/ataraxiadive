Feature: US-3.2.3 — Inscripcion de atleta a torneo

  Scenario: inscribir atleta exitosamente
    Given atleta registrado y torneo en estado INSCRIPCION_ABIERTA con disciplinas STA y DNF
    When POST /registro/inscripciones con atleta_id, torneo_id y disciplinas STA
    Then 201 con inscripcion_id
    And GET /registro/torneos/{torneo_id}/inscriptos incluye al atleta

  Scenario: torneo no disponible para inscripcion
    Given torneo en estado CREADO no INSCRIPCION_ABIERTA
    When POST /registro/inscripciones con atleta_id y torneo_id
    Then 409 Conflict con detalle TorneoNoDisponible

  Scenario: disciplina no disponible en el torneo
    Given torneo con disciplinas STA y DNF
    When POST /registro/inscripciones con disciplinas DYN
    Then 409 Conflict con detalle DisciplinaNoDisponible

  Scenario: atleta ya inscripto en el mismo torneo
    Given atleta ya inscripto en el torneo
    When POST /registro/inscripciones con mismo atleta_id y torneo_id
    Then 409 Conflict con detalle AtletaYaInscripto

  Scenario: cancelar inscripcion antes del torneo
    Given inscripcion ACTIVA y fecha inicio del torneo es maniana
    When DELETE /registro/inscripciones/{inscripcion_id}
    Then 200 y la inscripcion queda en estado CANCELADA

  Scenario: cancelar inscripcion el dia del torneo
    Given inscripcion ACTIVA y fecha inicio del torneo es hoy
    When DELETE /registro/inscripciones/{inscripcion_id}
    Then 409 Conflict con detalle PlazoCancelacionVencido

  Scenario: listar inscriptos de un torneo
    Given 3 atletas inscriptos en un torneo
    When GET /registro/torneos/{torneo_id}/inscriptos
    Then 200 con lista de 3 inscripciones ACTIVAS
