@US-ADJ-7.1
Feature: Correccion de DNS registrado por error
  Como juez
  Quiero corregir un DNS registrado por error
  Para que el atleta pueda continuar el flujo con resultado y tarjeta

  Background:
    Given una competencia en ejecucion con una performance en estado DNS

  Scenario: Un juez corrige un DNS registrado por error
    When el juez corrige el DNS con valor RP 50 metros y motivo "Error de juez"
    Then la performance queda en estado ResultadoRegistrado
    And el event store contiene un evento ResultadoCorregidoTrasDNS

  Scenario: No se puede corregir DNS desde una performance ejecutada
    Given una performance en estado Ejecutada
    When el juez intenta corregir el resultado tras DNS
    Then se rechaza la operacion por estado invalido

  Scenario: No se puede corregir DNS desde una performance llamada
    Given una performance en estado Llamada
    When el juez intenta corregir el resultado tras DNS
    Then se rechaza la operacion por estado invalido

  Scenario: El motivo de correccion es obligatorio
    When el juez corrige el DNS sin motivo
    Then se rechaza la operacion por motivo obligatorio

  Scenario: Flujo completo desde DNS corregido hasta tarjeta blanca
    When el juez corrige el DNS con valor RP 60 metros y motivo "AP incorrecto"
    And el juez asigna tarjeta blanca
    Then la performance queda en estado Ejecutada
    And el event store contiene ResultadoCorregidoTrasDNS antes de TarjetaAsignada
