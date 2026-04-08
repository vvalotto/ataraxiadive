Feature: US-4.1.2 - Tarjeta Blanca con penalizaciones

  Background:
    Given una Performance en estado ResultadoRegistrado para disciplina DYN con RP 72

  Scenario: asignar tarjeta blanca con una penalizacion
    When el juez asigna tarjeta BlancaConPenalizaciones con penalizacion SIN_CONTACTO_PARED
    Then la Performance pasa a estado Ejecutada
    And rp_medido es 72
    And rp_penalizado es 69
    And el evento TarjetaAsignada registra tipo "BlancaConPenalizaciones"
    And el evento incluye la penalizacion SIN_CONTACTO_PARED con deduccion 3

  Scenario: asignar tarjeta blanca con dos penalizaciones acumuladas
    When el juez asigna tarjeta BlancaConPenalizaciones con penalizaciones SIN_CONTACTO_PARED y FUERA_DE_CARRIL
    Then rp_penalizado es 66
    And el evento TarjetaAsignada registra 2 penalizaciones

  Scenario: lista de penalizaciones vacia lanza excepcion
    When el juez asigna tarjeta BlancaConPenalizaciones con lista de penalizaciones vacia
    Then se lanza PenalizacionesObligatorias

  Scenario: penalizaciones que superan el RP minimo resultan en rp_penalizado 0
    Given una Performance en estado ResultadoRegistrado para disciplina DYN con RP 4
    When el juez asigna tarjeta BlancaConPenalizaciones con penalizaciones SIN_CONTACTO_PARED y FUERA_DE_CARRIL
    Then rp_penalizado es 0
    And el evento TarjetaAsignada registra rp_penalizado "0"

  Scenario: ranking usa rp_penalizado para ordenar
    Given dos performances finalizadas en DYN con RP penalizado 66 y RP valido 70
    When se calcula el ranking de la disciplina DYN
    Then el atleta con RP 70 aparece antes que el atleta con RP penalizado 66
