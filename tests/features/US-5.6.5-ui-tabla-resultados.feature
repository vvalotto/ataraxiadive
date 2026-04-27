Feature: US-5.6.5 — UI tabla de ejecución de resultados por disciplina

  Background:
    Given el organizador está autenticado
    And existe el torneo "BA Open 2026" con disciplina DNF
    And la disciplina DNF tiene competencia_id "comp-dnf-001"

  Scenario: tabla muestra atletas en orden OT con datos completos (disciplina finalizada)
    Given la disciplina DNF está FINALIZADA con ranking calculado
    And Ana tiene OT=14:00, RP=70m, tarjeta Blanca, 100.00 puntos, categoría SENIOR_FEMENINO
    And Luis tiene OT=14:09, RP=56m, tarjeta Blanca, 80.00 puntos, categoría SENIOR_MASCULINO
    When el organizador abre Resultados con torneo_id del torneo
    And selecciona la disciplina DNF
    Then ve la tabla con Ana en primera fila (OT=14:00) y Luis en segunda (OT=14:09)
    And Ana muestra: Género=F, Categoría=SENIOR, RP=70 m, chip BLANCA, Puntos=100.00
    And Luis muestra: Género=M, Categoría=SENIOR, RP=56 m, chip BLANCA, Puntos=80.00

  Scenario: tabla parcial durante ejecución — atletas sin resultado muestran guión
    Given la disciplina DNF está EN EJECUCION (no FINALIZADA)
    And Ana completó su performance con RP=70m y tarjeta Blanca
    And Pedro aún no ejecutó (sin resultado)
    When el organizador abre la vista de resultados para DNF
    Then Ana muestra RP=70 m y chip BLANCA con "—" en Puntos
    And Pedro muestra "—" en RP, Tarjeta y Puntos

  Scenario: selector de disciplina cambia los datos mostrados
    Given el torneo tiene DNF y STA como disciplinas con competencias activas
    When el organizador selecciona la disciplina STA
    Then la tabla muestra los resultados de STA con tiempos en segundos

  Scenario: acceso con rol incorrecto es bloqueado
    Given un usuario autenticado con rol JUEZ
    When intenta acceder a /organizador/resultados
    Then el sistema redirige a la pantalla correspondiente a su rol

  Scenario: chip de tarjeta refleja el estado correcto
    Given la disciplina DNF está FINALIZADA
    And Carlos tiene tarjeta Roja (DQ)
    And Sofia tiene estado DNS
    When el organizador ve la tabla de DNF
    Then Carlos muestra chip ROJA
    And Sofia muestra chip DNS
