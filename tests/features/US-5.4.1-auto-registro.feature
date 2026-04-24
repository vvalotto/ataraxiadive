Feature: US-5.4.1 - Auto-registro de usuario

  Scenario: auto-registro exitoso como atleta
    Given no existe ninguna cuenta con email "ana@email.com"
    When "ana@email.com" completa el formulario con nombre "Ana", apellido "Garcia", password "apnea123" y rol "ATLETA"
    And confirma el registro
    Then el sistema responde 201
    And el usuario queda guardado con nombre "Ana", apellido "Garcia" y rol "ATLETA"
    And el usuario es redirigido a "/login"

  Scenario: nombre vacio es rechazado antes de enviar
    Given el formulario de registro esta abierto
    When el usuario deja el campo "nombre" vacio
    And intenta confirmar el registro
    Then el formulario muestra "El nombre es requerido"
    And no se envia POST "/auth/registro"

  Scenario: apellido vacio es rechazado antes de enviar
    Given el formulario de registro esta abierto
    When el usuario deja el campo "apellido" vacio
    And intenta confirmar el registro
    Then el formulario muestra "El apellido es requerido"
    And no se envia POST "/auth/registro"

  Scenario: email duplicado muestra error inline
    Given ya existe un usuario con email "juez1@email.com"
    When alguien intenta registrarse con email "juez1@email.com"
    Then el sistema responde 409
    And se muestra "Este email ya esta registrado" en el formulario

  Scenario: rol ADMIN es rechazado por el backend
    Given el cliente envia POST "/auth/registro" con rol "ADMIN"
    Then el sistema responde 403
    And el mensaje es "El rol ADMIN no esta permitido en el auto-registro"

  Scenario: rol ADMIN no aparece en el selector del formulario
    Given el formulario de registro esta abierto
    Then el selector de rol muestra solo "JUEZ", "ATLETA" y "ORGANIZADOR"
    And no muestra "ADMIN"

  Scenario: link de registro visible en la pagina de login
    Given el usuario no autenticado navega a "/login"
    Then ve el link "No tenes cuenta? Registrate" que apunta a "/registro"
