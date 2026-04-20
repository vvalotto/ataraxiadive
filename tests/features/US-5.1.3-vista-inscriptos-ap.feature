Feature: US-5.1.3 - Vista de inscriptos con estado de AP

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id "T1" esta en estado "PREPARACION"
    And la disciplina "DNF" tiene competencia_id "C1"

  Scenario: lista de inscriptos con estado de AP mixto
    Given hay 3 atletas inscriptos en "DNF": "Garcia" con AP "75m", "Lopez" sin AP y "Ruiz" con AP "60m"
    When el organizador accede al tab "Inscriptos" del torneo "T1"
    Then ve 3 filas en la tabla
    And "Garcia" muestra badge verde "AP registrado" con valor "75m"
    And "Lopez" muestra badge amarillo "Sin AP"
    And "Ruiz" muestra badge verde "AP registrado" con valor "60m"

  Scenario: filtrar por disciplina cuando el torneo tiene multiples disciplinas
    Given el torneo "T1" tiene disciplinas "DNF" y "STA"
    And hay atletas inscriptos en ambas disciplinas
    When el organizador selecciona el filtro "DNF"
    Then solo ve atletas inscriptos en "DNF"

  Scenario: sin inscriptos muestra mensaje vacio
    Given no hay atletas inscriptos en el torneo "T1"
    When el organizador accede al tab "Inscriptos"
    Then ve el mensaje "No hay atletas inscriptos en este torneo"

  Scenario: atleta inscripto en varias disciplinas muestra estado por disciplina
    Given el atleta "Garcia" esta inscripto en "DNF" y "STA"
    And tiene AP en "DNF" pero no en "STA"
    When el organizador ve la tabla
    Then "Garcia" muestra "DNF: AP registrado"
    And "Garcia" muestra "STA: Sin AP" en la misma fila
