Feature: US-3.4.1 — Torneo: AsignarDisciplinas + AsignarJuez

  Background:
    Given un torneo creado en estado CREADO

  Scenario: asignar disciplinas a torneo
    When el organizador asigna las disciplinas [STA, DNF, DBF] al torneo
    Then el torneo tiene 3 disciplinas configuradas sin juez asignado

  Scenario: asignar juez a disciplina del torneo
    Given el torneo tiene disciplinas [STA, DNF] configuradas
    When el organizador asigna el juez "juez-001" a la disciplina STA
    Then la disciplina STA tiene el juez "juez-001" asignado

  Scenario: reasignar juez a disciplina ya asignada
    Given el torneo tiene disciplinas [STA] con juez "juez-001" en STA
    When el organizador asigna el juez "juez-002" a la disciplina STA
    Then la disciplina STA tiene el juez "juez-002" asignado

  Scenario: asignar juez a disciplina no configurada en el torneo
    Given el torneo tiene disciplinas [STA]
    When el organizador asigna el juez "juez-001" a la disciplina DYN
    Then se lanza DisciplinaNoEnTorneo

  Scenario: listar disciplinas asignadas a un juez
    Given el torneo tiene 3 disciplinas y juez asignado a 2 de ellas
    When se consultan las disciplinas del juez registrado
    Then se retornan exactamente 2 disciplinas

  Scenario: asignar disciplinas con torneo en estado EJECUCION
    Given un torneo en estado EJECUCION
    When el organizador intenta asignar disciplinas [STA, DNF]
    Then se lanza AsignacionNoPermitida
