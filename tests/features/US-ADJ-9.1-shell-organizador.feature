Feature: US-ADJ-9.1 - Shell del organizador

  Background:
    Given existe un usuario autenticado con rol ORGANIZADOR

  Scenario: El shell muestra navbar persistente del organizador
    When el organizador abre una seccion principal
    Then ve la marca AtaraxiaDive
    And ve tabs para Panel, Grilla, Resultados, Jueces, Torneo y Audit Log

  Scenario: El tab activo refleja la seccion visible
    Given el organizador esta en la seccion Resultados
    Then el tab Resultados aparece activo
    And los demas tabs no aparecen activos

  Scenario: La navbar permanece visible al hacer scroll
    Given el organizador esta en una pantalla con scroll
    When hace scroll vertical
    Then la navbar sigue visible en la parte superior

  Scenario: El shell muestra conexión y usuario
    Given el organizador esta autenticado
    Then ve un badge de estado de conexion
    And ve el nombre o email del usuario

  Scenario: El shell usa tema dark aprobado
    When el organizador abre cualquier seccion principal
    Then el fondo general usa el tema dark aprobado
    And no se muestra el layout claro o beige anterior
