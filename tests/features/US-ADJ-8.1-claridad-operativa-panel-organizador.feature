Feature: US-ADJ-8.1 - Claridad operativa del panel organizador

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR

  Scenario: Inscriptos vacios no se muestran como error
    Given la API de inscriptos responde correctamente con lista vacia
    When el organizador abre el panel de inscriptos
    Then ve "Todavia no hay inscriptos para este torneo"
    And no ve "No se pudieron cargar los inscriptos del torneo"

  Scenario: Error real de inscriptos se muestra como error
    Given la API de inscriptos falla
    When el organizador abre el panel de inscriptos
    Then ve "No se pudieron cargar los inscriptos del torneo"

  Scenario: Jueces diferencia loading, vacio y error
    Given el panel de jueces esta cargando informacion
    Then muestra "Cargando jueces..."
    When la consulta termina exitosamente sin jueces asignados
    Then muestra "Todavia no hay jueces asignados"
    When la consulta falla
    Then muestra "No se pudieron cargar los jueces"

  Scenario: Disciplina seleccionada queda asociada al detalle
    Given el torneo tiene disciplinas DNF y STA
    When el organizador selecciona DNF en el tab Ejecucion
    Then el item DNF queda destacado visualmente
    And el panel detalle queda asociado visualmente con DNF

  Scenario: Bloqueo operativo indica accion concreta
    Given DNF no tiene grilla confirmada
    When el organizador abre el detalle de ejecucion de DNF
    Then ve "Falta confirmar la grilla de DNF en el tab Grilla"
    And no ve solo un estado tecnico interno como mensaje principal

  Scenario: Lenguaje de fase es preciso
    Given el torneo esta en EJECUCION
    Then la accion visible se llama "Pasar a premiacion"
    Given el torneo esta en PREMIACION
    Then la accion visible se llama "Cerrar torneo"
