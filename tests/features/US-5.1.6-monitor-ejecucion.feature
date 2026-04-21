Feature: US-5.1.6 - Monitor de ejecucion del organizador

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id "T1" esta en estado EnEjecucion
    And la disciplina "DNF" tiene competencia "C1" en estado EnEjecucion con 10 atletas
    And 6 atletas tienen performance completada
    And 1 atleta tiene performance en Llamada con nombre "Garcia" y OT "14:24"

  Scenario: organizador ve progreso en tiempo real de una disciplina
    When accede al tab "Ejecucion" del torneo "T1"
    Then ve la card de "DNF" con barra de progreso "6 / 10"
    And ve "Garcia" como atleta en curso con OT "14:24"
    And ve los proximos 2 atletas

  Scenario: disciplina sin atleta en Llamada muestra estado de espera
    Given la disciplina "STA" tiene competencia "C2" en estado EnEjecucion sin atleta en Llamada
    When el organizador ve la card de "STA"
    Then la seccion "En curso" muestra "- En espera -"
    And se muestra el proximo atleta y su OT si existe

  Scenario: refresco automatico cada 30 segundos
    Given el organizador esta en el tab "Ejecucion"
    When pasan 30 segundos sin interaccion
    Then la UI refresca los datos llamando de nuevo a "/competencia/C1/progreso"
    And los datos del monitor se actualizan sin recargar la pagina completa

  Scenario: todas las disciplinas completas habilita transicion a premiacion
    Given todas las competencias del torneo "T1" estan en estado CompetenciaFinalizada
    When el organizador accede al tab "Ejecucion"
    Then ve el mensaje "Todas las disciplinas completadas"
    And ve el estado de premiacion disponible en el panel de acciones del torneo

  Scenario: sin disciplinas en ejecucion muestra estado de espera
    Given no hay competencias en estado EnEjecucion en el torneo "T1"
    When el organizador accede al tab "Ejecucion"
    Then ve el mensaje "Ninguna disciplina en ejecucion"
