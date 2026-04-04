Feature: Parseo de AP en formato MM:SS

  Scenario: Parsear AP STA valido en formato MM:SS
    When se crea TiempoAP desde "02:30"
    Then el valor en segundos es 150

  Scenario: Parsear AP largo valido en formato HH:MM:SS
    When se crea TiempoAP desde "01:00:00"
    Then el valor en segundos es 3600

  Scenario: Formato invalido es rechazado
    When se intenta crear TiempoAP desde "abc"
    Then el sistema lanza FormatoTiempoInvalido

  Scenario: Segundos fuera de rango son rechazados
    When se intenta crear TiempoAP desde "02:60"
    Then el sistema lanza FormatoTiempoInvalido

  Scenario: Valor cero es rechazado
    When se intenta crear TiempoAP desde "00:00"
    Then el sistema lanza ValorTiempoInvalido

  Scenario: Constructor desde segundos directo
    When se crea TiempoAP desde segundos Decimal("196")
    Then el valor en segundos es 196

  Scenario: Segundos negativos o cero son rechazados desde constructor directo
    When se intenta crear TiempoAP desde segundos Decimal("0")
    Then el sistema lanza ValorTiempoInvalido
