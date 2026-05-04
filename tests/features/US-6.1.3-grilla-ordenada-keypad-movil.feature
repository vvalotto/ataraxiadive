Feature: US-6.1.3 — Grilla ordenada por estado + Keypad visible en móvil

  Scenario: Grilla renderizada con SIGUIENTE en primer lugar
    Given una competencia con performances en varios estados
    When se carga GrillaPage
    Then el atleta con estado SIGUIENTE aparece en la primera fila
    And el segundo atleta tiene estado EN_CURSO o PENDIENTE según disponibilidad

  Scenario: Dentro del mismo estado mantener orden original del backend
    Given dos atletas con estado SIGUIENTE
    When se ordena la grilla
    Then el orden relativo entre ambos es el original del backend

  Scenario: Orden final respeta prioridad de estados
    Given performances con estados FINALIZADA SIGUIENTE EN_CURSO REVISION y PENDIENTE
    When se renderiza GrillaPage
    Then el orden es SIGUIENTE luego EN_CURSO luego REVISION luego PENDIENTE luego FINALIZADA

  Scenario: RpSelector compactado mantiene funcionalidad de ingreso de marca
    Given un juez en paso 4 con RpSelector visible
    When ingresa la marca 75 metros con centímetros 50
    Then la marca se registra correctamente como 75.50 m
    And los presets funcionan igual que antes

  Scenario: RpSelector compactado mantiene funcionalidad en modo segundos
    Given un juez en modo segundos con RpSelector visible
    When selecciona el preset de 3 minutos
    Then el display muestra 3:00 min
    And los botones de ajuste modifican correctamente el tiempo
