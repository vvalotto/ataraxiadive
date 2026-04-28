Feature: US-ADJ-9.4 - Dashboard operativo del organizador

  Background:
    Given existe un usuario autenticado con rol ORGANIZADOR
    And existe un torneo activo o seleccionado para operar

  Scenario: El Panel muestra KPIs operativos y disciplina activa
    Given el torneo tiene una disciplina en ejecucion
    When el organizador abre la seccion Panel
    Then ve un strip de KPIs operativos
    And ve la disciplina en ejecucion destacada
    And no ve el listado general de torneos como contenido principal

  Scenario: El Panel muestra alertas activas
    Given existe al menos una alerta operativa pendiente
    When el organizador abre la seccion Panel
    Then ve una seccion de alertas activas
    And cada alerta expone una accion para resolverla

  Scenario: El Panel comunica explicitamente cuando no hay alertas
    Given no existen alertas operativas activas
    When el organizador abre la seccion Panel
    Then ve el mensaje "Sin alertas"

  Scenario: El Panel muestra proximos atletas de la disciplina activa
    Given la disciplina activa tiene grilla en curso
    When el organizador abre la seccion Panel
    Then ve la lista de proximos atletas de la disciplina activa
    And el siguiente atleta aparece visualmente destacado

  Scenario: El Panel muestra otras disciplinas en modo informativo
    Given el torneo tiene disciplinas adicionales fuera de ejecucion
    When el organizador abre la seccion Panel
    Then ve otras disciplinas del torneo en estado informativo
    And esas disciplinas no reemplazan la disciplina activa destacada
