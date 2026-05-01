Feature: US-5.2.1 - Vista maestro-detalle de ejecucion por disciplina

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id "T1" esta en estado EJECUCION
    And el torneo "T1" tiene las disciplinas "DNF" y "STA" configuradas

  Scenario: maestro muestra todas las disciplinas del torneo
    Given la disciplina "DNF" tiene competencia "C1" en estado Confirmada con grilla confirmada y juez "J1"
    And la disciplina "STA" tiene competencia "C2" en estado Preparacion sin grilla confirmada y juez "J2"
    When el organizador accede al tab "Ejecucion" del torneo "T1"
    Then ve una fila de maestro para la disciplina "DNF"
    And ve una fila de maestro para la disciplina "STA"
    And la disciplina "DNF" muestra estado operativo "Lista para iniciar"
    And la disciplina "STA" muestra bloqueo "Confirmar grilla antes de habilitar"

  Scenario: seleccionar disciplina abre detalle operativo
    Given la disciplina "DNF" tiene competencia "C1" en estado EnEjecucion con 10 atletas
    And 4 atletas tienen performance completada
    When el organizador selecciona la disciplina "DNF" en el maestro
    Then el detalle muestra la grilla OT de "DNF"
    And muestra el juez asignado
    And muestra progreso "4 / 10"
    And muestra atleta actual si existe
    And muestra proximas performances

  Scenario: habilitar disciplina lista para iniciar
    Given la disciplina "DNF" tiene competencia "C1" en estado Confirmada
    And la disciplina "DNF" tiene grilla confirmada
    And la disciplina "DNF" tiene juez "J1" asignado
    When el organizador selecciona la disciplina "DNF" en el maestro
    And toca "Habilitar disciplina"
    Then el frontend envia POST "/competencia/C1/iniciar" con disciplina "DNF" y juez_id "J1"
    And la disciplina "DNF" recarga con estado EnEjecucion
    And la accion "Habilitar disciplina" deja de mostrarse

  Scenario: disciplina sin juez no puede habilitarse
    Given la disciplina "DNF" tiene competencia "C1" en estado Confirmada
    And la disciplina "DNF" tiene grilla confirmada
    And la disciplina "DNF" no tiene juez asignado
    When el organizador selecciona la disciplina "DNF" en el maestro
    Then la accion "Habilitar disciplina" esta deshabilitada
    And el detalle muestra "Asignar juez antes de habilitar"
    And no se envia POST "/competencia/C1/iniciar"

  Scenario: disciplina sin grilla confirmada no puede habilitarse
    Given la disciplina "DNF" tiene competencia "C1" en estado Preparacion
    And la disciplina "DNF" no tiene grilla confirmada
    And la disciplina "DNF" tiene juez "J1" asignado
    When el organizador selecciona la disciplina "DNF" en el maestro
    Then la accion "Habilitar disciplina" esta deshabilitada
    And el detalle muestra "Confirmar grilla antes de habilitar"
    And no se envia POST "/competencia/C1/iniciar"

  Scenario: disciplina finalizada se muestra en modo lectura
    Given la disciplina "DNF" tiene competencia "C1" en estado Finalizada
    When el organizador selecciona la disciplina "DNF" en el maestro
    Then el detalle muestra estado "Finalizada"
    And muestra el hash SHA-256 si esta disponible
    And no muestra acciones de habilitacion
