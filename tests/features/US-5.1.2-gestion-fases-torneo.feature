Feature: US-5.1.2 - Transiciones de fase del torneo

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And existe el torneo "BA 2026" con id "T1"

  Scenario: torneo en Creado muestra abrir inscripcion y cancelar
    Given el torneo "T1" esta en estado "CREADO"
    When el organizador accede a "/organizador/torneo/T1"
    Then ve el badge de estado "Creado"
    And ve el boton "Abrir inscripcion"
    And ve el boton "Cancelar torneo"
    And no ve botones de otras transiciones

  Scenario: transicion exitosa Creado a Inscripcion
    Given el torneo "T1" esta en estado "CREADO"
    When el organizador toca "Abrir inscripcion"
    Then el backend recibe PUT "/torneos/T1/abrir-inscripcion"
    And la UI recarga el torneo
    And el badge de estado cambia a "Inscripcion abierta"
    And aparece el boton "Cerrar inscripcion"

  Scenario: transicion EnEjecucion a Preparacion
    Given el torneo "T1" esta en estado "EJECUCION"
    When el organizador toca "Volver a preparacion"
    Then el backend recibe PUT "/torneos/T1/volver-preparacion"
    And la UI recarga el torneo
    And el badge de estado cambia a "Preparacion"

  Scenario: cancelar torneo desde estado activo
    Given el torneo "T1" esta en estado "PREPARACION"
    When el organizador toca "Cancelar torneo"
    Then aparece un dialogo de confirmacion "Cancelar torneo BA 2026"
    When confirma la cancelacion
    Then el backend recibe PUT "/torneos/T1/cancelar"
    And la UI recarga el torneo
    And el badge de estado cambia a "Cancelado"
    And todos los botones de transicion desaparecen

  Scenario: error del backend muestra mensaje sin recargar estado
    Given el torneo "T1" esta en estado "PREPARACION"
    And el backend devuelve 409 al intentar iniciar ejecucion
    When el organizador toca "Iniciar ejecucion"
    Then la UI muestra el mensaje de error devuelto por el backend
    And el badge de estado sigue mostrando "Preparacion"

  Scenario: torneo terminal no muestra acciones de transicion
    Given el torneo "T1" esta en estado "CERRADO"
    When el organizador accede a "/organizador/torneo/T1"
    Then ve el badge de estado "Cerrado"
    And no ve botones de transicion de fase
