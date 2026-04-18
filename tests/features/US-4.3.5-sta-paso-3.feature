Feature: US-4.3.5 - Adaptacion STA en el Paso 3

  Background:
    Given el juez "juez@ataraxia.com" esta autenticado
    And la competencia C1 es de disciplina STA
    And el atleta "Rodriguez, Pedro" tiene AP 4m30s en AnunciadaAP

  Scenario: Paso 3 en STA muestra boton adaptado
    Given el juez llamo a Rodriguez y esta en el Paso 3
    And la ventana OT esta activa
    Then el boton muestra "VIAS RESPIRATORIAS EN AGUA"
    And no se muestra "ATLETA INICIA"
    And hay un texto descriptivo "Las vias respiratorias del atleta entran en contacto con el agua"

  Scenario: Tap en boton STA arranca el cronometro normalmente
    Given el juez esta en el Paso 3 de STA con ventana activa
    When toca "VIAS RESPIRATORIAS EN AGUA"
    Then la UI avanza al Paso 4
    And el estado visible es "Performance en curso"
    And el cronometro local ya esta iniciado

  Scenario: Paso 3 en DNF mantiene boton estandar
    Given el juez esta en el Paso 3 de una disciplina DNF con ventana activa
    Then el boton muestra "ATLETA INICIA"
    And no hay mencion de "vias respiratorias"

  Scenario: Paso 5 de STA usa selector de tiempo
    Given el juez llego al Paso 5 de STA
    Then el selector muestra minutos y segundos
    And los presets son "2:00", "3:00", "4:00", "5:00", "6:00"
    And los ajustes son "-5s", "+5s", "+30s", "+1m"

  Scenario: Paso 5 de DNF mantiene selector en metros
    Given el juez llego al Paso 5 de DNF
    Then el selector muestra metros y centimetros
    And los presets son "25", "50", "75", "100", "125"
