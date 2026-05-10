Feature: US-6.6.3 — Navegación contextual y redirect post-login

  Scenario: Visitante sin login llega a / y es redirigido a /portalapnea
    Given el usuario no está autenticado
    When navega a /
    Then es redirigido a /portalapnea (no a /login)

  Scenario: Clic en "Inscribirse" sin login guarda destino y redirige al login
    Given el usuario no está autenticado en /portalapnea
    When pulsa "Inscribirse" en un torneo con id "abc-123"
    Then sessionStorage["redirectAfterLogin"] contiene "/atleta/torneos/abc-123/inscripcion"
    And es redirigido a /login

  Scenario: Post-login con destino guardado compatible con rol atleta
    Given el usuario tiene redirectAfterLogin="/atleta/torneos/abc-123/inscripcion" en sessionStorage
    When hace login como atleta exitosamente
    Then es redirigido a /atleta/torneos/abc-123/inscripcion
    And sessionStorage["redirectAfterLogin"] es eliminado

  Scenario: Post-login con destino guardado incompatible con rol organizador
    Given el usuario tiene redirectAfterLogin="/atleta/torneos/abc-123/inscripcion" en sessionStorage
    When hace login como organizador
    Then es redirigido a /organizador/torneo
    And sessionStorage["redirectAfterLogin"] es eliminado

  Scenario: Post-login sin destino guardado usa portal por defecto del rol juez
    Given no hay redirectAfterLogin en sessionStorage
    When hace login como juez
    Then es redirigido a /juez/disciplinas

  Scenario: LoginPage muestra link para volver al portal público
    Given el usuario está en /login
    Then existe un link "Ver torneos" que navega a /portalapnea
