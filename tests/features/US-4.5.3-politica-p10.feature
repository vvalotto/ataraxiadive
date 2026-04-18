Feature: US-4.5.3 - Politica P-10 email de confirmacion de inscripcion

  Scenario: email enviado exitosamente al confirmar inscripcion
    Given el sistema recibe el evento InscripcionConfirmada para "Martin Garcia"
    And el evento tiene email "garcia@apnea.com" y torneo "Open BA 2026"
    And el evento contiene las disciplinas "DNF" y "STA"
    When se procesa la politica P-10
    Then se crea un aggregate Notificacion en estado "Enviada"
    And el email llega a "garcia@apnea.com" con asunto "Inscripcion confirmada - Open BA 2026"
    And el cuerpo del email contiene el torneo "Open BA 2026"
    And el cuerpo del email contiene las disciplinas "DNF" y "STA"

  Scenario: idempotencia ante el mismo evento procesado dos veces
    Given el evento InscripcionConfirmada "evt-reg-001" ya fue procesado exitosamente
    When la politica P-10 recibe nuevamente el evento "evt-reg-001"
    Then no se envia un segundo email
    And el store conserva exactamente una NotificacionEnviada para "evt-reg-001"

  Scenario: atleta sin email registrado
    Given el sistema recibe un evento InscripcionConfirmada sin email de atleta
    When se procesa la politica P-10
    Then se crea un aggregate Notificacion en estado "Fallida"
    And el motivo del fallo es "destinatario_sin_email"
    And la politica P-10 no lanza excepcion

  Scenario: fallo tecnico del proveedor de email
    Given el proveedor de email falla al enviar la confirmacion
    And el sistema recibe el evento InscripcionConfirmada para "Martin Garcia"
    When se procesa la politica P-10
    Then se crea un aggregate Notificacion en estado "Fallida"
    And el fallo queda registrado en el event store de notificaciones
    And la inscripcion del atleta no se revierte

  Scenario: contenido del email de confirmacion
    Given el sistema recibe el evento InscripcionConfirmada para "Martin Garcia"
    And el evento tiene torneo "Open BA 2026", fecha "2026-05-15" y sede "Club Nautico"
    And el evento contiene las disciplinas "DNF" y "STA"
    When se procesa la politica P-10
    Then el asunto del email incluye "Open BA 2026"
    And el cuerpo del email contiene "Martin Garcia"
    And el cuerpo del email contiene "2026-05-15"
    And el cuerpo del email contiene "Club Nautico"
    And el cuerpo del email contiene las disciplinas "DNF" y "STA"
