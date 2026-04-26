Feature: US-5.6.2 — TipoReglamento en Torneo y DI de AlgoritmoPuntaje en CalcularRanking

  Background:
    Given un torneo base con datos validos

  Scenario: torneo sin reglamento explicito usa FAAS por defecto
    Given un torneo creado sin tipo_reglamento explicito
    When se consulta el tipo_reglamento del torneo
    Then el tipo_reglamento es "FAAS"

  Scenario: torneo con reglamento FAAS persiste y recupera correctamente
    Given un torneo creado con tipo_reglamento "FAAS"
    When se persiste en el repositorio y se recupera por id
    Then el tipo_reglamento recuperado es "FAAS"

  Scenario: CalcularRankingHandler usa el algoritmo inyectado sin instanciar uno propio
    Given un handler construido con un algoritmo mock
    And una disciplina DNF con resultados de dos atletas
    When se ejecuta el comando CalcularRanking
    Then el algoritmo mock recibe la llamada a calcular
