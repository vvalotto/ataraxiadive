@US-1.3.1
Feature: Interfaz del Juez — Read Models y Endpoints
  Como juez,
  quiero consultar el estado actual de la competencia desde mi celular
  para saber quién está compitiendo ahora, quiénes son los próximos atletas
  y cuánto falta para terminar.

  Scenario: Performance actual — retorna la performance en estado Llamada
    Given una competencia con id "C001"
    And la competencia tiene una performance de "P001" en disciplina "DNF" con AP 50 metros
    And la competencia tiene una performance de "P002" en disciplina "DNF" con AP 60 metros
    And la performance de "P001" fue llamada en andarivel 1
    When el juez consulta GET /competencia/C001/performance/actual
    Then la respuesta tiene status 200
    And la performance actual corresponde al participante "P001"
    And el estado de la performance actual es "Llamada"
    And el andarivel de la performance actual es 1
    And el AP declarado es "50"

  Scenario: Proximas performances — retorna hasta 3 en orden de registro
    Given una competencia con id "C001"
    And la competencia tiene performances registradas de "P001", "P002", "P003", "P004", "P005" en disciplina "DNF" con AP 40 metros
    And la performance de "P001" fue llamada en andarivel 1
    And la performance de "P002" fue llamada en andarivel 2
    When el juez consulta GET /competencia/C001/performance/proximas
    Then la respuesta tiene status 200
    And la respuesta contiene exactamente 3 proximos atletas
    And los proximos atletas no incluyen a "P001" ni a "P002"
    And los proximos atletas incluyen a "P003", "P004" y "P005"

  Scenario: Progreso — cuenta correctamente por estado
    Given una competencia con id "C001"
    And la competencia tiene una performance de "P001" en disciplina "STA" con AP 360 segundos ejecutada con tarjeta blanca
    And la competencia tiene una performance de "P002" en disciplina "STA" con AP 300 segundos ejecutada con tarjeta blanca
    And la competencia tiene una performance de "P003" en disciplina "STA" con AP 240 segundos con DNS registrado
    And la competencia tiene una performance de "P004" en disciplina "STA" con AP 200 segundos en estado Llamada
    When el juez consulta GET /competencia/C001/progreso
    Then la respuesta tiene status 200
    And el total de performances es 4
    And las ejecutadas son 2
    And los dns son 1
    And las completadas son 3

  Scenario: Competencia sin performances — retorna estructuras vacías sin error
    Given una competencia con id "C001" sin performances registradas
    When el juez consulta GET /competencia/C001/performance/actual
    Then la respuesta tiene status 200
    And la performance actual es null
    When el juez consulta GET /competencia/C001/performance/proximas
    Then la respuesta tiene status 200
    And la lista de proximas esta vacia
    When el juez consulta GET /competencia/C001/progreso
    Then la respuesta tiene status 200
    And el total de performances es 0
