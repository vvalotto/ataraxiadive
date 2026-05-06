Feature: US-6.2.6 - Pagina de Podios separada de Resultados

  Scenario: Acceder a la pagina de Podios con torneo_id valido
    Given un torneo con resultados calculados
    When el organizador navega a "/organizador/podios?torneo_id={id}"
    Then ve la seccion de podios por disciplina
    And ve la seccion de podios overall

  Scenario: La pagina de Resultados ya no muestra los podios
    Given un torneo con resultados calculados
    When el organizador navega a "/organizador/resultados?torneo_id={id}"
    Then ve rankings por disciplina
    And no ve ninguna seccion de podios
    And no ve ninguna seccion overall de premiacion

  Scenario: Sin torneo_id, la pagina de Podios muestra el selector de torneo
    Given existen torneos disponibles para el organizador
    When el organizador navega a "/organizador/podios" sin query params
    Then ve el selector de torneo
    And puede entrar a los podios de un torneo desde ese selector

  Scenario: Existe enlace de navegacion hacia Podios con torneo activo
    Given un torneo activo seleccionado
    When el organizador ve la navegacion del torneo
    Then hay un item "Podios"
    And el item navega a "/organizador/podios?torneo_id={id}"
