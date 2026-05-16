Feature: Creación automática de perfiles en BC Registro al registrarse
  As a user registering in AtaraxiaDive
  I want my BC Registro profile to be created automatically when I register
  So that I can access "Mis Datos" without additional steps

  Background:
    Given the registro database is empty

  Scenario: Registro solo ATLETA crea perfil stub de atleta
    When a user registers with roles=["ATLETA"], nombre="Ana", apellido="Lopez", email="ana@test.com"
    Then an Atleta exists in BC Registro with email="ana@test.com"
    And the Atleta has nombre="Ana" and apellido="Lopez"
    And the Atleta has fecha_nacimiento=null

  Scenario: Registro con ATLETA + JUEZ crea ambos perfiles
    When a user registers with roles=["ATLETA", "JUEZ"], email="multi@test.com"
    Then an Atleta exists in BC Registro with email="multi@test.com"
    And a Juez exists in BC Registro with email="multi@test.com"

  Scenario: Registro con ORGANIZADOR crea perfil de organizador
    When a user registers with roles=["ORGANIZADOR"], email="org@test.com"
    Then an Organizador exists in BC Registro with email="org@test.com"

  Scenario: Registro con los tres roles crea los tres perfiles
    When a user registers with roles=["ATLETA", "JUEZ", "ORGANIZADOR"], email="all@test.com"
    Then an Atleta exists in BC Registro with email="all@test.com"
    And a Juez exists in BC Registro with email="all@test.com"
    And an Organizador exists in BC Registro with email="all@test.com"

  Scenario: Atleta creado sin fecha_nacimiento es válido en el dominio
    Given an Atleta aggregate with nombre="Carlos", apellido="Test", email="c@test.com" and no fecha_nacimiento
    Then the Atleta aggregate is valid without raising an error

  Scenario: Atleta puede completar fecha_nacimiento en Mis Datos
    Given an Atleta exists with no fecha_nacimiento
    When the Atleta updates with fecha_nacimiento=1990-05-15
    Then the Atleta has fecha_nacimiento=1990-05-15

  Scenario: Creación idempotente — perfil ya existente no genera error
    Given an Atleta already exists with email="existing@test.com"
    When a user registers again with roles=["ATLETA"], email="existing@test.com"
    Then no error is raised
    And only one Atleta exists with email="existing@test.com"
