Feature: US-6.1.4 — Rediseño inicio juez + STA mm:ss + tarjeta amarilla simplificada

  Scenario: DisciplinasPage muestra título Mis asignaciones
    Given un juez logueado con disciplinas asignadas
    When accede a la página de inicio del juez
    Then el encabezado principal dice "Mis asignaciones"
    And no hay botón de Password visible

  Scenario: DisciplinasPage muestra datos del torneo antes que las asignaciones
    Given un juez logueado con torneo activo
    When accede a la página de inicio del juez
    Then aparece la sección de torneo activo con nombre y sede
    And debajo aparece la lista de disciplinas asignadas

  Scenario: formatMarca convierte STA a mm:ss con sufijo min
    Given una marca STA de 120 segundos
    When se llama a formatMarca con valor "120" y unidad "Segundos"
    Then el resultado es "2:00 min"

  Scenario: formatMarca preserva marcas dinámicas en metros
    Given una marca dinámica de 75.5 metros
    When se llama a formatMarca con valor "75.5" y unidad "Metros"
    Then el resultado es "75.5 m"

  Scenario: AtletaCard muestra STA en formato mm:ss min
    Given un atleta con AP de 90 segundos en STA
    When se renderiza AtletaCard con apDeclarado "90" y unidad "Segundos"
    Then el display de performance anunciada muestra "1:30 min"

  Scenario: StepRevision muestra etiquetas BLANCA y ROJA en los botones
    Given un juez en paso de revisión con tarjeta amarilla
    When se renderiza StepRevision
    Then el botón de tarjeta blanca tiene texto visible "BLANCA"
    And el botón de tarjeta roja tiene texto visible "ROJA"
    And no hay campos de distancia ni presets ni penalizaciones

  Scenario: StepRevision deshabilita confirmar sin selección
    Given StepRevision sin tarjeta seleccionada
    When se intenta confirmar la resolución
    Then el botón CONFIRMAR está deshabilitado

  Scenario: StepRevision habilita confirmar al seleccionar Blanca
    Given un juez selecciona tarjeta Blanca en StepRevision
    When se verifica el estado del botón CONFIRMAR
    Then el botón CONFIRMAR está habilitado
