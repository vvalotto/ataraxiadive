@US-1.2.2
Feature: Llamar Atleta
  Como sistema de gestión de competencia,
  quiero llamar a un atleta según el orden de grilla
  para dar inicio formal al OT y registrar que la competencia espera su actuación.

  Background:
    Given una competencia activa con id "C001" en estado "EnEjecucion"
    And un participante con id "P001"
    And la disciplina "STA"
    And la performance del participante está en estado "AnunciadaAP"

  Scenario: Sistema llama al atleta exitosamente
    Given la competencia está en estado "EnEjecucion"
    When el sistema llama al atleta con ot_programado "2026-03-22T10:30:00" y posicion_grilla 3
    Then la performance pasa al estado "Llamada"
    And el evento "AtletaLlamado" persiste en el event stream
    And el evento contiene posicion_grilla 3 y ot_programado "2026-03-22T10:30:00"

  Scenario: Rechazo por performance no en estado AnunciadaAP
    Given la performance del participante está en estado "Llamada"
    When el sistema intenta llamar al atleta con ot_programado "2026-03-22T10:30:00" y posicion_grilla 1
    Then el sistema rechaza la operación con error "EstadoInvalidoParaLlamar"

  Scenario: Rechazo por competencia no en ejecución
    Given la competencia NO está en estado "EnEjecucion"
    When el sistema intenta llamar al atleta con ot_programado "2026-03-22T10:30:00" y posicion_grilla 3
    Then el sistema rechaza la operación con error "CompetenciaNoEnEjecucion"
