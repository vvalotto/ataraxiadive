Feature: US-6.1.1 — Fix BUG canSubmitBko + Secuencia tarjeta→marca

  Scenario: BKO en disciplina dinámica habilita botón al ingresar distancia + motivo
    Given un juez en paso BKO de una performance dinámico (ej: DYN)
    When ingresa un valor de distancia en RpSelector (ej: 50 metros)
    And selecciona un motivo de descalificación (ej: BKO_SUPERFICIE)
    Then el botón "Confirmar BKO" se habilita
    And al clickearlo, la mutation envía { distancia_blackout: 50, motivo_dq: "BKO_SUPERFICIE" }

  Scenario: BKO en STA no requiere distancia
    Given un juez en paso BKO de una performance STA
    When selecciona un motivo de descalificación
    Then el botón "Confirmar BKO" se habilita sin necesidad de ingresar distancia
    And la mutation envía { distancia_blackout: None, motivo_dq: "..." }

  Scenario: Secuencia correcta: RP → asignar tarjeta → confirmar marca
    Given un flujo iniciado en una performance nueva
    When el juez termina la performance y asigna la tarjeta (paso 5)
    Then se pasa a confirmar la marca / RP (paso 6)
    And la tarjeta no puede editarse de nuevo

  Scenario: Asignar tarjeta antes que marca preserva datos
    Given tarjeta asignada y marca confirmada
    When se guarda la performance
    Then el backend recibe { ..., tarjeta: [asignada], rp: [confirmada] } en orden correcto
