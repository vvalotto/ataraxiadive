Feature: US-1.4.1 — Black-out con Distancia
  Como juez
  Quiero registrar un black-out con la distancia alcanzada
  Para que el resultado quede documentado correctamente según RF-EJ-07

  Background:
    Given una Performance en estado ResultadoRegistrado

  Scenario: Juez registra black-out con distancia válida
    When el juez asigna tarjeta roja con motivo "black-out" y distancia 45.5 metros
    Then la Performance queda en estado Ejecutada
    And el evento TarjetaAsignada contiene distancia_blackout 45.5

  Scenario: Black-out sin distancia es rechazado
    When el juez asigna tarjeta roja con motivo "black-out" sin distancia
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: Black-out con distancia cero es rechazado
    When el juez asigna tarjeta roja con motivo "black-out" y distancia 0 metros
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: Tarjeta roja sin black-out sigue funcionando (regresión)
    When el juez asigna tarjeta roja con motivo "tiempo excedido" sin distancia
    Then la Performance queda en estado Ejecutada
