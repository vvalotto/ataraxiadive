Feature: Secciones primarias del organizador dentro de la arquitectura UX correcta

  Scenario: Grilla se navega como seccion primaria del shell
    Given un organizador autenticado con un torneo seleccionado
    When abre Grilla desde la navbar superior
    Then ve la seccion Grilla dentro del shell dark del organizador
    And la navegacion principal permanece visible

  Scenario: Jueces se navega como seccion primaria del shell
    Given un organizador autenticado con un torneo seleccionado
    When abre Jueces desde la navbar superior
    Then ve la seccion Jueces dentro del shell dark del organizador
    And la navegacion principal permanece visible

  Scenario: Torneo se navega como seccion primaria del shell
    Given un organizador autenticado con un torneo seleccionado
    When abre Torneo desde la navbar superior
    Then ve la seccion Torneo dentro del shell dark del organizador
    And la navegacion principal permanece visible

  Scenario: Audit Log se navega como seccion primaria del shell
    Given un organizador autenticado con un torneo seleccionado
    When abre Audit Log desde la navbar superior
    Then ve la seccion Audit Log dentro del shell dark del organizador
    And la navegacion principal permanece visible

  Scenario: DetalleTorneoPage deja de concentrar navegacion primaria redundante
    Given un organizador autenticado dentro de un torneo
    When abre la vista de detalle del torneo
    Then no necesita tabs o accesos locales equivalentes a Grilla, Jueces, Torneo o Audit Log
    And esas secciones se resuelven desde la navbar principal del shell

  Scenario: Las vistas contextuales de auditoria mantienen el shell principal
    Given un organizador entra a una auditoria de competencia o de performance
    Then la navbar principal del organizador sigue visible
    And la vista contextual no reemplaza la navegacion principal
