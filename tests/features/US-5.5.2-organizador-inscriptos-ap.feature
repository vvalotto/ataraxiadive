Feature: US-5.5.2 - Vista del organizador de inscriptos con estado AP

  Background:
    Given existe el torneo "BA Open 2026"
    And el organizador esta autenticado
    And hay inscripciones activas de Ana Garcia y Carlos Lopez

  Scenario: organizador ve inscriptos con datos completos
    When abre la vista de inscriptos del torneo
    Then ve apellido y nombre de cada atleta
    And ve categoria y club
    And ve las disciplinas inscriptas por atleta

  Scenario: organizador distingue AP pendiente y AP declarado
    Given Ana declaro AP para DNF
    And Carlos todavia no declaro AP para DYN
    When el organizador consulta la vista
    Then Ana aparece con estado "AP declarado" en DNF
    And Carlos aparece con estado "AP pendiente" en DYN

  Scenario: cierre del periodo bloquea nuevos anuncios y cambia el estado visible
    Given el organizador cerro el periodo de anuncios del torneo
    When consulta la vista de inscriptos
    Then las disciplinas muestran estado "AP cerrado" donde corresponda
    And la vista queda en solo lectura respecto del AP

  Scenario: inscripciones canceladas no aparecen como operativas
    Given existe una inscripcion cancelada para "pepe@email.com"
    When el organizador consulta la vista
    Then Pepe no aparece en la lista operativa de inscriptos

  Scenario: acceso con rol atleta es rechazado
    Given un usuario autenticado con rol ATLETA
    When intenta abrir la vista de inscriptos del organizador
    Then el sistema rechaza el acceso
