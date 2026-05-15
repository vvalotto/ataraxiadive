Feature: US-ADJ-10.3 - Email de bienvenida y auto-login post-registro

  Background:
    Given el servicio de identidad esta inicializado con DB temporal

  Scenario: Email de bienvenida se invoca al registrar un usuario nuevo
    Given el email port esta disponible y captura llamadas
    When se registra un nuevo usuario con email "nuevo@ejemplo.com" y rol "ATLETA"
    Then el registro responde 201
    And el email port recibio exactamente 1 llamada a enviar
    And el destinatario del email es "nuevo@ejemplo.com"

  Scenario: El registro no falla si el servicio de email no esta disponible
    Given el email port esta configurado para lanzar excepcion
    When se registra un nuevo usuario con email "fallo@ejemplo.com" y rol "ATLETA"
    Then el registro responde 201
    And el usuario queda registrado correctamente con email "fallo@ejemplo.com"

  Scenario: El usuario puede autenticarse con las mismas credenciales tras el registro
    Given el email port esta disponible y captura llamadas
    When se registra un nuevo usuario con email "autologin@ejemplo.com" y rol "ATLETA"
    And se intenta login con email "autologin@ejemplo.com" y password "Apnea12345"
    Then el login responde 200
    And la respuesta contiene un access_token valido

  Scenario: El auto-login post-registro como organizador devuelve token con rol correcto
    Given el email port esta disponible y captura llamadas
    When se registra un nuevo usuario con email "org@ejemplo.com" y rol "ORGANIZADOR"
    And se intenta login con email "org@ejemplo.com" y password "Apnea12345"
    Then el login responde 200
    And el token contiene rol "organizador"

  Scenario: El auto-login post-registro como atleta devuelve token con rol correcto
    Given el email port esta disponible y captura llamadas
    When se registra un nuevo usuario con email "atleta@ejemplo.com" y rol "ATLETA"
    And se intenta login con email "atleta@ejemplo.com" y password "Apnea12345"
    Then el login responde 200
    And el token contiene rol "atleta"
