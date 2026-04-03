Feature: US-3.3.2 — Flujo E2E Torneo-Registro-Competencia

  Scenario: flujo completo inscripcion AP grilla
    Given torneo abierto para inscripcion
    And atleta registrado e inscripto en disciplina STA
    And competencia STA configurada con torneo_id
    When el atleta registra su AP en la competencia
    And se genera y confirma la grilla
    Then la grilla contiene al atleta
    And la competencia referencia el torneo_id correcto

  Scenario: atleta sin AP no aparece en grilla
    Given torneo abierto para inscripcion
    And dos atletas inscriptos solo uno registra AP
    And competencia STA configurada con torneo_id
    When se genera y confirma la grilla
    Then la grilla contiene solo el atleta con AP

  Scenario: multiples atletas ordenados por AP ascendente
    Given torneo abierto para inscripcion
    And tres atletas con APs de 360 300 y 240 segundos en STA
    And competencia STA configurada con torneo_id
    When se genera y confirma la grilla
    Then el orden de la grilla es 240 300 360 segundos
