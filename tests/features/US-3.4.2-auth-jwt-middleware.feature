Feature: US-3.4.2 — Auth por rol: middleware JWT en APIs

  Scenario: organizador crea torneo con token válido
    Given un token JWT con rol ORGANIZADOR
    When POST /torneos con el token
    Then la respuesta es 201

  Scenario: atleta intenta crear torneo y recibe 403
    Given un token JWT con rol ATLETA
    When POST /torneos con el token
    Then la respuesta es 403

  Scenario: request sin token a endpoint protegido recibe 401
    Given no hay token de autenticación
    When POST /torneos sin token
    Then la respuesta es 401

  Scenario: juez registra tarjeta con su token
    Given un token JWT con rol JUEZ
    When POST /competencias/{id}/performances/{perf_id}/tarjeta con el token
    Then la respuesta es 200

  Scenario: atleta registra AP con su token
    Given un token JWT con rol ATLETA
    When POST /competencias/{id}/performances/{atleta_id}/ap con el token
    Then la respuesta es 201

  Scenario: GET /torneos sin token es público
    Given no hay token de autenticación
    When GET /torneos sin token
    Then la respuesta es 200
