Feature: US-4.5.5 - Cableado P-10 al endpoint de inscripcion

  Scenario: email enviado al inscribir atleta via HTTP
    Given existe un atleta con email "test@ataraxiadive.io" y un torneo abierto
    And el endpoint de inscripcion tiene P-10 configurada
    When se hace POST /registro/inscripciones con atleta_id y torneo_id validos
    Then la inscripcion se crea con status 201
    And se envia un email a "test@ataraxiadive.io" con asunto que contiene el nombre del torneo
    And el event store de notificaciones registra una NotificacionEnviada

  Scenario: idempotencia end-to-end del callback P-10
    Given la inscripcion "ins-001" ya fue procesada y su NotificacionEnviada existe en el store
    When el callback P-10 se ejecuta de nuevo con inscripcion_id "ins-001"
    Then no se envia un segundo email
    And el event store sigue con exactamente una NotificacionEnviada para "ins-001"

  Scenario: atleta no encontrado no interrumpe la inscripcion
    Given el callback P-10 recibe una inscripcion con atleta_id inexistente
    When el callback se ejecuta
    Then no se lanza excepcion
    And no se envia ningun email

  Scenario: torneo no encontrado no interrumpe la inscripcion
    Given el callback P-10 recibe una inscripcion con torneo_id inexistente
    When el callback se ejecuta
    Then no se lanza excepcion
    And no se envia ningun email
