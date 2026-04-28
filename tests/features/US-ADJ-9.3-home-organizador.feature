Feature: US-ADJ-9.3 - Home del organizador

  Background:
    Given existe un usuario autenticado con rol ORGANIZADOR

  Scenario: La vista inicial muestra torneos vigentes
    Given existen torneos en INSCRIPCION_ABIERTA, PREPARACION, EJECUCION y CERRADO
    When el organizador entra a la home del organizador
    Then ve los torneos en INSCRIPCION_ABIERTA, PREPARACION y EJECUCION
    And no ve por defecto el torneo CERRADO

  Scenario: El filtro historico muestra torneos anteriores
    Given existen torneos CERRADO y CANCELADO
    When el organizador activa el filtro de historico
    Then ve los torneos CERRADO y CANCELADO

  Scenario: Cada torneo permite entrar a su gestion
    Given el organizador ve un torneo vigente
    When selecciona la accion principal del torneo
    Then entra al flujo de gestion de ese torneo

  Scenario: La home no se presenta como dashboard operativo
    Given el organizador esta en la pagina inicial
    Then ve una lista de torneos
    And no ve KPIs operativos ni alertas de disciplina activa como contenido principal
