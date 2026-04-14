Feature: Aggregate Notificacion con idempotencia

  Scenario: solicitud de envio nueva
    Given el event store de notificaciones no tiene eventos para evento_fuente_id "reg-001"
    When se ejecuta SolicitarEnvio con evento_fuente_id "reg-001" y destinatario "juan@example.com"
    Then el aggregate Notificacion emite NotificacionSolicitada
    And el evento queda persistido en el event store de notificaciones

  Scenario: solicitud duplicada con envio exitoso previo
    Given el event store de notificaciones tiene NotificacionEnviada para evento_fuente_id "reg-001"
    When se ejecuta SolicitarEnvio con evento_fuente_id "reg-001" nuevamente
    Then el aggregate Notificacion no emite nuevos eventos
    And no se realiza ningun envio al canal externo

  Scenario: reintento permitido despues de un fallo definitivo
    Given el event store de notificaciones tiene NotificacionFallida para evento_fuente_id "reg-002"
    When se ejecuta SolicitarEnvio con evento_fuente_id "reg-002" y destinatario "ana@example.com"
    Then el aggregate Notificacion emite NotificacionSolicitada como reintento

  Scenario: destinatario con email invalido
    When se ejecuta SolicitarEnvio con destinatario email "no-es-un-email"
    Then el aggregate Notificacion rechaza la solicitud por validacion de dominio
    And no emite ningun evento

  Scenario: registro de envio exitoso
    Given el aggregate Notificacion esta en estado Solicitada
    When se ejecuta RegistrarEnvioExitoso
    Then el aggregate Notificacion emite NotificacionEnviada
    And la notificacion queda en estado terminal

  Scenario: registro de fallo definitivo
    Given el aggregate Notificacion esta en estado Solicitada
    When se ejecuta RegistrarFallo con motivo "SMTP connection refused"
    Then el aggregate Notificacion emite NotificacionFallida con ese motivo
    And la notificacion queda en estado terminal
