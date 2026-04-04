Feature: API Overall por torneo
  # US-3.5.3 | INV-OV-API-01 | INV-OV-API-02 | INV-OV-API-03
  # Como atleta u organizador, quiero consultar el ranking general
  # de un torneo para ver las posiciones finales de todas las disciplinas.

  Scenario: overall calculado disponible
    Given P-09 calculo el overall para un torneo con STA y DNF
    When consulto GET /resultados/{torneo_id}/overall
    Then la respuesta es 200 con calculado true
    And el ranking overall contiene entradas ordenadas por posicion

  Scenario: overall no calculado aun
    Given un torneo con disciplinas no finalizadas
    When consulto GET /resultados/{torneo_id}/overall
    Then la respuesta es 200 con calculado false
    And el ranking overall es vacio

  Scenario: respuesta incluye detalle por disciplina
    Given P-09 calculo el overall para un torneo con STA y DNF
    When consulto GET /resultados/{torneo_id}/overall
    Then cada entrada incluye detalle STA y DNF con sus posiciones

  Scenario: podio marcado correctamente
    Given un overall calculado con 5 atletas
    When consulto GET /resultados/{torneo_id}/overall
    Then los puestos 1, 2 y 3 tienen en_podio true
    And los demas puestos tienen en_podio false
