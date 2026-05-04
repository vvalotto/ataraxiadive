Feature: US-6.1.5 — AtletaCard compacta en paso 5 (RpSelector)

  Scenario: AtletaCard variant compact muestra solo nombre y estado
    Given una AtletaCard renderizada con variant compact
    When se renderiza el componente
    Then aparece el nombre del atleta
    And aparece el estado EN CURSO
    And no aparece Performance anunciada
    And no aparece Andarivel
    And no aparece OT

  Scenario: AtletaCard variant full muestra todos los campos
    Given una AtletaCard renderizada con variant full
    When se renderiza el componente
    Then aparece el nombre del atleta
    And aparece Performance anunciada
    And aparece Andarivel
    And aparece OT

  Scenario: AtletaCard sin prop variant usa full por defecto
    Given una AtletaCard sin prop variant
    When se renderiza el componente
    Then aparece Performance anunciada
    And aparece Andarivel
    And aparece OT

  Scenario: Paso 6 RpSelector usa AtletaCard compacta
    Given un juez en paso 6 del flujo de performance
    When se renderiza PerformanceFlowPage en paso 6
    Then la tarjeta del atleta es compacta
    And el RpSelector esta visible
    And no aparecen AP ni andarivel ni OT en la tarjeta

  Scenario: Otros pasos del flujo no usan AtletaCard compacta en header
    Given un juez en pasos 1 2 o 3 del flujo de performance
    When se renderiza PerformanceFlowPage
    Then la AtletaCard muestra todos los campos del atleta
