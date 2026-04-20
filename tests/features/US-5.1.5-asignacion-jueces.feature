Feature: US-5.1.5 - Asignacion de jueces a disciplinas desde el panel organizador

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id "T1" esta en estado Preparacion
    And el torneo "T1" tiene las disciplinas "DNF" y "STA"
    And existen los usuarios "juez1@ataraxia.com" y "juez2@ataraxia.com" con rol JUEZ

  Scenario: asignar juez a disciplina exitosamente
    Given el organizador accede al tab "Jueces" del torneo "T1"
    When selecciona "juez1@ataraxia.com" para la disciplina "DNF"
    Then el backend recibe PUT "/torneos/T1/disciplinas/DNF/juez" con juez_id de "juez1@ataraxia.com"
    And la fila de "DNF" muestra "juez1@ataraxia.com" como juez asignado

  Scenario: reasignar juez a disciplina ya asignada
    Given la disciplina "DNF" tiene asignado a "juez1@ataraxia.com"
    When el organizador cambia el selector de "DNF" a "juez2@ataraxia.com"
    Then el backend recibe PUT "/torneos/T1/disciplinas/DNF/juez" con juez_id de "juez2@ataraxia.com"
    And la fila de "DNF" muestra "juez2@ataraxia.com"

  Scenario: disciplina sin juez asignado muestra indicador vacio
    Given la disciplina "STA" no tiene juez asignado
    When el organizador accede al tab "Jueces"
    Then la fila de "STA" muestra el selector con placeholder "Sin juez asignado"

  Scenario: error del backend muestra mensaje inline
    Given el backend devuelve 409 al asignar
    When el organizador intenta asignar un juez
    Then la UI muestra el mensaje de error del backend
    And el selector vuelve al valor anterior

  Scenario: solo aparecen usuarios con rol JUEZ en el selector
    Given existe el usuario "admin@ataraxia.com" con rol ORGANIZADOR
    When el organizador abre el selector de juez para "DNF"
    Then "admin@ataraxia.com" no aparece en la lista de opciones
    And si aparecen "juez1@ataraxia.com" y "juez2@ataraxia.com"
