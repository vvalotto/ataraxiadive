Feature: US-1.4.2 — Flujo Completo E2E: AP → Tarjeta
  Como juez
  Quiero ejecutar el flujo completo de una competencia (AP → llamar → resultado → tarjeta)
  Para verificar que el Event Store y los Read Models reflejan fielmente todo lo ocurrido

  Background:
    Given una competencia activa con id "comp-e2e-test"
    And 5 performances con AP registrado en la grilla

  Scenario: Flujo completo para atleta con tarjeta blanca
    Given el atleta "atleta-A" tiene AP de 60.0 metros en estado AnunciadaAP
    When el juez llama al atleta "atleta-A"
    And el juez registra resultado de 60.0 metros para "atleta-A"
    And el juez asigna tarjeta blanca a "atleta-A"
    Then la performance de "atleta-A" está en estado Ejecutada
    And el evento TarjetaAsignada existe en el Event Store para "atleta-A"

  Scenario: Flujo con DNS registrado
    Given el atleta "atleta-B" está en estado Llamada
    When el juez registra DNS para el atleta "atleta-B"
    Then la performance de "atleta-B" está en estado DNS
    And el evento DNSRegistrado existe en el Event Store para "atleta-B"

  Scenario: Corrección de resultado después de ejecutada
    Given el atleta "atleta-D" tiene tarjeta blanca asignada con resultado 55.0 metros
    When el juez corrige el resultado a 53.0 metros con motivo "error de lectura"
    Then el evento ResultadoCorregido existe en el Event Store para "atleta-D"
    And el Read Model de progreso refleja 1 performance completada

  Scenario: Flujo con black-out y distancia obligatoria
    Given el atleta "atleta-E" tiene AP de 90.0 metros en estado Llamada
    When el juez registra resultado de 90.0 metros para "atleta-E"
    And el juez asigna tarjeta roja con motivo "black-out" y distancia 45.0 metros a "atleta-E"
    Then la performance de "atleta-E" está en estado Ejecutada
    And el evento TarjetaAsignada contiene distancia_blackout 45.0 para "atleta-E"

  Scenario: El endpoint de eventos retorna la traza completa
    Given el flujo completo de las 5 performances fue ejecutado
    When el juez consulta GET /competencia/comp-e2e-test/events
    Then la respuesta tiene status 200
    And la respuesta contiene al menos 15 eventos en orden de secuencia
    And todos los eventos tienen campo event_type y occurred_at

  Scenario: Read Models consistentes con el Event Store al final del flujo
    Given el flujo completo de las 5 performances fue ejecutado
    When el juez consulta GET /competencia/comp-e2e-test/progreso
    Then ejecutadas es 3 y total es 5 y dns es 1
