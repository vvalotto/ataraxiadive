Feature: US-6.4.3 - Routers sin imports cross-BC de infraestructura

  Scenario: resultados/api/router.py no importa infraestructura de otros BCs
    Given el archivo src/resultados/api/router.py
    When se buscan imports desde competencia.infrastructure o torneo.infrastructure
    Then no hay coincidencias

  Scenario: competencia/api/router.py no importa infraestructura de registro
    Given el archivo src/competencia/api/router.py
    When se buscan imports desde registro.infrastructure
    Then no hay coincidencias

  Scenario: Endpoint de exportacion de resultados sigue funcionando
    Given un handler de exportacion configurado para el router de resultados
    When se solicita la exportacion JSON de un torneo
    Then el endpoint retorna el payload exportable correctamente

  Scenario: Generacion de grilla sigue funcionando
    Given un handler de generacion de grilla configurado para el router de competencia
    When se solicita generar grilla para una competencia
    Then el endpoint traduce el body al comando GenerarGrillaCommand

  Scenario: Registro mantiene dependencias de upload fuera de domain y application
    Given los modulos de registro tras esta US
    When se buscan UploadFile y Path en registro/domain y registro/application
    Then no hay coincidencias
