**ATARAXIADIVE**

Plataforma de Gestión de Torneos de Apnea

Estrategia de Desarrollo --- Subproyectos e Incrementos

> **Estado documental:** histórico — planificación inicial de Febrero 2026.
> Las DoDs de SP1/SP2 mencionan PostgreSQL y docker-compose, que fueron reemplazados
> por SQLite por BC (ADR-007) y desarrollo sin Docker (ADR-010) antes de iniciar la implementación.
> El alcance real de cada SP divergió parcialmente de lo descrito aquí (especialmente SP5).
> Para el estado de cada SP y los incrementos realmente implementados, ver `CLAUDE.md §14`.
> Para los planes de implementación específicos, ver `docs/plans/sp{N}/PLAN-SP{N}.md`.

  **Proyecto:**            Ataraxiadive
  ------------------------ ------------------------------------------------------------------
  **Versión:**             2.0
  **Fecha:**               Febrero 2026
  **Desarrollador:**       Victor (solo)
  **Horizonte:**           2026 --- sin fecha fija, avance sostenido
  **Modelo de trabajo:**   Subproyectos con incrementos (sin timebox fijo)
  **Cadencia:**            Cada incremento termina cuando cumple su Definición de Terminado

1. Modelo de Trabajo
====================

1.1 Estructura
--------------

El desarrollo se organiza en una jerarquía de dos niveles:

  **Nivel**   **Nombre**    **Qué es**                                                                                                **Cuándo termina**
  ----------- ------------- --------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------
  **1**       Subproyecto   Un MVP con identidad propia (nombre, objetivo, entregable final). Es una unidad de valor completa.        Cuando todos sus incrementos están terminados y el criterio de éxito del subproyecto se cumple.
  **2**       Incremento    Una porción de trabajo dentro del subproyecto que produce un avance verificable. Es la unidad de ritmo.   Cuando cumple su Definición de Terminado --- una condición concreta y observable, sin ambigüedad.

1.2 Reglas del Modelo
---------------------

-   **Sin timebox fijo.** Cada incremento toma el tiempo que toma. La presión no viene de un calendario sino de la granularidad: si un incremento está bien definido, es naturalmente pequeño.

-   **La Definición de Terminado es binaria.** Está terminado o no lo está. No hay \"casi terminado\" ni \"terminado al 80%\". Si la definición dice \"el juez registra una performance en el celular\", tiene que funcionar en el celular, no solo en el emulador.

-   **Un incremento a la vez.** No se abren múltiples incrementos en paralelo. Se termina uno, se verifica, y se empieza el siguiente. Esto evita el trabajo en progreso que se acumula sin cerrarse.

-   **Al cerrar un incremento, se evalúa.** ¿Qué funcionó? ¿Qué fue más difícil de lo esperado? ¿Hay que ajustar el siguiente incremento? Esta mini-retrospectiva informal reemplaza la retro formal del sprint.

-   **Al cerrar un subproyecto, se celebra.** Es un hito real. Se documenta el estado, se toma nota de las lecciones, y se arranca el siguiente subproyecto con energía fresca.

-   **Los incrementos de un subproyecto pueden reordenarse.** Si al avanzar descubrís que conviene cambiar el orden, se cambia. Lo que no cambia es la Definición de Terminado de cada uno.

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Principio:**                                                                                                                                                                                                                                                             |
|                                                                                                                                                                                                                                                                            |
| La disciplina del modelo no está en el calendario sino en la Definición de Terminado. Si cada incremento tiene una DdT concreta, verificable, y honesta, el ritmo se sostiene solo: terminás uno, ves el resultado, y la satisfacción de cerrarlo te impulsa al siguiente. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

2. Mapa General de Subproyectos
===============================

Cinco subproyectos, cada uno expandiendo el sistema desde el núcleo hacia la periferia:

  **\#**   **Subproyecto**       **Foco**                                                **Incrementos**   **Producto entregable**
  -------- --------------------- ------------------------------------------------------- ----------------- ----------------------------------------------------------------
  **1**    La Performance        Walking skeleton --- una performance de punta a punta   4                 Demo: juez registra performances en el celular
  **2**    La Competencia        Disciplina completa con grilla y ranking                4                 Demo: disciplina ejecutable que un apneísta reconoce como real
  **3**    El Torneo             Ciclo de vida completo con multi-rol                    5                 Sistema funcional para simular un torneo de principio a fin
  **4**    La Plataforma         Offline, notificaciones, configuración, auditoría       5                 Sistema operativo listo para un entorno real
  **5**    La Puesta en Marcha   Endurecimiento, integración, primer uso real            4                 Sistema probado en un torneo real o simulacro completo

3. Subproyectos en Detalle
==========================

+--------------------------------------------------------------------------------------------+
| **Subproyecto 1: La Performance**                                                          |
|                                                                                            |
| *Walking skeleton: una performance registrada de punta a punta por un juez en el celular.* |
+--------------------------------------------------------------------------------------------+

Este subproyecto valida la arquitectura completa con el caso más simple posible. Si al cerrarlo el flujo del juez funciona, el Event Sourcing persiste, y la pantalla responde en el celular, la base está sólida.

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 1.1: Fundación técnica**                                                                                                                                                                                                                                                |
+======================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                         |
|                                                                                                                                                                                                                                                                                      |
| El proyecto está creado con la estructura de capas (dominio / aplicación / infraestructura / presentación), la base de datos PostgreSQL tiene la tabla de eventos, y el backend responde a un health-check. Se puede ejecutar con un solo comando (docker-compose up o equivalente). |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 1.2: El dominio habla**                                                                                                                                                                                                                                                                                                                                      |
+===========================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                           |
| Las entidades Performance, Atleta y Tarjeta existen en la capa de dominio con su lógica de validación. El caso de uso RegistrarPerformance persiste un evento en el Event Store y genera la proyección en el Read Model. Se puede verificar con un test automatizado que recorre el flujo: crear performance → asignar marca → asignar tarjeta blanca → verificar estado. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 1.3: El juez ve y toca**                                                                                                                                                                                                                                                                              |
+====================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                       |
|                                                                                                                                                                                                                                                                                                                    |
| La interfaz del juez muestra un atleta (datos hardcodeados) y presenta los 6 botones del flujo (Llamar → Confirmar → Iniciar → Finalizar → Registrar marca → Asignar tarjeta). Los botones avanzan el estado visualmente en pantalla. Se ve correctamente en un celular real con botones grandes y alto contraste. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 1.4: Todo conectado**                                                                                                                                                                                                                                                                                                                                                                                             |
+================================================================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                                                   |
|                                                                                                                                                                                                                                                                                                                                                                                                                                |
| La interfaz del juez conecta con el backend. El flujo completo funciona de punta a punta: el juez ejecuta los 6 pasos en el celular, los eventos se persisten en PostgreSQL, y se puede consultar el Event Store para ver la secuencia completa de eventos de esa performance. Se puede registrar un black-out como caso alternativo. Se puede repetir el flujo para 3-5 atletas consecutivos (cargados como datos de prueba). |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **Criterio de éxito del subproyecto**   
  --------------------------------------- -----------------------------------------------------------------------------------------------------------------------
  **Demostración**                        Abrir la app en el celular, registrar 5 performances, y mostrar la traza de eventos de cada una.
  **Arquitectura validada**               El código refleja las 4 capas. Las dependencias apuntan hacia adentro. El dominio no importa nada de infraestructura.
  **Riesgo mitigado**                     Se confirma que React + PWA + PostgreSQL + Event Sourcing funcionan juntos para este caso de uso.

+------------------------------------------------------------------------------------------------+
| **Subproyecto 2: La Competencia**                                                              |
|                                                                                                |
| *Una disciplina completa: grilla, secuencia de atletas, múltiples andariveles, ranking final.* |
+------------------------------------------------------------------------------------------------+

Este subproyecto expande de una performance aislada a una disciplina completa. Es el primer producto que se puede mostrar a alguien del mundo de la apnea y que lo reconozca como un flujo real de competencia.

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 2.1: La grilla de salida**                                                                                                                                                                                                                                                                       |
+===============================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                  |
|                                                                                                                                                                                                                                                                                                               |
| Existe el concepto de Competencia (disciplina + atletas + orden). Se puede crear una grilla con 10 atletas en orden predefinido (cargada manualmente). La interfaz del juez muestra el atleta actual y el siguiente según la grilla. Al terminar una performance, avanza automáticamente al siguiente atleta. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 2.2: Dos mecánicas, un modelo**                                                                                                                                                                                                                                                                                                                                                 |
+==============================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                                                                                                                              |
| El sistema soporta dos disciplinas de prueba: STA (tiempo) y DNF (distancia). Cada una tiene su descriptor de disciplina (tipo de medición, unidad, orden de ranking). El juez ve el campo correcto según la disciplina (tiempo para STA, metros con decimales para DNF). El DNS funciona como caso alternativo: el juez marca DNS, el atleta queda descalificado, y se avanza al siguiente. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 2.3: Andariveles simultáneos**                                                                                                                                                                                                                                                                   |
+===============================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                  |
|                                                                                                                                                                                                                                                                                                               |
| La grilla soporta 2-3 andariveles. La interfaz del juez muestra los andariveles activos con el atleta de cada uno. Se pueden registrar performances en andariveles distintos sin interferencia. El modelo de datos garantiza que no hay conflicto (cada performance está asociada a un andarivel específico). |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 2.4: El ranking**                                                                                                                                                                                                                                                                           |
+==========================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                             |
|                                                                                                                                                                                                                                                                                                          |
| Al cerrar una disciplina se calcula el ranking automáticamente: ordenado por marca (mejor primero), con descalificados y DNS al final. Empates comparten posición (RF-PM-03). Existe una pantalla de resultados que muestra el ranking de la disciplina con podio destacado. Se puede ver en el celular. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **Criterio de éxito del subproyecto**   
  --------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------
  **Demostración**                        Ejecutar una competencia de STA y una de DNF con 10 atletas cada una, incluyendo DNS y black-outs. Mostrar el ranking final de cada una.
  **Validación de dominio**               Un apneísta o juez real mira la demo y reconoce el flujo como realista.
  **Riesgo mitigado**                     Se confirma que el modelo de descriptores de disciplina funciona para mecánicas distintas (tiempo vs distancia).

+-------------------------------------------------------------------------------------------------+
| **Subproyecto 3: El Torneo**                                                                    |
|                                                                                                 |
| *Ciclo de vida completo: crear torneo, inscribir atletas, preparar grillas, ejecutar, premiar.* |
+-------------------------------------------------------------------------------------------------+

Este subproyecto cierra el ciclo completo del torneo. Agrega todo lo que rodea a la competencia: inscripción, anuncios, generación automática de grillas, múltiples disciplinas, autenticación, y publicación de resultados.

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 3.1: El torneo como máquina de estados**                                                                                                                                                                                                                                                                                                                                      |
+============================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                                                                                                                                                                            |
| El organizador puede crear un torneo (nombre, lugar, fechas, disciplinas) y transicionarlo por las 6 fases (Creado → Inscripción → Preparación → Ejecución → Premiación → Cerrado). Las restricciones de transición se respetan (incluyendo retroceso Ejecución → Preparación y Cancelado desde cualquier estado). Existe autenticación básica (mail + contraseña) con rol de organizador. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 3.2: La inscripción**                                                                                                                                                                                                                                                                                                                     |
+========================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                           |
|                                                                                                                                                                                                                                                                                                                                                        |
| Los atletas pueden auto-registrarse con el formulario completo (nombre, mail, documento, categoría, disciplinas). Existe el rol de atleta con login propio. El atleta ve la lista de disciplinas del torneo y puede inscribirse en varias. El organizador ve la lista de inscriptos. La transición de Inscripción a Preparación cierra la inscripción. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 3.3: Anuncios y grillas automáticas**                                                                                                                                                                                                                                                                                                                                                |
+===================================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                      |
|                                                                                                                                                                                                                                                                                                                                                                                                   |
| Los atletas inscriptos reciben (en pantalla, no por mail aún) la indicación de registrar sus anuncios (AP). El atleta ingresa su anuncio por disciplina. El organizador genera la grilla automáticamente según la regla de cada disciplina (RF-PR-05: distancia menor→mayor, tiempo mayor→menor). La grilla distribuye atletas en andariveles. El organizador puede ajustar el orden manualmente. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 3.4: Multi-disciplina y jueces asignados**                                                                                                                                                                                                                                                                  |
+==========================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                             |
|                                                                                                                                                                                                                                                                                                                          |
| El torneo tiene las 5 disciplinas iniciales (STA, DNF, DBF, DYN, SPE). El organizador asigna un juez a cada disciplina (RF-US-04). El juez solo ve y opera las disciplinas asignadas. Se ejecutan múltiples disciplinas secuencialmente. Los atletas que no registraron anuncio no aparecen en la grilla (RF-PR-04). |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 3.5: Premiación y Overall**                                                                                                                                                                                                                                                                                                                                                                 |
+==========================================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                             |
|                                                                                                                                                                                                                                                                                                                                                                                                          |
| Al cerrar todas las disciplinas se calculan rankings por disciplina. El ranking Overall combina resultados de todas las disciplinas (RF-PM-02), inicialmente por marca absoluta (sin fórmula de puntos hasta que se defina RF-PM-01). Los resultados se publican en la plataforma y son visibles para los atletas (RF-US-05: solo resultados finales). El organizador puede descargar un resumen básico. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **Criterio de éxito del subproyecto**   
  --------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------
  **Demostración**                        Simular un torneo completo con 5 disciplinas, 20 atletas, y 3 usuarios (organizador, juez, atleta) desde la creación hasta la premiación.
  **Producto usable**                     Si el proyecto se detuviera acá, el sistema podría usarse (con limitaciones) para gestionar un torneo real con conexión a internet.
  **Riesgo mitigado**                     Se confirma que la máquina de estados, la generación de grillas, y el multi-rol funcionan integrados.

+-------------------------------------------------------------------------------+
| **Subproyecto 4: La Plataforma**                                              |
|                                                                               |
| *Modo offline del juez, notificaciones, configuración sin código, auditoría.* |
+-------------------------------------------------------------------------------+

Este subproyecto transforma el sistema de \"demo funcional\" a \"plataforma operativa\". Ataca los atributos de calidad más exigentes: offline, configurabilidad, seguridad, y comunicación.

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 4.1: El juez se desconecta**                                                                                                                                                                                                                                                                                                                                                               |
+=========================================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                            |
|                                                                                                                                                                                                                                                                                                                                                                                                         |
| La interfaz del juez funciona en modo offline: al abrir una disciplina se pre-cargan datos al dispositivo (grilla, atletas, reglas). El juez puede registrar performances sin conexión. Los eventos se almacenan en IndexedDB. Un indicador muestra el estado de conexión. Se puede poner el celular en modo avión, registrar 5 performances, reconectar, y verificar que se sincronizaron al servidor. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 4.2: El sistema habla**                                                                                                                                                                                                                                                                                                       |
+============================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                                                                                                                            |
| Se implementan notificaciones por email en los momentos clave: confirmación de inscripción, apertura de período de anuncios, recordatorio de fecha límite de anuncios (RF-NT-02), y publicación de resultados (RF-NT-04). Se usa un servicio gestionado (SendGrid, SES, o Resend). Los emails se envían realmente a direcciones de prueba. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 4.3: Configuración sin código**                                                                                                                                                                                                                                                                                                                                                      |
+===================================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                      |
|                                                                                                                                                                                                                                                                                                                                                                                                   |
| El administrador tiene un panel para configurar: disciplinas disponibles (AC-CF-01), categorías por edad y género (AC-CF-03), y reglas de tarjetas con penalizaciones (AC-CF-02). Los datos configurados se almacenan como JSONB en PostgreSQL. Se puede agregar una disciplina nueva y una categoría nueva desde el panel, y usarlas inmediatamente en un torneo nuevo sin reiniciar el sistema. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 4.4: Tarjetas y penalizaciones completas**                                                                                                                                                                                                                                                                            |
+====================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                       |
|                                                                                                                                                                                                                                                                                                                                    |
| Se implementan las tarjetas amarillas con penalizaciones configurables (RF-EJ-03). El juez puede asignar tarjeta amarilla seleccionando un código de penalización de la lista configurada. Se implementa la corrección de resultados con registro de motivo (RF-EJ-06). Los rankings se generan por categoría y género (RF-PM-05). |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 4.5: Confianza y auditoría**                                                                                                                                                                                                                                                                                                                                                                                            |
+======================================================================================================================================================================================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                                                                                                                                                                                         |
|                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| El log de auditoría es visible para el organizador: puede ver la traza completa de cada performance (AC-SG-02). Al cerrar una disciplina se genera un hash SHA-256 de todos los eventos (AC-SG-04). Después del cierre, no se pueden modificar performances. Se implementa la exportación de resultados en CSV y JSON (AC-IO-02). Se registran apto médico y constancia de pago como requisitos de inscripción (RF-IN-05, RF-IN-06). |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **Criterio de éxito del subproyecto**   
  --------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------
  **Demostración**                        Ejecutar una disciplina completa en modo avión. Configurar una disciplina nueva desde el panel. Verificar la traza de auditoría de una performance.
  **Producto operativo**                  El sistema está técnicamente listo para usarse en un torneo real, incluyendo condiciones adversas de conectividad.
  **Riesgo mitigado**                     Se confirma que el modo offline y la sincronización funcionan en un dispositivo real bajo condiciones de conectividad intermitente.

+-------------------------------------------------------------------+
| **Subproyecto 5: La Puesta en Marcha**                            |
|                                                                   |
| *Integración real, pruebas con usuarios, ajustes, primer torneo.* |
+-------------------------------------------------------------------+

Este subproyecto es la transición de \"software que funciona\" a \"software que se usa\". No agrega funcionalidad nueva significativa --- se enfoca en la robustez, la integración, y el contacto con la realidad.

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 5.1: El mundo externo**                                                                                                                                                                                                                        |
+=============================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                |
|                                                                                                                                                                                                                                                             |
| Se implementa la integración con la base de datos de la FAAS (si el protocolo está definido, RF-IG-01). Si no está disponible, se implementa una importación manual de atletas desde CSV como alternativa. Se migran datos de atletas existentes al sistema. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 5.2: Prueba de fuego simulada**                                                                                                                                                                                               |
+============================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                            |
| Se ejecuta un simulacro completo de torneo con usuarios reales de la federación (al menos un organizador y un juez reales). Se documentan todos los problemas de UX, flujo, y datos que surjan. Se genera una lista priorizada de ajustes. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 5.3: Ajustes del mundo real**                                                                                                                                                               |
+==========================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                             |
|                                                                                                                                                                                                          |
| Se implementan los ajustes prioritarios del simulacro. Se resuelven los problemas de UX del juez. Se verifican los escenarios límite que hayan surgido (atletas duplicados, anuncios incorrectos, etc.). |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Incremento 5.4: El primer torneo**                                                                                                                                                                                                                                      |
+===========================================================================================================================================================================================================================================================================+
| **Definición de Terminado:**                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                           |
| El sistema se configura para un torneo real. Se ejecuta el torneo completo con el sistema como herramienta principal (con plan B manual como respaldo, AC-DS-04). Se publican los resultados oficiales desde la plataforma. El torneo se completa sin recurrir al plan B. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **Criterio de éxito del subproyecto**   
  --------------------------------------- ----------------------------------------------------------------------------------------------
  **Demostración**                        Un torneo real completado con el sistema, resultados publicados, y feedback de los usuarios.
  **Producto en producción**              El sistema es la herramienta oficial para torneos de la federación.
  **Riesgo mitigado**                     Se confirma que el sistema funciona en condiciones reales con usuarios reales.

4. Resumen: 5 Subproyectos, 22 Incrementos
==========================================

La tabla siguiente muestra la estructura completa. Cada fila es un incremento verificable. Cada bloque de color es un subproyecto con producto entregable propio.

  **Inc.**   **Nombre**                       **Foco principal**              **Lo que se puede mostrar al terminarlo**
  ---------- -------------------------------- ------------------------------- ---------------------------------------------------
  **1.1**    Fundación técnica                Stack + estructura de capas     docker-compose up y health-check
  **1.2**    El dominio habla                 Entidades + Event Sourcing      Test del flujo de performance en consola
  **1.3**    El juez ve y toca                Interfaz mobile-first           6 botones funcionando en el celular
  **1.4**    Todo conectado                   Full-stack end-to-end           5 performances registradas desde el celular
  **2.1**    La grilla de salida              Secuencia de atletas            Juez avanza por la grilla atleta a atleta
  **2.2**    Dos mecánicas, un modelo         Descriptores de disciplina      STA (tiempo) y DNF (distancia) funcionando
  **2.3**    Andariveles simultáneos          Concurrencia de andariveles     2-3 andariveles activos sin conflicto
  **2.4**    El ranking                       Cálculo de posiciones           Ranking con podio después de cerrar disciplina
  **3.1**    Máquina de estados               Ciclo de vida del torneo        Torneo transicionando por las 6 fases
  **3.2**    La inscripción                   Auto-registro de atletas        Atleta se inscribe y ve sus disciplinas
  **3.3**    Anuncios y grillas automáticas   AP + generación de grilla       Grilla generada desde anuncios con orden correcto
  **3.4**    Multi-disciplina y jueces        5 disciplinas + asignación      Torneo con 5 disciplinas y juez asignado
  **3.5**    Premiación y Overall             Rankings combinados             Ranking Overall de un torneo completo
  **4.1**    El juez se desconecta            Offline-first + sync            5 performances en modo avión, sincronizadas
  **4.2**    El sistema habla                 Notificaciones email            Emails reales en cada transición de fase
  **4.3**    Configuración sin código         Panel admin + JSONB             Disciplina nueva creada desde el panel
  **4.4**    Tarjetas y penalizaciones        Reglas configurables            Tarjeta amarilla con código de penalización
  **4.5**    Confianza y auditoría            Log + hash + exportación        Traza completa de una performance + CSV
  **5.1**    El mundo externo                 Integración FAAS o CSV           Atletas importados al sistema
  **5.2**    Prueba de fuego simulada         Simulacro con usuarios reales   Lista de ajustes del simulacro
  **5.3**    Ajustes del mundo real           Correcciones de UX y flujo      Problemas del simulacro resueltos
  **5.4**    El primer torneo                 Uso en producción               Torneo real completado con resultados publicados

5. Ritmo y Sostenibilidad
=========================

Algunas reflexiones finales sobre cómo sostener el ritmo en un proyecto solitario:

**El incremento es tu unidad de progreso.** No midas el avance en horas trabajadas ni en líneas de código. Medilo en incrementos cerrados. Si esta semana cerraste un incremento, fue una buena semana.

**La Definición de Terminado es tu ancla.** Cuando estás solo, es fácil declarar algo \"terminado\" prematuramente. La DdT te protege de eso: es una promesa que te hacés a vos mismo sobre qué significa realmente terminar.

**Los subproyectos son puntos de respiración.** Al cerrar un subproyecto, tomate un momento para evaluar el proyecto completo. ¿Tiene sentido seguir con el plan? ¿Hay que ajustar algo? ¿Estás disfrutando el proceso? Cada subproyecto es una oportunidad legítima de replantear.

**La demo del subproyecto 2 es el punto de inflexión.** Si podés mostrar a alguien de la federación una disciplina completa ejecutándose en el celular, con ranking al final, vas a obtener feedback que vale más que cualquier especificación. Ese momento transforma el proyecto de ejercicio técnico a herramienta real.

**El código no es el único producto.** Cada subproyecto produce también conocimiento de dominio, decisiones de diseño validadas, y material que alimenta tu libro de DDD y tus clases de Ingeniería de Software. Ese valor existe aunque el software nunca llegue a producción.

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Nota:**                                                                                                                                                                                                                                    |
|                                                                                                                                                                                                                                              |
| Este documento se complementa con los Requerimientos Funcionales v1.0, los Atributos de Calidad v1.0, y la Arquitectura de Referencia v1.0. Juntos, los cuatro documentos constituyen la base para iniciar el Subproyecto 1: La Performance. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
