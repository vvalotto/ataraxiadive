Feature: US-4.5.4 - Politica P-11 emails de resultados publicados

  Background:
    Given el evento ResultadosPublicados contiene 3 atletas con emails validos

  Scenario: emails enviados a todos los atletas al publicar resultados
    When se procesa la politica P-11
    Then se crean 3 aggregates Notificacion, uno por atleta
    And cada aggregate queda en estado "Enviada"
    And cada atleta recibe un email con su posicion individual y el podio

  Scenario: email personalizado con datos correctos
    When se procesa la politica P-11
    Then el email de "Martin Garcia" contiene "Posicion: #1"
    And el email de "Martin Garcia" contiene "96m"
    And el email de "Martin Garcia" contiene el podio con los 3 primeros clasificados

  Scenario: idempotencia ante ResultadosPublicados procesado dos veces
    Given los resultados "evt-res-001" ya fueron publicados y emails enviados
    When la politica P-11 recibe nuevamente el evento "evt-res-001"
    Then no se envian emails duplicados a ningun atleta
    And el store conserva exactamente una NotificacionEnviada por par evento-atleta

  Scenario: atleta sin email no interrumpe el envio a los demas
    Given uno de los 3 atletas no tiene email registrado
    When se procesa la politica P-11
    Then los 2 atletas con email reciben su notificacion
    And el atleta sin email tiene una Notificacion en estado "Fallida" con motivo "destinatario_sin_email"
    And la publicacion de resultados no se revierte

  Scenario: fallo de proveedor en un atleta continua con los demas
    Given el proveedor de email falla solo para el primer atleta
    When se procesa la politica P-11
    Then el primer atleta tiene Notificacion en estado "Fallida"
    And los atletas restantes reciben su email exitosamente

  Scenario: atleta con DNS recibe email
    Given un atleta tiene estado "DNS" en los resultados
    When se procesa la politica P-11
    Then ese atleta recibe el email con "DNS" como su resultado
    And el email incluye el podio de la disciplina
