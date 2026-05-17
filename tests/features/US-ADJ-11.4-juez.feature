Feature: US-ADJ-11.4 — BC Registro: entidad Juez
  Como usuario con rol JUEZ
  Quiero poder crear y actualizar mi perfil de juez
  Para que el organizador tenga mis datos de licencia disponibles

  Background:
    Given el repositorio de jueces está inicializado

  Scenario: Crear perfil Juez con datos mínimos
    Given no existe perfil Juez para "juez@test.com"
    When hace POST /registro/jueces con body vacío como "juez@test.com"
    Then la respuesta es 201
    And la respuesta contiene un juez_id generado por el backend
    And el juez "juez@test.com" tiene numero_licencia null y federacion null

  Scenario: Crear perfil Juez con datos completos
    Given no existe perfil Juez para "completo@test.com"
    When hace POST /registro/jueces con numero_licencia "ARG-001" y federacion "AIDA" como "completo@test.com"
    Then la respuesta es 201
    And el juez "completo@test.com" tiene numero_licencia "ARG-001" y federacion "AIDA"

  Scenario: Intentar crear perfil Juez duplicado devuelve 409
    Given existe un perfil Juez para "juez@test.com" sin licencia
    When hace POST /registro/jueces con body vacío como "juez@test.com"
    Then la respuesta es 409

  Scenario: Obtener perfil Juez propio
    Given existe un perfil Juez para "juez@test.com" sin licencia
    When hace GET /registro/jueces/me como "juez@test.com"
    Then la respuesta es 200
    And el cuerpo contiene el email "juez@test.com"

  Scenario: Obtener perfil Juez inexistente devuelve 404
    Given no existe perfil Juez para "nuevo@test.com"
    When hace GET /registro/jueces/me como "nuevo@test.com"
    Then la respuesta es 404

  Scenario: Actualizar numero de licencia
    Given existe un perfil Juez para "juez@test.com" sin licencia
    When hace PATCH /registro/jueces/me con numero_licencia "ARG-042" como "juez@test.com"
    Then la respuesta es 200
    And el juez "juez@test.com" tiene numero_licencia "ARG-042" y federacion null

  Scenario: Usuario con rol ATLETA no puede crear perfil Juez
    When hace POST /registro/jueces como ATLETA con email "atleta@test.com"
    Then la respuesta es 403
