Feature: US-5.1.10 - Acciones correctas de fase en AccionesPanel

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR

  Scenario: torneo en EJECUCION muestra Iniciar premiacion, no Iniciar ejecucion
    Given el torneo T1 esta en estado EJECUCION
    When el organizador navega a la pagina de detalle de T1
    Then AccionesPanel muestra "Iniciar premiacion"
    And AccionesPanel muestra "Volver a preparacion"
    And AccionesPanel NO muestra "Iniciar ejecucion"

  Scenario: torneo en PREPARACION muestra Iniciar ejecucion
    Given el torneo T1 esta en estado PREPARACION
    When el organizador navega a la pagina de detalle de T1
    Then AccionesPanel muestra "Iniciar ejecucion"
    And AccionesPanel NO muestra "Iniciar premiacion"

  Scenario: accion Iniciar premiacion ejecuta transicion exitosa
    Given el torneo T1 esta en estado EJECUCION
    When el organizador hace click en "Iniciar premiacion"
    Then el backend recibe PUT /torneos/T1/iniciar-premiacion
    And el torneo recarga en estado PREMIACION
    And AccionesPanel muestra "Cerrar torneo"

  Scenario: campo estado del torneo llega como string exacto del enum
    Given el backend devuelve { estado: "EJECUCION" } para el torneo T1
    When fetchTorneo(T1) resuelve
    Then el valor de estado es exactamente el string "EJECUCION"
    And coincide con la clave del mapa ACCIONES_POR_ESTADO
