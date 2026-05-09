Feature: US-6.4.2 - CalcularOverallHandler usa proyeccion materializada

  Scenario: CalcularOverall no escanea el event store de competencia
    Given un torneo con competencias registradas en la proyeccion competencias_por_torneo
    When se ejecuta CalcularOverallCommand para ese torneo
    Then el handler consulta competencias_por_torneo.listar_por_torneo una sola vez
    And no llama a load_all_streams_with_prefix sobre el event store de competencia

  Scenario: El resultado del overall se preserva
    Given un torneo con competencias finalizadas y rankings calculados por disciplina
    When se ejecuta CalcularOverallCommand usando la proyeccion materializada
    Then los entries del ranking overall conservan puntajes y posiciones esperadas

  Scenario: Torneo sin competencias materializadas no falla
    Given un torneo sin competencias registradas en la proyeccion competencias_por_torneo
    When se ejecuta CalcularOverallCommand para ese torneo
    Then el handler retorna una lista vacia
    And no persiste un evento RankingOverallCalculado
