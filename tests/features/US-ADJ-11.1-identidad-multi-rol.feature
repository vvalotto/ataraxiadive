Feature: US-ADJ-11.1 — BC Identidad multi-rol: registro y login
  Como persona que participa en el mundo del apnea en múltiples roles
  Quiero poder registrarme con más de un rol en una única cuenta
  Para no necesitar dos emails distintos cuando soy juez y también compito

  Background:
    Given el sistema de identidad está inicializado

  Scenario: Registro con un único rol devuelve token directo
    Given no existe ningún usuario con email "maria@test.com"
    When se registra con email "maria@test.com" password "Apnea2024!" y roles "ATLETA"
    Then la respuesta es 201
    And la respuesta contiene campo "access_token"
    And el token del registro contiene rol "ATLETA"

  Scenario: Registro con múltiples roles devuelve requires_role_selection
    Given no existe ningún usuario con email "carlos@test.com"
    When se registra con email "carlos@test.com" password "Apnea2024!" y roles "JUEZ,ATLETA"
    Then la respuesta es 201
    And la respuesta contiene campo "requires_role_selection"
    And la respuesta no contiene campo "access_token"

  Scenario: Login con usuario de un único rol devuelve token
    Given existe un usuario con email "ana@test.com" password "Apnea2024!" y roles "ORGANIZADOR"
    When hace login con email "ana@test.com" password "Apnea2024!" sin rol_elegido
    Then la respuesta es 200
    And la respuesta contiene campo "access_token"
    And el token del login contiene rol "ORGANIZADOR"

  Scenario: Login con múltiples roles sin rol_elegido devuelve requires_role_selection
    Given existe un usuario con email "pedro@test.com" password "Apnea2024!" y roles "JUEZ,ATLETA"
    When hace login con email "pedro@test.com" password "Apnea2024!" sin rol_elegido
    Then la respuesta es 200
    And la respuesta contiene campo "requires_role_selection"
    And la respuesta no contiene campo "access_token"

  Scenario: Login con múltiples roles especificando rol_elegido devuelve token
    Given existe un usuario con email "pedro@test.com" password "Apnea2024!" y roles "JUEZ,ATLETA"
    When hace login con email "pedro@test.com" password "Apnea2024!" y rol_elegido "ATLETA"
    Then la respuesta es 200
    And el token del login contiene rol "ATLETA"

  Scenario: Login con rol_elegido que el usuario no posee retorna 401
    Given existe un usuario con email "solo@test.com" password "Apnea2024!" y roles "ATLETA"
    When hace login con email "solo@test.com" password "Apnea2024!" y rol_elegido "JUEZ"
    Then la respuesta es 401

  Scenario: Registro con email existente agrega roles nuevos y requiere selección
    Given existe un usuario con email "lucia@test.com" password "Apnea2024!" y roles "ATLETA"
    When se registra con email "lucia@test.com" password "Apnea2024!" y roles "JUEZ"
    Then la respuesta es 200
    And la respuesta contiene campo "requires_role_selection"

  Scenario: Registro con email existente y contraseña incorrecta retorna 401
    Given existe un usuario con email "lucia@test.com" password "Apnea2024!" y roles "ATLETA"
    When se registra con email "lucia@test.com" password "WrongPass1!" y roles "JUEZ"
    Then la respuesta es 401

  Scenario: Registro con email existente y rol ya asignado retorna 409
    Given existe un usuario con email "lucia@test.com" password "Apnea2024!" y roles "ATLETA"
    When se registra con email "lucia@test.com" password "Apnea2024!" y roles "ATLETA"
    Then la respuesta es 409
