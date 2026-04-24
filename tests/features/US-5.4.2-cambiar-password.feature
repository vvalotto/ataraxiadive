Feature: US-5.4.2 - Cambiar contrasena

  Background:
    Given el usuario "juez1@email.com" esta autenticado con password actual "apnea123"

  Scenario: cambiar password exitosamente
    When el usuario ingresa password actual "apnea123" y nueva password "nuevapass456"
    And confirma el cambio
    Then el sistema responde 204
    And el usuario puede autenticarse con "nuevapass456" en adelante

  Scenario: password actual incorrecta es rechazada
    When el usuario ingresa password actual "wrongpass" y nueva password "nuevapass456"
    And confirma el cambio
    Then el sistema responde 401
    And se muestra "La contrasena actual es incorrecta"

  Scenario: nueva password menor a 8 caracteres es rechazada antes de enviar
    When el usuario ingresa nueva password "abc"
    And intenta confirmar el cambio
    Then el formulario muestra "La contrasena debe tener al menos 8 caracteres"
    And no se envia POST "/auth/cambiar-password"

  Scenario: confirmacion de nueva password no coincide es rechazada en frontend
    When el usuario ingresa nueva password "nuevapass456" y confirmacion "otrapass789"
    And intenta confirmar el cambio
    Then el formulario muestra "Las contrasenas no coinciden"
    And no se envia POST "/auth/cambiar-password"
