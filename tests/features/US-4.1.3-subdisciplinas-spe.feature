Feature: US-4.1.3 - Subdisciplinas SPE

  Scenario: SPE_2X50 tiene unidad Segundos y pertenece a la familia SPE
    Given el DisciplinaDescriptor para SPE_2X50
    Then unidad_esperada es Segundos
    And orden_ascendente es False
    And es_tiempo() retorna True
    And es_spe() retorna True

  Scenario: SPE_4X50 y SPE_8X50 son eventos independientes en el mismo torneo
    Given un torneo con SPE_4X50 y SPE_8X50 configuradas
    When se consultan las disciplinas configuradas del torneo
    Then SPE_4X50 queda configurada en el torneo
    And SPE_8X50 queda configurada en el torneo
    And ambas disciplinas son independientes

  Scenario: ranking SPE_2X50 es independiente de SPE_8X50
    Given un torneo con performances en SPE_2X50 y SPE_8X50
    When se consulta el ranking de SPE_2X50
    Then el ranking de SPE_2X50 no incluye atletas de SPE_8X50

  Scenario: AP en SPE se registra en segundos
    Given una Performance para disciplina SPE_4X50
    When se registra AP con valor 180 y unidad Segundos
    Then el AP queda registrado correctamente

  Scenario: AP en SPE con unidad metros lanza excepción
    Given una Performance para disciplina SPE_2X50
    When se registra AP con valor 100 y unidad Metros
    Then se lanza UnidadIncompatible

  Scenario: disciplina SPE genérica no puede agregarse a torneo nuevo
    Given un Torneo recién creado
    When se intenta agregar disciplina SPE genérica al torneo
    Then se lanza DisciplinaObsoleta
