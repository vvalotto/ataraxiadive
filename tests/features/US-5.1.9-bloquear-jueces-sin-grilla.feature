Feature: US-5.1.9 - Precondicion de grilla en asignacion de jueces

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo T1 esta en estado PREPARACION con disciplinas DNF y STA

  Scenario: disciplina con grilla generada tiene selector habilitado
    Given existe competencia C1 para disciplina DNF en estado GrillaGenerada
    When el organizador accede al tab Jueces
    Then la fila de DNF muestra el JuezSelector habilitado

  Scenario: disciplina sin competencia tiene selector bloqueado
    Given no existe competencia para disciplina STA en T1
    When el organizador accede al tab Jueces
    Then la fila de STA muestra el selector deshabilitado
    And la fila muestra el mensaje "Generar grilla antes de asignar juez"

  Scenario: asignacion existente visible aunque grilla no este generada
    Given existe una asignacion de juez para STA en torneo.db
    And no existe competencia para STA en competencia.db
    When el organizador accede al tab Jueces
    Then la fila de STA muestra el juez asignado como texto
    And el selector de STA permanece deshabilitado

  Scenario: asignar juez a disciplina con grilla funciona normalmente
    Given existe competencia C1 para DNF en estado GrillaConfirmada
    And no hay juez asignado a DNF
    When el organizador selecciona un juez en la fila de DNF
    Then el backend recibe PUT /torneos/T1/disciplinas/DNF/juez
    And la fila actualiza con el juez asignado
