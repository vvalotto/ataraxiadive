Feature: Disciplinas con acrónimos AIDA correctos

  Scenario: DBF es una disciplina de distancia válida
    Given el sistema conoce las disciplinas AIDA
    When se consulta la disciplina "DBF"
    Then el sistema la reconoce como disciplina de distancia
    And su orden de grilla es ascendente

  Scenario: SPE es una disciplina de distancia válida
    Given el sistema conoce las disciplinas AIDA
    When se consulta la disciplina "SPE"
    Then el sistema la reconoce como disciplina de distancia

  Scenario: Los acrónimos obsoletos no son reconocidos
    Given el sistema conoce las disciplinas AIDA
    When se intenta usar "DYNB" como disciplina
    Then el sistema rechaza el valor como disciplina desconocida

  Scenario: Los acrónimos obsoletos SPE2X50 no son reconocidos
    Given el sistema conoce las disciplinas AIDA
    When se intenta usar "SPE2X50" como disciplina
    Then el sistema rechaza el valor como disciplina desconocida
