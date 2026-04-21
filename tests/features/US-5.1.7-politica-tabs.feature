Feature: US-5.1.7 - Politica de tabs por fase y estado CANCELADO

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR

  Scenario: torneo en INSCRIPCION_ABIERTA solo habilita Detalle e Inscriptos
    Given el torneo "BA 2026" esta en estado INSCRIPCION_ABIERTA
    When el organizador navega a la pagina de detalle
    Then las tabs "Detalle" e "Inscriptos" estan habilitadas
    And las tabs "Grilla", "Jueces" y "Ejecucion" estan visibles pero deshabilitadas

  Scenario: tab deshabilitada no responde a click
    Given el torneo esta en INSCRIPCION_ABIERTA
    When el organizador hace click en la tab "Grilla"
    Then el activeTab sigue siendo "Detalle"
    And el panel Grilla no se renderiza

  Scenario: torneo en PREPARACION habilita hasta Jueces
    Given el torneo esta en estado PREPARACION
    When el organizador navega a la pagina de detalle
    Then las tabs "Detalle", "Inscriptos", "Grilla" y "Jueces" estan habilitadas
    And la tab "Ejecucion" esta visible pero deshabilitada

  Scenario: torneo CANCELADO reemplaza panel por mensaje de cancelacion
    Given el torneo esta en estado CANCELADO
    When el organizador navega a la pagina de detalle
    Then se muestra el nombre del torneo y el mensaje "Torneo cancelado"
    And las tabs "Inscriptos", "Grilla", "Jueces" y "Ejecucion" no estan presentes
    And AccionesPanel no muestra acciones

  Scenario: activeTab se resetea si torneo recarga en estado incompatible
    Given el organizador esta en la tab "Grilla" del torneo en PREPARACION
    When el torneo transiciona a INSCRIPCION_ABIERTA y la pagina refresca
    Then el activeTab vuelve a "Detalle"
    And el panel Grilla no se renderiza
