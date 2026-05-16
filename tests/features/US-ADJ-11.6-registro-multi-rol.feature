Feature: Registro multi-rol en RegistroPage
  As a user registering in AtaraxiaDive
  I want to select one or more roles (Atleta, Juez, Organizador)
  So that my account reflects all my activities from the start

  Background:
    Given the user is on /registro and is not authenticated

  Scenario: Usuario selecciona un solo rol (ATLETA) — flujo actual sin cambios
    Given the user checks only the ATLETA checkbox
    And completes nombre, apellido, email, password fields
    When the user submits the registration form
    Then the API receives roles=["ATLETA"]
    And auto-login succeeds and redirects to /atleta

  Scenario: Usuario selecciona múltiples roles — sección Juez visible
    Given the user checks ATLETA and JUEZ checkboxes
    Then the Juez data section is visible with fields numero_licencia and federacion
    When the user submits the registration form
    Then the API receives roles=["ATLETA", "JUEZ"]

  Scenario: Usuario selecciona múltiples roles — sección Organizador visible
    Given the user checks ATLETA and ORGANIZADOR checkboxes
    Then the Organizador data section is visible with field nombre_organizacion
    When the user submits the registration form
    Then the API receives roles=["ATLETA", "ORGANIZADOR"]

  Scenario: Respuesta con requires_role_selection
    Given the user checks ATLETA and ORGANIZADOR checkboxes
    And completes the registration form
    When the backend returns requires_role_selection=true
    Then the frontend redirects to /login with state requiresRoleSelection=true

  Scenario: Intento de envío sin roles seleccionados
    Given the user unchecks all role checkboxes
    Then the submit button is disabled
    And the message "Seleccioná al menos un rol" is visible

  Scenario: Campos de rol no seleccionado no se envían en el payload
    Given the user checks only ATLETA
    And the Juez section is hidden
    When the user submits the registration form
    Then the payload does not include numero_licencia or federacion
