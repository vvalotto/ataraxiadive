Feature: US-6.3.2 - Formulario de inscripcion con AP inline y adjuntos

  Background:
    Given existe una inscripcion activa de atleta para un torneo con disciplinas DYN y STA

  Scenario: Input AP aparece al seleccionar disciplina en el wizard
    Given el atleta esta en el paso 2 del formulario de inscripcion
    When selecciona la disciplina DYN
    Then el formulario muestra un input AP bajo DYN
    And el input indica la unidad esperada para DYN

  Scenario: AP invalido bloquea avance al paso 3
    Given el atleta esta en el paso 2 del formulario de inscripcion
    And selecciono STA
    And escribio "abc" como AP de STA
    When intenta avanzar al paso 3
    Then permanece en el paso 2
    And ve un error de AP invalido

  Scenario: AP vacio no bloquea avance
    Given el atleta esta en el paso 2 del formulario de inscripcion
    And selecciono DYN sin completar AP
    When intenta avanzar al paso 3
    Then avanza al paso 3 sin error de AP

  Scenario: AP declarado se persiste despues de crear la inscripcion
    Given el atleta completo el wizard con DYN y AP "50"
    When envia la inscripcion
    Then el frontend crea la inscripcion
    And declara el AP de DYN sobre la inscripcion creada

  Scenario: Apto medico se persiste en backend
    Given una inscripcion activa
    When el atleta sube un archivo PDF a apto-medico
    Then la respuesta es 200
    And la inscripcion tiene apto_medico_path no nulo

  Scenario: Constancia de pago se persiste en backend
    Given una inscripcion activa
    When el atleta sube un archivo PDF a constancia-pago
    Then la respuesta es 200
    And la inscripcion tiene constancia_pago_path no nulo

  Scenario: Archivo demasiado grande rechazado
    Given una inscripcion activa
    When el atleta intenta subir un archivo de mas de 10 MB
    Then la respuesta es 413

  Scenario: Inscripciones existentes siguen funcionando sin adjuntos
    Given una inscripcion creada antes de agregar columnas de adjuntos
    When el repositorio la recupera con el schema migrado
    Then apto_medico_path es None
    And constancia_pago_path es None
