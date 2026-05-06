Feature: US-6.2.5 - Grupos etarios al crear torneo

  Background:
    Given la base de datos de torneos está limpia para grupos etarios

  Scenario: crear torneo persiste grupos etarios seleccionados
    Given un payload de torneo con grupos etarios JUNIOR y MASTER
    When POST /torneos con el payload de grupos etarios
    Then la respuesta de creacion es 201 con torneo_id
    And GET /torneos/{torneo_id} retorna grupos_etarios JUNIOR y MASTER

  Scenario: payload sin grupos_etarios es rechazado
    Given un payload de torneo sin grupos_etarios
    When POST /torneos con el payload de grupos etarios
    Then la respuesta de grupos etarios es 422

  Scenario: payload con grupos_etarios vacio es rechazado
    Given un payload de torneo con grupos_etarios vacio
    When POST /torneos con el payload de grupos etarios
    Then la respuesta de grupos etarios es 422

  Scenario: payload con grupo etario invalido es rechazado
    Given un payload de torneo con grupo etario INVALIDO
    When POST /torneos con el payload de grupos etarios
    Then la respuesta de grupos etarios es 422
