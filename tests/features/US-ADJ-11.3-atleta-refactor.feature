Feature: US-ADJ-11.3 — BC Registro: Atleta con campos opcionales y BT-002 (dni, telefono)
  Como atleta que se registra en la plataforma
  Quiero poder crear mi perfil sin club ni categoria obligatorios
  Y poder guardar mi DNI y teléfono
  Para completar los datos cuando los tenga disponibles

  Background:
    Given el repositorio de atletas está inicializado

  Scenario: Registrar atleta sin club ni categoria
    Given no existe ningún atleta con email "laura@test.com"
    When se registra un atleta con email "laura@test.com" nombre "Laura" apellido "Pérez" fecha_nacimiento "2000-01-01" sin club ni categoria
    Then la respuesta es 201
    And la respuesta contiene un atleta_id generado por el backend
    And el atleta "laura@test.com" tiene club null y categoria null

  Scenario: Registrar atleta con todos los campos incluyendo dni y telefono
    Given no existe ningún atleta con email "completo@test.com"
    When se registra un atleta con email "completo@test.com" nombre "Carlos" apellido "López" fecha_nacimiento "1990-06-15" club "Club Apnea BA" categoria "SENIOR_MASCULINO" dni "30123456" telefono "1155559999"
    Then la respuesta es 201
    And el atleta "completo@test.com" tiene dni "30123456" y telefono "1155559999"

  Scenario: Actualizar atleta agregando dni y telefono
    Given existe un atleta con email "existente@test.com" sin dni ni telefono
    When actualiza su perfil con dni "28888999" y telefono "1133334444"
    Then la respuesta es 200
    And el atleta "existente@test.com" tiene dni "28888999" y telefono "1133334444"

  Scenario: Registrar atleta con email ya existente devuelve 409
    Given existe un atleta con email "doble@test.com" sin dni ni telefono
    When se registra un atleta con email "doble@test.com" nombre "Otro" apellido "Atleta" fecha_nacimiento "1995-01-01" sin club ni categoria
    Then la respuesta es 409

  Scenario: Registrar atleta con club vacío devuelve 422
    When se registra un atleta con email "invalido@test.com" nombre "Ana" apellido "García" fecha_nacimiento "1998-03-20" club ""
    Then la respuesta es 422
