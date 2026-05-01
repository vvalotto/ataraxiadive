Feature: US-ADJ-8.3 - Cancelacion fuerte de torneo

  Background:
    Given el organizador esta autenticado
    And existe el torneo "BA 2026"

  Scenario: Cancelar torneo esta en una zona de peligro
    When el organizador abre el panel de acciones
    Then la accion "Cancelar torneo" esta separada de las acciones normales de fase
    And usa tratamiento visual de accion destructiva

  Scenario: No se puede cancelar con un click accidental
    When el organizador toca "Cancelar torneo"
    Then se abre una confirmacion fuerte
    And no se cancela el torneo todavia

  Scenario: Confirmacion incorrecta mantiene accion bloqueada
    When el organizador toca "Cancelar torneo"
    And escribe "BA"
    Then la accion final de cancelacion permanece deshabilitada
    And el torneo sigue en su estado actual

  Scenario: Confirmacion exacta permite cancelar
    When el organizador toca "Cancelar torneo"
    And escribe "BA 2026"
    Then la accion final de cancelacion queda habilitada
    When confirma la cancelacion
    Then el frontend ejecuta la cancelacion del torneo
