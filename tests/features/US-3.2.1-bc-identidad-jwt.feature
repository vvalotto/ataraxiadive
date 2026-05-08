Feature: US-3.2.1 — BC Identidad JWT
  Como usuario del sistema
  Quiero registrarme y autenticarme para obtener un JWT
  Para que los demás endpoints puedan verificar mi identidad y rol

  Background:
    Given el sistema de identidad está inicializado

  Scenario: registrar usuario nuevo con rol ORGANIZADOR
    Given un email "organizador@test.com" no registrado
    When POST /auth/registro con email "organizador@test.com", password "Clave1234A", rol "ORGANIZADOR"
    Then la respuesta es 201
    And la respuesta contiene un campo "usuario_id"

  Scenario: registrar usuario con email duplicado retorna 409
    Given un usuario registrado con email "existente@test.com"
    When POST /auth/registro con email "existente@test.com", password "Otralave1A", rol "ATLETA"
    Then la respuesta es 409

  Scenario: registrar usuario con password menor a 8 caracteres retorna 422
    Given un email "nuevo@test.com" no registrado
    When POST /auth/registro con email "nuevo@test.com", password "corto", rol "JUEZ"
    Then la respuesta es 422

  Scenario: login exitoso retorna JWT con payload correcto
    Given un usuario registrado con email "juez@test.com" y password "Secreto99A" y rol "JUEZ"
    When POST /auth/login con email "juez@test.com" y password "Secreto99A"
    Then la respuesta es 200
    And la respuesta contiene un campo "access_token"
    And el token contiene email "juez@test.com" y rol "JUEZ"

  Scenario: login con password incorrecto retorna 401
    Given un usuario registrado con email "juez@test.com" y password "Secreto99A" y rol "JUEZ"
    When POST /auth/login con email "juez@test.com" y password "wrongpass"
    Then la respuesta es 401

  Scenario: login con email no registrado retorna 401
    Given un email "inexistente@test.com" no registrado
    When POST /auth/login con email "inexistente@test.com" y password "cualquier1"
    Then la respuesta es 401

  Scenario: JWT válido es verificable por get_current_user
    Given un usuario registrado con email "org@test.com" y password "Organiz01A" y rol "ORGANIZADOR"
    And un access_token obtenido con esas credenciales
    When se verifica el token con get_current_user
    Then el payload contiene "sub", "email" y "rol"
    And el campo "email" es "org@test.com"
    And el campo "rol" es "ORGANIZADOR"
