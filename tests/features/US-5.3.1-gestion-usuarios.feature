Feature: US-5.3.1 - UI de gestion de usuarios

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And en el sistema existen los usuarios:
      | email           | rol  | activo |
      | juez1@email.com | JUEZ | true   |

  Scenario: listar todos los usuarios del sistema
    When el organizador navega a la pagina de gestion de usuarios
    Then ve una lista con "juez1@email.com" con rol "JUEZ"
    And ve el estado "Activo" para "juez1@email.com"

  Scenario: crear usuario juez exitosamente
    When el organizador completa el formulario de usuario con email "juez2@email.com", password "pass1234" y rol "JUEZ"
    And confirma la creacion del usuario
    Then el sistema responde 201
    And "juez2@email.com" aparece en la lista con rol "JUEZ"
    And el formulario de usuario queda limpio para una nueva entrada

  Scenario: crear usuario con email duplicado muestra error inline
    When el organizador intenta crear un usuario con email "juez1@email.com", password "pass1234" y rol "ATLETA"
    And confirma la creacion del usuario
    Then el sistema responde 409
    And se muestra "Este email ya esta registrado" en el formulario de usuario
    And el formulario de usuario permanece abierto con los datos ingresados

  Scenario: password de menos de 8 caracteres es rechazada antes de enviar
    When el organizador ingresa password "abc" en el formulario de usuario
    And intenta confirmar la creacion del usuario
    Then el formulario de usuario muestra "La contrasena debe tener al menos 8 caracteres"
    And no se envia POST a "/auth/registro"

  Scenario: rol ADMIN no esta disponible en el selector
    When el organizador abre el formulario de creacion de usuario
    Then el selector de rol muestra solo "JUEZ", "ATLETA" y "ORGANIZADOR"
    And no muestra "ADMIN"
