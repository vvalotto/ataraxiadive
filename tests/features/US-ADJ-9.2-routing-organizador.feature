Feature: US-ADJ-9.2 - Routing primario del organizador

  Background:
    Given existe un usuario autenticado con rol ORGANIZADOR

  Scenario: El organizador aterriza en una home clara
    When entra a la aplicacion
    Then el sistema lo redirige a la home del organizador
    And no a una pantalla detalle de torneo

  Scenario: Las secciones primarias cuelgan del shell compartido
    Given el organizador esta dentro del panel
    When navega a Panel, Grilla, Resultados, Jueces, Torneo y Audit Log
    Then cada seccion se abre dentro del shell compartido
    And la navbar primaria sigue visible

  Scenario: Las vistas detalle no reemplazan la navegacion principal
    Given el organizador abre una vista contextual de torneo o auditoria
    Then la navegacion primaria sigue disponible
    And puede ir a otra seccion principal sin depender de "Volver al dashboard"

  Scenario: Las rutas historicas redirigen o conservan compatibilidad
    Given el organizador abre una ruta historica del panel
    When esa ruta fue reemplazada por una ruta primaria nueva
    Then el sistema redirige a la ubicacion aprobada
    And no pierde el contexto del shell
