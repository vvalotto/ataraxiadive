Feature: US-5.1.1 - Crear torneo desde la UI del organizador

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR

  Scenario: crear torneo con disciplinas exitosamente
    Given el organizador accede a "/organizador/torneos/nuevo"
    When completa el nombre "BA 2026"
    And completa la sede "Club Nautico", ciudad "Buenos Aires" y pais "Argentina"
    And selecciona fechas desde "2026-10-01" hasta "2026-10-03"
    And completa entidad organizadora "FAAS" de tipo "Federacion"
    And selecciona las disciplinas "STA", "DNF" y "DYN"
    And toca "Crear Torneo"
    Then el backend recibe POST "/torneos" con los datos del torneo
    And el backend recibe PUT "/torneos/{id}/disciplinas" con "STA", "DNF" y "DYN"
    And la UI navega a "/organizador/torneo/{id}"
    And el torneo aparece con estado "Creado"

  Scenario: validacion frontend por fechas incoherentes
    Given el organizador accede a "/organizador/torneos/nuevo"
    And completa fecha de inicio "2026-10-03"
    And completa fecha de fin "2026-10-01"
    When toca "Crear Torneo"
    Then el formulario muestra el error "La fecha de fin debe ser igual o posterior a la de inicio"
    And no se realiza ninguna llamada al backend

  Scenario: validacion frontend por nombre vacio
    Given el organizador accede a "/organizador/torneos/nuevo"
    And deja el nombre del torneo vacio
    When toca "Crear Torneo"
    Then el formulario muestra el error "El nombre es obligatorio"
    And no se realiza ninguna llamada al backend

  Scenario: validacion frontend por disciplinas vacias
    Given el organizador accede a "/organizador/torneos/nuevo"
    And no selecciona disciplinas
    When toca "Crear Torneo"
    Then el formulario muestra el error "Selecciona al menos una disciplina"
    And no se realiza ninguna llamada al backend

  Scenario: error de backend al crear torneo se muestra inline
    Given el organizador accede a "/organizador/torneos/nuevo"
    And completa el formulario con datos validos
    And el backend devuelve 422 al crear el torneo
    When toca "Crear Torneo"
    Then la UI muestra el mensaje de error devuelto por el backend
    And el formulario permanece abierto con los datos ingresados

  Scenario: error de backend al asignar disciplinas permite continuar sin perder contexto
    Given el organizador accede a "/organizador/torneos/nuevo"
    And completa el formulario con datos validos
    And el backend crea el torneo con id "T1"
    And el backend devuelve 409 al asignar disciplinas
    When toca "Crear Torneo"
    Then la UI muestra el mensaje de error devuelto por el backend
    And informa que el torneo fue creado sin disciplinas
    And ofrece ir al detalle del torneo "T1"
