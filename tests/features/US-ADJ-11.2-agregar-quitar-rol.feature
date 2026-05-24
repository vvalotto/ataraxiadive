Feature: Gestión de roles de usuario post-registro

  Background:
    Given el sistema de identidad está inicializado

  Scenario: Usuario ATLETA agrega el rol JUEZ
    Given existe un usuario autenticado con email "atleta@email.com" password "Apnea12345" y roles "ATLETA"
    When hace POST /auth/usuarios/me/roles con rol "JUEZ"
    Then la respuesta es 200
    And la respuesta incluye los roles "ATLETA,JUEZ"

  Scenario: Usuario intenta agregar un rol que ya posee
    Given existe un usuario autenticado con email "multi@email.com" password "Apnea12345" y roles "ATLETA,JUEZ"
    When hace POST /auth/usuarios/me/roles con rol "JUEZ"
    Then la respuesta es 409

  Scenario: Usuario intenta agregar el rol ADMIN
    Given existe un usuario autenticado con email "atleta2@email.com" password "Apnea12345" y roles "ATLETA"
    When hace POST /auth/usuarios/me/roles con rol "ADMIN"
    Then la respuesta es 403

  Scenario: Usuario JUEZ+ATLETA quita el rol JUEZ
    Given existe un usuario autenticado con email "juez@email.com" password "Apnea12345" y roles "JUEZ,ATLETA"
    When hace DELETE /auth/usuarios/me/roles/JUEZ
    Then la respuesta es 200
    And la respuesta incluye los roles "ATLETA"

  Scenario: Usuario intenta quitar el rol ATLETA
    Given existe un usuario autenticado con email "atleta3@email.com" password "Apnea12345" y roles "ATLETA,JUEZ"
    When hace DELETE /auth/usuarios/me/roles/ATLETA
    Then la respuesta es 409

  Scenario: Usuario intenta quitar un rol que no posee
    Given existe un usuario autenticado con email "atleta4@email.com" password "Apnea12345" y roles "ATLETA"
    When hace DELETE /auth/usuarios/me/roles/JUEZ
    Then la respuesta es 404

  Scenario: Usuario intenta quitar su único rol JUEZ
    Given existe un usuario autenticado con email "solojuez@email.com" password "Apnea12345" y roles "JUEZ"
    When hace DELETE /auth/usuarios/me/roles/JUEZ
    Then la respuesta es 409
