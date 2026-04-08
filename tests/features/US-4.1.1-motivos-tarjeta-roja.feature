Feature: US-4.1.1 - Motivos de tarjeta roja con catalogo formal

  Background:
    Given una Performance en estado ResultadoRegistrado para disciplina DYN

  Scenario: asignar tarjeta roja con motivo BKO_SUPERFICIE
    Given el juez detecto black-out en superficie
    When asigna tarjeta Roja con motivo BKO_SUPERFICIE y distancia_blackout 45
    Then la Performance pasa a estado Ejecutada
    And el evento TarjetaAsignada registra motivo_dq_codigo "BKO_SUPERFICIE"
    And el evento TarjetaAsignada registra distancia_blackout "45"

  Scenario: asignar tarjeta roja con motivo PROTOCOLO_SUPERFICIE
    Given el atleta no realizo el protocolo de superficie reglamentario
    When asigna tarjeta Roja con motivo PROTOCOLO_SUPERFICIE
    Then la Performance pasa a estado Ejecutada
    And el evento TarjetaAsignada registra motivo_dq_codigo "PROTOCOLO_SUPERFICIE"
    And el evento TarjetaAsignada no registra distancia_blackout

  Scenario: tarjeta roja sin motivo_dq lanza excepcion
    When asigna tarjeta Roja sin especificar MotivoDQ
    Then se lanza MotivoDQObligatorio

  Scenario: BKO superficie sin distancia_blackout lanza excepcion
    When asigna tarjeta Roja con motivo BKO_SUPERFICIE sin distancia_blackout
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: BKO subacuatico con distancia_blackout cero lanza excepcion
    When asigna tarjeta Roja con motivo BKO_SUBACUATICO y distancia_blackout 0
    Then se lanza DistanciaBlackoutObligatoria

  Scenario: motivo de DQ no BKO no debe tener distancia_blackout
    When asigna tarjeta Roja con motivo SALIDA_EN_FALSO y distancia_blackout 20
    Then se lanza DistanciaBlackoutNoAplica

  Scenario: tarjeta amarilla mantiene motivo texto libre
    When asigna tarjeta Amarilla con motivo texto "duda sobre protocolo"
    Then la Performance pasa a estado Ejecutada
    And el evento TarjetaAsignada registra motivo_texto "duda sobre protocolo"
    And el evento TarjetaAsignada no registra motivo_dq_codigo
