Feature: US-4.4.3 - Sincronizacion automatica al reconectar

  Background:
    Given existen comandos pendientes en la cola local
    And el badge de sincronizacion muestra pendientes

  Scenario: reconexion sincroniza cola en orden FIFO
    Given el dispositivo estaba offline y vuelve online
    When se ejecuta la sincronizacion
    Then los comandos se envian en orden FIFO
    And la cola queda vacia
    And el badge muestra estado sincronizado

  Scenario: error 4xx marca comando en error y pausa
    Given un comando de la cola responde 409
    When corre la sincronizacion
    Then el comando queda en estado error con mensaje
    And el badge muestra estado de error
    And no se procesan comandos posteriores

  Scenario: error transitorio reintenta con backoff
    Given un comando falla por red o 5xx en los primeros intentos
    When corre la sincronizacion
    Then el sistema reintenta hasta 3 veces
    And si finalmente responde 200 el comando se elimina de la cola

