Feature: US-1.4.1 — Black-out con Distancia
  Como juez
  Quiero registrar un black-out con la distancia alcanzada
  Para que el resultado quede documentado correctamente según RF-EJ-07

  Background:
    Given una Performance en estado ResultadoRegistrado

  Scenario: Juez registra BKO_SUPERFICIE con distancia válida
    When el juez asigna tarjeta roja con motivo_dq "BKO_SUPERFICIE" y distancia 45.5 metros
    Then la Performance queda en estado Ejecutada
    And el evento TarjetaAsignada contiene distancia_blackout 45.5

  Scenario: BKO_SUPERFICIE sin distancia es rechazado
    When el juez asigna tarjeta roja con motivo_dq "BKO_SUPERFICIE" sin distancia
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: BKO_SUPERFICIE con distancia cero es rechazado
    When el juez asigna tarjeta roja con motivo_dq "BKO_SUPERFICIE" y distancia 0 metros
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: Motivo no BKO con distancia es rechazado
    When el juez asigna tarjeta roja con motivo_dq "SALIDA_EN_FALSO" y distancia 20 metros
    Then se lanza DistanciaBlackoutNoAplica
