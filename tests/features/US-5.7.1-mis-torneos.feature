Feature: US-5.7.1 - Mis torneos inscriptos en la pagina Torneos
  Como atleta autenticado
  Quiero ver primero los torneos en los que ya estoy inscripto
  Para distinguir mi participacion de las inscripciones abiertas

  Background:
    Given el atleta "ana@email.com" esta autenticado con rol ATLETA
    And existe el torneo "BA Open 2026" en estado "EJECUCION"
    And Ana esta inscripta en "BA Open 2026" con disciplinas DNF y STA
    And existe el torneo "Open Litoral 2026" en estado "INSCRIPCION_ABIERTA" sin inscripcion de Ana

  Scenario: Atleta ve sus torneos inscriptos en la primera seccion
    When Ana navega a la tab "Torneos"
    Then ve la seccion "Mis torneos" primero
    And "BA Open 2026" aparece en "Mis torneos" con badge "EN EJECUCION"
    And "BA Open 2026" muestra chips "DNF" y "STA"

  Scenario: Torneo inscripto no aparece en inscripciones abiertas
    When Ana navega a la tab "Torneos"
    Then "BA Open 2026" no aparece en la seccion "Inscripciones abiertas"
    And "Open Litoral 2026" si aparece en "Inscripciones abiertas"

  Scenario: Estado vacio cuando el atleta no tiene inscripciones
    Given el atleta no esta inscripto en ningun torneo
    When navega a la tab "Torneos"
    Then ve el mensaje "Aun no estas inscripto en ningun torneo." en la seccion "Mis torneos"
