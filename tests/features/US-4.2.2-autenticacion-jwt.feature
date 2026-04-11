Feature: US-4.2.2 — Autenticación JWT con rutas protegidas por rol

  Background:
    Given la aplicación React está corriendo
    And el backend BC Identidad está disponible en localhost:8000

  Scenario: login exitoso como juez
    Given el usuario "juez@ataraxia.com" existe con rol juez
    When ingresa email "juez@ataraxia.com" y password correcto en la pantalla de login
    Then el store useAuthStore contiene el JWT y rol "juez"
    And el usuario es redirigido a /juez/disciplinas

  Scenario: login exitoso como organizador
    Given el usuario "org@ataraxia.com" existe con rol organizador
    When ingresa email "org@ataraxia.com" y password correcto
    Then el store useAuthStore contiene el JWT y rol "organizador"
    And el usuario es redirigido a /organizador/dashboard

  Scenario: login con credenciales inválidas
    When ingresa credenciales incorrectas en el formulario de login
    Then el formulario muestra el mensaje "Credenciales inválidas"
    And el store useAuthStore permanece vacío
    And el usuario permanece en /login

  Scenario: acceso a ruta protegida sin sesión
    Given el usuario no tiene sesión activa
    When navega directamente a /juez/disciplinas
    Then es redirigido a /login

  Scenario: acceso a ruta de rol incorrecto
    Given el usuario tiene sesión activa con rol "juez"
    When intenta navegar a /organizador/dashboard
    Then es redirigido a /juez/disciplinas

  Scenario: logout limpia la sesión
    Given el usuario tiene sesión activa
    When ejecuta logout
    Then useAuthStore queda vacío
    And el usuario es redirigido a /login
