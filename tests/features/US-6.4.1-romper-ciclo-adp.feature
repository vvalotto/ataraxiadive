Feature: US-6.4.1 - Ciclo ADP eliminado en competencia/domain/aggregates

  Scenario: ArchitectAnalyst no reporta ciclos en aggregates de competencia
    Given el codigo de US-6.4.1 esta aplicado
    When se ejecuta ArchitectAnalyst sobre src
    Then el reporte no contiene DependencyCycle para competencia/domain/aggregates
    And should_block es false

  Scenario: La suite de competencia no regresiona
    Given el codigo de US-6.4.1 esta aplicado
    When se ejecutan los tests unitarios, de integracion y features de competencia
    Then todos los tests finalizan sin fallas nuevas

  Scenario: Los imports directos de aggregates siguen funcionando
    Given la API publica de los aggregates Competencia y Performance
    When otro modulo importa Competencia desde competencia.domain.aggregates.competencia
    And otro modulo importa Performance desde competencia.domain.aggregates.performance
    Then ambas importaciones funcionan sin error
