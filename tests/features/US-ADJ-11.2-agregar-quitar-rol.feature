Feature: Gestión de roles de usuario post-registro

  Background:
    Given el sistema de identidad está inicializado

  Scenario: Usuario ATLETA agrega el rol JUEZ
    Given existe un usuario autenticado con email "atleta@email.com" password "Apnea12345" y roles "ATLETA"
    When hace POST /auth/me/roles con rol "JUEZ"
    Then la respuesta es 200
    And la respuesta incluye los roles "ATLETA,JUEZ"

  Scenario: Usuario intenta agregar un rol que ya posee
    Given existe un usuario autenticado con email "multi@email.com" password "Apnea12345" y roles "ATLETA,JUEZ"
    When hace POST /auth/me/roles con rol "JUEZ"
    Then la respuesta es 409

  Scenario: Usuario JUEZ+ATLETA quita el rol JUEZ
    Given existe un usuario autenticado con email "juez@email.com" password "Apnea12345" y roles "JUEZ,ATLETA"
    When hace DELETE /auth/me/roles/JUEZ
    Then la respuesta es 200
    And la respuesta incluye los roles "ATLETA"

  Scenario: Usuario intenta quitar un rol que no posee
    Given existe un usuario autenticado con email "atleta4@email.com" password "Apnea12345" y roles "ATLETA"
    When hace DELETE /auth/me/roles/JUEZ
    Then la respuesta es 409

  Scenario: Usuario intenta quitar su único rol JUEZ
    Given existe un usuario autenticado con email "solojuez@email.com" password "Apnea12345" y roles "JUEZ"
    When hace DELETE /auth/me/roles/JUEZ
    Then la respuesta es 422
