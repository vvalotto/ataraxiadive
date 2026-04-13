Feature: US-4.4.2 - Flujo del juez operando offline

  Background:
    Given el juez esta autenticado
    And la disciplina activa fue pre-cargada localmente
    And el dispositivo esta offline

  Scenario: llamar atleta offline encola comando y avanza de paso
    Given el atleta esta en estado AnunciadaAP
    When el juez toca "LLAMAR ATLETA"
    Then se encola un comando tipo "llamar"
    And el flujo avanza al paso siguiente
    And el atleta queda con estado optimista "Llamada"

  Scenario: registrar resultado y tarjeta offline
    Given el atleta ya fue llamado en modo offline
    When el juez registra RP y confirma tarjeta blanca
    Then se encolan comandos "resultado" y "tarjeta"
    And la grilla muestra estado optimista final con indicador de pendiente

  Scenario: DNS offline
    Given el atleta esta pendiente en grilla
    When el juez toca "DNS — NO SE PRESENTA"
    Then se encola un comando "dns"
    And el estado optimista del atleta es DNS con pendiente

