Feature: US-3.2.2 — BC Registro: Aggregate Atleta

  Scenario: registrar atleta con datos válidos
    Given datos personales completos con nombre "Ana", apellido "García", email "ana@example.com", fecha_nacimiento "1990-05-15", categoria "SENIOR_FEMENINO"
    When POST /registro/atletas con un atleta_id válido
    Then la respuesta es 201 con el atleta_id
    And GET /registro/atletas con ese id retorna los datos del atleta

  Scenario: registrar atleta sin brevet
    Given datos válidos sin campo brevet
    When POST /registro/atletas
    Then la respuesta es 201 y brevet es nulo en la respuesta

  Scenario: atleta duplicado mismo ID
    Given un atleta ya registrado con atleta_id X
    When POST /registro/atletas con el mismo atleta_id X
    Then la respuesta es 409 Conflict

  Scenario: nombre vacío
    Given nombre vacío en los datos del atleta
    When POST /registro/atletas
    Then la respuesta es 422 Unprocessable Entity

  Scenario: atleta no encontrado
    Given un UUID no registrado en el sistema
    When GET /registro/atletas con ese UUID
    Then la respuesta es 404 Not Found
