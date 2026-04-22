Feature: US-ADJ-8.2 - Restricciones operativas por torneo y fase

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR

  Scenario: Selector de grilla usa solo disciplinas del torneo actual
    Given el torneo "BA 2026" con id T1 tiene disciplinas STA y DNF configuradas
    And el sistema conoce tambien las disciplinas CWT y FIM
    When el organizador abre el selector de disciplinas para generar grilla de T1
    Then el selector muestra STA y DNF
    And el selector no muestra CWT
    And el selector no muestra FIM

  Scenario: No se puede pasar a premiacion con una competencia en ejecucion
    Given el torneo "BA 2026" con id T1 esta en estado EJECUCION
    And la disciplina DNF tiene competencia C1 en estado Finalizada
    And la disciplina STA tiene competencia C2 en estado EnEjecucion
    When el organizador ve las acciones de fase de T1
    Then la accion "Pasar a premiacion" esta bloqueada
    And el panel indica que falta cerrar STA
    And no se solicita la transicion a PREMIACION

  Scenario: No se puede pasar a premiacion si falta crear una competencia esperada
    Given el torneo "BA 2026" con id T1 esta en estado EJECUCION
    And el torneo T1 tiene disciplinas DNF y STA configuradas
    And solo DNF tiene competencia en estado Finalizada
    When el organizador ve las acciones de fase de T1
    Then la accion "Pasar a premiacion" esta bloqueada
    And el panel indica que falta cerrar STA
    And no se solicita la transicion a PREMIACION

  Scenario: Se puede pasar a premiacion con todas las competencias finalizadas
    Given el torneo "BA 2026" con id T1 esta en estado EJECUCION
    And la disciplina DNF tiene competencia C1 en estado Finalizada
    And la disciplina STA tiene competencia C2 en estado Finalizada
    When el organizador ve las acciones de fase de T1
    Then la accion "Pasar a premiacion" esta habilitada
    When el organizador ejecuta "Pasar a premiacion"
    Then el frontend solicita la transicion a PREMIACION
