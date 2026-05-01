Feature: US-5.3.2 - Vista del atleta

  Background:
    Given el sistema tiene los torneos:
      | nombre                 | estado               |
      | Buenos Aires Open 2026 | INSCRIPCION_ABIERTA  |
      | Campeonato Patagonia   | INSCRIPCION_ABIERTA  |
      | Torneo BA 2025         | CERRADO              |

  Scenario: atleta autenticado es redirigido a su dashboard
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When navega a "/"
    Then es redirigido a "/atleta/dashboard"

  Scenario: dashboard muestra perfil del atleta
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When accede a "/atleta/dashboard"
    Then ve su email "atleta1@email.com"
    And ve su rol como "Atleta"

  Scenario: dashboard muestra solo torneos en inscripcion abierta
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When accede a "/atleta/dashboard"
    Then ve "Buenos Aires Open 2026" en la lista de torneos disponibles
    And ve "Campeonato Patagonia" en la lista de torneos disponibles
    And no ve "Torneo BA 2025" en la lista

  Scenario: sin torneos disponibles muestra mensaje informativo
    Given no existen torneos en estado INSCRIPCION_ABIERTA
    And "atleta1@email.com" esta autenticado con rol ATLETA
    When accede a "/atleta/dashboard"
    Then ve el mensaje "No hay torneos disponibles en este momento"

  Scenario: atleta no puede acceder a rutas del organizador
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When intenta navegar a "/organizador/dashboard"
    Then es redirigido a "/atleta/dashboard"

  Scenario: atleta no puede acceder a rutas del juez
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When intenta navegar a "/juez/disciplinas"
    Then es redirigido a "/atleta/dashboard"
