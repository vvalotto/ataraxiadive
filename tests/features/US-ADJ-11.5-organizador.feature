Feature: US-ADJ-11.5 — BC Registro: entidad Organizador
  Como usuario con rol ORGANIZADOR
  Quiero poder crear y actualizar mi perfil de organizador
  Para que los atletas sepan quién organiza los torneos que publico

  Background:
    Given el repositorio de organizadores está inicializado

  Scenario: Crear perfil Organizador con datos mínimos
    Given no existe perfil Organizador para "org@test.com"
    When hace POST /registro/organizadores con body vacío como "org@test.com"
    Then la respuesta es 201
    And la respuesta contiene un organizador_id generado por el backend
    And el organizador "org@test.com" tiene nombre_organizacion null

  Scenario: Crear perfil Organizador con nombre de organización
    Given no existe perfil Organizador para "org2@test.com"
    When hace POST /registro/organizadores con nombre_organizacion "Club Apnea Buenos Aires" como "org2@test.com"
    Then la respuesta es 201
    And el organizador "org2@test.com" tiene nombre_organizacion "Club Apnea Buenos Aires"

  Scenario: Intentar crear perfil Organizador duplicado devuelve 409
    Given existe un perfil Organizador para "org@test.com" sin nombre
    When hace POST /registro/organizadores con body vacío como "org@test.com"
    Then la respuesta es 409
    And el detalle contiene "Perfil de organizador ya registrado"

  Scenario: Obtener perfil Organizador propio
    Given existe un perfil Organizador para "org@test.com" sin nombre
    When hace GET /registro/organizadores/me como "org@test.com"
    Then la respuesta es 200
    And el cuerpo contiene el email "org@test.com"

  Scenario: Obtener perfil Organizador inexistente devuelve 404
    Given no existe perfil Organizador para "nuevo@test.com"
    When hace GET /registro/organizadores/me como "nuevo@test.com"
    Then la respuesta es 404
    And el detalle contiene "Organizador no encontrado"

  Scenario: Actualizar nombre de organización
    Given existe un perfil Organizador para "org@test.com" sin nombre
    When hace PATCH /registro/organizadores/me con nombre_organizacion "Federación Apnea Sur" como "org@test.com"
    Then la respuesta es 200
    And el organizador "org@test.com" tiene nombre_organizacion "Federación Apnea Sur"

  Scenario: Limpiar nombre de organización a null
    Given existe un perfil Organizador para "org@test.com" con nombre "Club Viejo"
    When hace PATCH /registro/organizadores/me con nombre_organizacion null como "org@test.com"
    Then la respuesta es 200
    And el organizador "org@test.com" tiene nombre_organizacion null

  Scenario: Usuario con rol ATLETA no puede crear perfil Organizador
    When hace POST /registro/organizadores como ATLETA con email "atleta@test.com"
    Then la respuesta es 403
