Feature: US-3.1.2 — API REST Torneo — CRUD + transiciones de fase

  Background:
    Given la base de datos de torneos está limpia

  Scenario: crear torneo exitosamente
    Given un payload válido con nombre, fechas, sede y entidad organizadora
    When POST /torneos con el payload
    Then la respuesta es 201 con torneo_id
    And GET /torneos/{torneo_id} retorna el torneo con estado CREADO

  Scenario: crear torneo con fecha_fin anterior a fecha_inicio
    Given un payload con fecha_fin anterior a fecha_inicio
    When POST /torneos con el payload
    Then la respuesta es 422 Unprocessable Entity

  Scenario: crear torneo con nombre vacío
    Given un payload con nombre vacío
    When POST /torneos con el payload
    Then la respuesta es 422 Unprocessable Entity

  Scenario: ciclo completo de transiciones via API
    Given un torneo creado con estado CREADO
    When se ejecutan secuencialmente las transiciones abrir-inscripcion, cerrar-inscripcion, iniciar-ejecucion, iniciar-premiacion, cerrar
    Then cada transición retorna 200
    And el estado final del torneo es CERRADO

  Scenario: retroceso de ejecución a preparación
    Given un torneo en estado EJECUCION
    When PUT /torneos/{torneo_id}/volver-preparacion
    Then la respuesta es 200
    And el estado del torneo es PREPARACION

  Scenario: transición inválida via API
    Given un torneo creado con estado CREADO
    When PUT /torneos/{torneo_id}/iniciar-ejecucion
    Then la respuesta es 409 Conflict
    And el mensaje de error describe la transición inválida

  Scenario: cancelar torneo en cualquier estado no terminal
    Given un torneo en estado INSCRIPCION_ABIERTA
    When PUT /torneos/{torneo_id}/cancelar
    Then la respuesta es 200
    And el estado del torneo es CANCELADO

  Scenario: torneo inexistente retorna 404
    Given un UUID que no existe en la base de datos
    When GET /torneos/{uuid}
    Then la respuesta es 404 Not Found

  Scenario: listar torneos
    Given 3 torneos creados
    When GET /torneos
    Then la respuesta es 200 con lista de 3 torneos

  Scenario: respuesta completa de GET /torneos/{id}
    Given un torneo creado con todos sus campos
    When GET /torneos/{torneo_id}
    Then la respuesta contiene torneo_id, nombre, descripcion, fechas, sede, entidad_organizadora y estado
