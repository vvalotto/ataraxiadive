Feature: US-5.1.8 - Composicion disciplinas + competencias en Ver competencias

  Background:
    Given el organizador "org@ataraxia.com" esta autenticado con rol ORGANIZADOR

  Scenario: torneo en INSCRIPCION_ABIERTA muestra disciplinas aunque no haya competencias
    Given el torneo T1 esta en INSCRIPCION_ABIERTA con disciplinas DNF y STA
    And no existen competencias en competencia.db para T1
    When el organizador navega a "Ver competencias" de T1
    Then se muestran dos cards: una para DNF y otra para STA
    And ambas cards muestran estado "Competencia pendiente"
    And el boton "Ver auditoria" esta deshabilitado en ambas

  Scenario: torneo en EJECUCION muestra disciplinas con y sin competencia
    Given el torneo T1 esta en EJECUCION con disciplinas DNF y STA
    And existe competencia C1 para disciplina DNF en T1
    And no existe competencia para disciplina STA en T1
    When el organizador navega a "Ver competencias" de T1
    Then la card de DNF muestra "Ver auditoria" habilitado con link a C1
    And la card de STA muestra estado "Competencia pendiente"

  Scenario: pantalla vacia reemplazada por disciplinas configuradas
    Given el torneo T1 en INSCRIPCION_ABIERTA tiene disciplina DNF
    When el organizador navega a "Ver competencias"
    Then no se muestra el mensaje "Este torneo no tiene competencias configuradas"
    And si se muestra la card de DNF

  Scenario: error al cargar disciplinas muestra mensaje de error
    Given el endpoint GET /torneos/T1/disciplinas falla con 500
    When el organizador navega a "Ver competencias"
    Then se muestra un mensaje de error de carga
