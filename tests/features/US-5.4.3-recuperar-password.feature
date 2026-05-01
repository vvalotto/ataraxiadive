Feature: US-5.4.3 - Olvide contrasena

  Scenario: solicitar reset con email existente siempre responde 200
    Given el usuario "ana@email.com" esta registrado en el sistema
    When se envia POST "/auth/solicitar-reset" con email "ana@email.com"
    Then el sistema responde 200
    And el mensaje es "Si el email esta registrado, recibiras un enlace en breve."
    And se envia un email a "ana@email.com" con un link de reset

  Scenario: solicitar reset con email inexistente tambien responde 200
    Given no existe ningun usuario con email "noexiste@email.com"
    When se envia POST "/auth/solicitar-reset" con email "noexiste@email.com"
    Then el sistema responde 200
    And el mensaje es "Si el email esta registrado, recibiras un enlace en breve."
    And no se envia ningun email

  Scenario: reset exitoso con token valido
    Given "ana@email.com" tiene un token de reset valido "eyJ..."
    When se envia POST "/auth/reset-password" con el token y password_nueva "nueva_apnea99"
    Then el sistema responde 204
    And "ana@email.com" puede autenticarse con "nueva_apnea99"

  Scenario: token expirado es rechazado
    Given "ana@email.com" tiene un token de reset expirado
    When se envia POST "/auth/reset-password" con ese token y password_nueva "nueva_apnea99"
    Then el sistema responde 400
    And el mensaje es "El enlace es invalido o ha expirado"

  Scenario: token de sesion no es aceptado como token de reset
    Given "ana@email.com" tiene un token de sesion valido
    When se envia POST "/auth/reset-password" con ese token de sesion
    Then el sistema responde 400
    And el mensaje es "El enlace es invalido o ha expirado"

  Scenario: link de recuperacion visible en login
    Given el usuario no autenticado navega a "/login"
    Then ve el link "Olvidaste tu contrasena?" que apunta a "/recuperar-password"
