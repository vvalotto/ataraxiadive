Feature: US-4.6.3 - UI auditoria del organizador

  Background:
    Given el usuario esta autenticado como organizador
    And existe la competencia "comp-abc" con disciplina DNF
    And el atleta "Martin Garcia" tiene 3 eventos en el audit log

  Scenario: organizador navega a la pantalla de auditoria de la disciplina
    Given la disciplina esta cerrada con hash SHA-256 "a3f7c2d1e5f9"
    When accede a /organizador/competencias/comp-abc/auditoria
    Then ve la lista de atletas de la disciplina con su resultado final
    And el encabezado muestra el estado "Finalizada"
    And el hash SHA-256 es visible con accion de copiar

  Scenario: hash no visible si la disciplina sigue en ejecucion
    Given la disciplina esta en estado "EnEjecucion"
    When accede a /organizador/competencias/comp-abc/auditoria
    Then el encabezado muestra el estado "EnEjecucion"
    And el campo hash SHA-256 no aparece

  Scenario: organizador ve la traza cronologica de una performance
    When accede a /organizador/competencias/comp-abc/auditoria/ath-001
    Then ve 3 eventos en orden cronologico ascendente
    And el primer evento es "PerformanceRegistrada"
    And el ultimo evento es "TarjetaAsignada"

  Scenario: traza con correccion muestra todos los eventos
    Given la performance de "Ana Flores" incluye un evento "ResultadoCorregido"
    When accede a su traza de auditoria
    Then el evento "ResultadoCorregido" aparece despues del resultado original

  Scenario: juez no puede acceder a la auditoria del organizador
    Given el usuario esta autenticado como juez
    When intenta acceder a /organizador/competencias/comp-abc/auditoria
    Then es redirigido a la ruta /juez/disciplinas

  Scenario: copiar hash entrega feedback visual
    Given la disciplina esta cerrada con hash SHA-256 "a3f7c2d1e5f9"
    When pulsa la accion copiar hash
    Then el hash completo queda disponible para copiar
    And aparece el feedback "Copiado"
