Feature: US-5.6.6 - UI podios por categoria y genero

  Background:
    Given el organizador esta autenticado
    And existe el torneo "BA Open 2026"
    And la vista ResultadosPage muestra la disciplina seleccionada

  Scenario: podio de disciplina muestra los 6 paneles al finalizar
    Given la disciplina DNF esta FINALIZADA con ranking calculado
    And hay atletas en SENIOR_MASCULINO, SENIOR_FEMENINO y JUNIOR_MASCULINO
    When el organizador selecciona la disciplina DNF
    Then ve 6 paneles de podio:
      | panel     |
      | SENIOR M |
      | SENIOR F |
      | MASTER M |
      | MASTER F |
      | JUNIOR M |
      | JUNIOR F |
    And los paneles sin atletas muestran "Sin participantes"

  Scenario: posiciones y badges reflejan el orden por puntos
    Given la disciplina DNF esta FINALIZADA con ranking calculado
    And el panel SENIOR M tiene:
      | atleta | puntos |
      | Luis   | 80.00  |
      | Pedro  | 60.00  |
    When el organizador ve el panel SENIOR M
    Then Luis aparece en posicion 1 con badge oro
    And Pedro aparece en posicion 2 con badge plata

  Scenario: empate en puntos comparte posicion
    Given la disciplina DNF esta FINALIZADA con ranking calculado
    And el panel SENIOR F tiene:
      | atleta | puntos |
      | Ana    | 100.00 |
      | Maria  | 100.00 |
    When el organizador ve el panel SENIOR F
    Then Ana aparece en posicion 1
    And Maria aparece en posicion 1

  Scenario: overall en empty state mientras hay disciplinas pendientes
    Given el torneo tiene 2 disciplinas
    And 1 disciplina esta FINALIZADA
    And 1 disciplina sigue pendiente
    When el organizador ve la seccion Overall
    Then se muestra "Disponible al cerrar todas las disciplinas"
    And se muestra "(1 de 2 disciplinas cerradas)"

  Scenario: overall disponible al cerrar todas las disciplinas
    Given todas las disciplinas del torneo estan FINALIZADAS
    And el overall fue calculado
    When el organizador ve la seccion Overall
    Then ve 6 paneles de overall por categoria y genero
    And cada panel muestra puntos_overall acumulados

  Scenario: podios no visibles con disciplina en ejecucion
    Given la disciplina DNF esta EN EJECUCION
    When el organizador selecciona la disciplina DNF
    Then la seccion Podios no se muestra
