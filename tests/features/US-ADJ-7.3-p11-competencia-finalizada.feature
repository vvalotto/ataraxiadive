@US-ADJ-7.3
Feature: P-11 wiring al finalizar disciplina
  Como atleta inscripto
  Quiero recibir mis resultados por email cuando finaliza una disciplina
  Para conocer mi posicion sin estar presente en la competencia

  Background:
    Given una disciplina finalizada con ranking calculable para 3 atletas

  Scenario: Los atletas reciben email de resultados al finalizar la disciplina
    When se ejecuta el callback de finalizacion de competencia
    Then el store de notificaciones contiene NotificacionEnviada para los 3 atletas
    And cada email contiene nombre del atleta, posicion, RP y disciplina

  Scenario: Un atleta sin email no bloquea el envio a los demas
    Given uno de los atletas no tiene email registrado
    When se ejecuta el callback de finalizacion de competencia
    Then el store de notificaciones contiene NotificacionFallida para ese atleta
    And los otros 2 atletas reciben email normalmente

  Scenario: P-11 es idempotente al reprocesar la misma finalizacion
    Given el callback de finalizacion ya se ejecuto una vez
    When se ejecuta el callback de finalizacion de competencia
    Then no se envian emails duplicados
    And el store de notificaciones conserva una NotificacionEnviada por atleta

  Scenario: Fallo de proveedor de email no afecta la finalizacion
    Given el proveedor de email falla al enviar
    When se ejecuta el callback de finalizacion de competencia
    Then no se propaga error al callback de finalizacion
    And el fallo de envio queda registrado en notificaciones
    And el ranking calculado sigue disponible
