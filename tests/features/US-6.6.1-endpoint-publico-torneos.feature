Feature: US-6.6.1 - Endpoint publico GET /api/torneos

  Background:
    Given la base de datos de torneos publicos esta limpia

  Scenario: Visitante lista torneos sin token
    Given existe un torneo publico con estado CREADO
    When un visitante hace GET /torneos sin Authorization header
    Then la respuesta publica de torneos es 200 OK
    And el body es una lista de torneos

  Scenario: Torneos cancelados no aparecen en la lista publica
    Given existe un torneo publico con estado CREADO
    And existe un torneo publico con estado CANCELADO
    When un visitante hace GET /torneos sin Authorization header
    Then la respuesta publica de torneos es 200 OK
    And la lista publica no contiene torneos con estado CANCELADO

  Scenario: Respuesta incluye los campos del portal
    Given existen torneos publicos con estados CREADO, INSCRIPCION_ABIERTA y EJECUCION
    When un visitante hace GET /torneos sin Authorization header
    Then cada torneo publico incluye torneo_id, nombre, descripcion, fecha_inicio, fecha_fin, sede y estado

  Scenario: Endpoint con auth mantiene el mismo contrato
    Given existen torneos publicos con estados CREADO e INSCRIPCION_ABIERTA
    When un visitante hace GET /torneos sin Authorization header
    And un organizador autenticado hace GET /torneos
    Then ambas respuestas publicas tienen status 200
    And ambas respuestas publicas tienen el mismo contrato de torneo
