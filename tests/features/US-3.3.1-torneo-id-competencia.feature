Feature: US-3.3.1 — torneo_id en Competencia

  Scenario: configurar competencia con torneo_id
    Given un torneo_id valido
    When se configura el intervalo OT con torneo_id
    Then la competencia almacena el torneo_id
    And GET estado retorna el torneo_id

  Scenario: configurar competencia sin torneo_id (backward compat)
    Given payload sin campo torneo_id
    When se configura el intervalo OT sin torneo_id
    Then la competencia se crea con torneo_id nulo
    And los tests existentes siguen pasando

  Scenario: listar competencias de un torneo
    Given 3 competencias configuradas con el mismo torneo_id
    When se consultan competencias por torneo_id
    Then se retornan 3 competencias

  Scenario: listar competencias filtra por torneo_id correcto
    Given 2 competencias de torneo A y 1 de torneo B
    When se consultan competencias por torneo A
    Then se retornan solo 2 competencias
