Feature: US-ADJ-12.5 — BC Registro: inscripción con estado de aceptación

  Background:
    Given un torneo y un atleta inscripto activo con estado aceptación "ACEPTADO"

  Scenario: Al inscribirse el estado de aceptación por defecto es ACEPTADO
    Then el estado_aceptacion de la inscripción es "ACEPTADO"

  Scenario: El organizador puede rechazar una inscripción
    When el organizador cambia el estado de aceptación a "RECHAZADO"
    Then el estado_aceptacion de la inscripción es "RECHAZADO"

  Scenario: El organizador puede re-aceptar una inscripción rechazada
    Given la inscripción tiene estado_aceptacion "RECHAZADO"
    When el organizador cambia el estado de aceptación a "ACEPTADO"
    Then el estado_aceptacion de la inscripción es "ACEPTADO"

  Scenario: El endpoint PATCH requiere rol ORGANIZADOR
    When un usuario con rol "ATLETA" intenta cambiar el estado de aceptación
    Then la respuesta es 403

  Scenario: El endpoint detalle devuelve datos del atleta y estado de aceptación
    When el organizador consulta el detalle de la inscripción
    Then la respuesta incluye nombre, categoría, club, brevet, dni, telefono, estado_aceptacion y URLs de adjuntos

  Scenario: La columna estado_aceptacion persiste correctamente en SQLite
    When el organizador cambia el estado de aceptación a "RECHAZADO"
    And se recarga la inscripción desde la base de datos
    Then el estado_aceptacion cargado es "RECHAZADO"
