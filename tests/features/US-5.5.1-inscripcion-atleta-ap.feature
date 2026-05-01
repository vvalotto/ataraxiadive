Feature: US-5.5.1 - Inscripcion completa del atleta y declaracion/modificacion de AP

  Background:
    Given existe el torneo "BA Open 2026" publicado con inscripciones abiertas
    And el atleta "ana@email.com" accede al portal del atleta

  Scenario: atleta completa la inscripcion con wizard de 3 pasos
    When navega a "Torneos"
    And abre el detalle del torneo "BA Open 2026"
    And presiona "Inscribirme en este torneo"
    And completa Personales, Competencia y Requisitos
    Then el sistema registra la inscripcion
    And la inscripcion queda visible en "Mis inscripciones"
    And el estado queda "pendiente de verificacion"

  Scenario: no se puede enviar inscripcion sin ambos adjuntos obligatorios
    Given el atleta esta en el paso 3 "Requisitos"
    When intenta enviar la inscripcion sin certificado medico
    Then la UI bloquea el envio
    And informa que el certificado medico es obligatorio

  Scenario: atleta declara AP desde pantalla dedicada
    Given el atleta ya esta inscripto en DNF
    And el periodo de anuncios sigue abierto
    When desde "Mis inscripciones" presiona "Declarar AP"
    And guarda AP=70 metros
    Then vuelve a "Mis inscripciones"
    And la disciplina DNF muestra el AP guardado

  Scenario: atleta modifica AP antes del cierre
    Given el atleta ya declaro AP=70 para DNF
    And el periodo de anuncios sigue abierto
    When vuelve a "Declarar AP"
    And cambia el valor a 72 metros
    Then la disciplina DNF muestra AP=72

  Scenario: AP queda solo lectura despues del cierre
    Given el atleta ya declaro AP para DNF
    And el organizador cerro el periodo de anuncios
    When el atleta abre "Mis inscripciones"
    Then la disciplina muestra chip "AP cerrado"
    And no existe CTA "Declarar AP"
