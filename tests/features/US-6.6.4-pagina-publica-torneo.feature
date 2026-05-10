Feature: US-6.6.4 — Página pública de torneo en ejecución

  Scenario: Visitante accede a la página del torneo sin sesión
    Given el torneo "abc-123" está en estado EJECUCION
    And el usuario no está autenticado
    When navega a /portalapnea/abc-123
    Then ve el nombre del torneo, fecha y sede
    And ve la grilla de atletas ordenada por posición
    And no se le pide autenticación

  Scenario: La página muestra una sección por disciplina activa
    Given el torneo "abc-123" tiene dos competencias activas: STA y DYN
    When navega a /portalapnea/abc-123
    Then ve dos secciones de grilla, una por disciplina

  Scenario: La grilla muestra estado y tarjeta de cada atleta
    Given la grilla de STA tiene atletas con estados PENDIENTE, EN_PROGRESO y REALIZADO
    When navega a /portalapnea/abc-123
    Then el atleta PENDIENTE aparece sin tarjeta
    And el atleta EN_PROGRESO aparece resaltado como "En curso"
    And el atleta REALIZADO muestra su tarjeta asignada

  Scenario: Botón "Ver panel" en torneos EJECUCION navega a /portalapnea/:torneoId
    Given el torneo "abc-123" está en EJECUCION en la lista pública
    When el visitante pulsa "Ver panel"
    Then navega a /portalapnea/abc-123

  Scenario: Visitante autenticado ve su portal en el header
    Given el usuario tiene sesión como atleta
    When navega a /portalapnea/abc-123
    Then el header muestra "Mi portal" en lugar de "Iniciar sesión"
