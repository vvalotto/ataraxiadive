**ATARAXIADIVE**

Plataforma de Gestión de Torneos de Apnea

Arquitectura de Referencia - Propuesta Inicial

  ---------------- -------------------------------------------------------------
  **Proyecto:**    Ataraxiadive
  **Versión:**     1.0 - Propuesta inicial
  **Fecha:**       Febrero 2026
  **Dimensión:**   Arquitectura de Referencia
  **Insumos:**     Requerimientos Funcionales v1.0 + Atributos de Calidad v1.0
  ---------------- -------------------------------------------------------------

Este documento presenta la propuesta inicial de arquitectura de alto nivel para el sistema Ataraxiadive. Cada decisión arquitectónica se deriva directamente de los requerimientos funcionales y atributos de calidad relevados en las dos dimensiones anteriores del análisis. El documento está organizado en secciones que abordan progresivamente desde la visión general hasta las decisiones estructurales concretas.

1\. Drivers Arquitectónicos Priorizados

Del cruce entre los requerimientos funcionales y los atributos de calidad emergen los siguientes drivers arquitectónicos, ordenados por impacto en las decisiones de diseño:

  --------------- ------------------------------------------------------ ------------------------------------------ -------------------------------------------------------------------
  **Prioridad**   **Driver**                                             **Origen**                                 **Impacto**
  **1**           Operación offline del juez durante la competencia      AC-DS-02, AC-DS-03, AC-CN-01               Define la estrategia de sincronización y el modelo de datos local
  **2**           Interfaz del juez mobile-first bajo estrés             AC-US-01, AC-US-02, AC-US-03, AC-RD-01     Define el framework de UI y el diseño de interacción crítica
  **3**           Configurabilidad multinivel sin cambios de código      AC-CF-01 a AC-CF-05, RF-EJ-03, RF-IN-01    Define el modelo de metadatos y el motor de reglas
  **4**           Integridad y auditabilidad de resultados               AC-SG-02, AC-SG-04, AC-CN-03               Define la estrategia de persistencia y el modelo de eventos
  **5**           Ciclo de vida del torneo como máquina de estados       RF-GT-05, RF-GT-04                         Define el flujo de negocio central y las transiciones permitidas
  **6**           Integración con sistemas externos bajo incertidumbre   RF-IG-01 a RF-IG-04, AC-IO-01 a AC-IO-04   Define la estrategia de acoplamiento débil en los bordes
  --------------- ------------------------------------------------------ ------------------------------------------ -------------------------------------------------------------------

2\. Visión General de la Arquitectura

2.1 Estilo Arquitectónico

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                                                                                                                                                                            |
| Arquitectura modular por capas con separación explícita entre el núcleo de dominio, los servicios de aplicación, y los adaptadores de infraestructura. El sistema se estructura siguiendo los principios de Arquitectura Hexagonal (Ports & Adapters), donde el dominio de la competencia es el centro y todo lo demás (UI, base de datos, integraciones) son adaptadores intercambiables. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver:**                                                                                                                                                                                                                                      |
|                                                                                                                                                                                                                                                  |
| La combinación de configurabilidad (AC-CF-01 a AC-CF-05), integración incierta (RF-IG-01 a RF-IG-04), y la necesidad futura de nuevos tipos de disciplinas (AC-CF-05) requiere un núcleo de dominio estable y desacoplado de la infraestructura. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

La elección de Arquitectura Hexagonal responde a una necesidad concreta: el dominio de la apnea competitiva tiene reglas propias que cambian según la federación (AIDA, CMAS) y que el sistema debe absorber sin modificar la estructura. Al aislar el dominio del resto, las reglas de tarjetas, penalizaciones, cálculo de puntos y disciplinas pueden evolucionar independientemente de cómo se persistan los datos o cómo se presente la interfaz.

2.2 Estructura de Capas

El sistema se organiza en cuatro capas concéntricas, donde las dependencias fluyen siempre hacia adentro:

  ---------------------- ------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Capa**               **Responsabilidad**                                     **Contenido**
  **Dominio (centro)**   Reglas de negocio puras, independientes de tecnología   Entidades (Torneo, Atleta, Performance, Disciplina), Value Objects (AP, Tarjeta, Penalización), Reglas de validación, Máquina de estados del torneo
  **Aplicación**         Orquestación de casos de uso y flujos de trabajo        Servicios de aplicación (InscribirAtleta, RegistrarPerformance, GenerarGrilla), Comandos y Queries, Políticas de notificación
  **Infraestructura**    Implementaciones técnicas concretas                     Repositorios (persistencia), Servicios de notificación (mail, push), Clientes de integración (BD externa FAZ), Sincronización offline
  **Presentación**       Interfaces de usuario adaptadas por rol                 Interfaz del Juez (mobile-first, offline-capable), Portal del Atleta (registro, anuncios, resultados), Panel del Organizador (gestión, grillas, configuración), Panel del Administrador (configuración global)
  ---------------------- ------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

3\. Modelo de Dominio de Alto Nivel

El modelo de dominio se organiza alrededor de los agregados principales que emergen del análisis funcional. Cada agregado es una frontera de consistencia transaccional.

3.1 Agregados Principales

  ------------------- --------------------------- ------------------------------------------------------------------------------------ ----------------------------------------------------------------------------------
  **Agregado**        **Raíz**                    **Entidades/VOs contenidos**                                                         **Responsabilidad**
  **Torneo**          Torneo                      Fase, Disciplina seleccionada, Entidad organizadora                                  Ciclo de vida del torneo, transiciones de fase, configuración de disciplinas
  **Inscripción**     Inscripción                 Datos del atleta, Categoría, Disciplinas, Constancia de pago, Apto médico            Registro del atleta en un torneo específico con sus disciplinas
  **Competencia**     Competencia                 Grilla de salida, Slot de competencia, OT                                            Planificación de una disciplina: orden de salida, andariveles, tiempos oficiales
  **Performance**     Performance                 Marca (tiempo/distancia), Tarjeta, Penalización, Estado (DNS, black-out, válida)     Registro atómico de cada performance individual de un atleta
  **Resultado**       Resultado de disciplina     Ranking por categoría, Puntos, Posición                                              Cálculo y publicación de resultados por disciplina y overall
  **Configuración**   Configuración del sistema   Disciplina, Categoría, Regla de tarjeta, Código de penalización, Fórmula de puntos   Metadatos configurables del sistema, gestionados por el administrador
  ------------------- --------------------------- ------------------------------------------------------------------------------------ ----------------------------------------------------------------------------------

3.2 Máquina de Estados del Torneo

El torneo es una máquina de estados con transiciones controladas por el organizador (RF-GT-05). Las transiciones permitidas son:

  ------------------------- --------------------- ----------------------------------------------------------------------
  **Estado origen**         **Estado destino**    **Condición / Acción**
  **Creado**                Inscripción Abierta   Organizador habilita inscripción. Se notifica apertura.
  **Inscripción Abierta**   Preparación           Organizador cierra inscripción. Se notifica a atletas para anuncios.
  **Preparación**           Ejecución             Todos los anuncios registrados o plazo vencido. Grillas generadas.
  **Ejecución**             Preparación           Retroceso permitido si se detecta error (RF-GT-05: sí).
  **Ejecución**             Premiación            Todas las disciplinas cerradas. Rankings calculados.
  **Premiación**            Cerrado               Organizador confirma cierre. Resultados publicados.
  **Cualquiera**            Cancelado             Organizador cancela. Se conserva toda la información (RF-GT-04).
  ------------------------- --------------------- ----------------------------------------------------------------------

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Trade-off:**                                                                                                                                                                                                                                                                                                                                                                       |
|                                                                                                                                                                                                                                                                                                                                                                                      |
| Permitir el retroceso de Ejecución a Preparación (RF-GT-05) introduce complejidad: ¿qué pasa con las performances ya registradas en disciplinas que ya se ejecutaron? Decisión propuesta: el retroceso solo es posible si no hay disciplinas con performances registradas, o si el organizador confirma explícitamente que se descartarán los resultados de disciplinas no cerradas. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

4\. Estrategia Offline-First para la Interfaz del Juez

*Este es el driver arquitectónico de mayor impacto. La combinación de conectividad precaria (AC-DS-02), operación offline obligatoria (AC-DS-03), y garantía de persistencia (AC-CN-01) exige una estrategia deliberada.*

4.1 Modelo Propuesto

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                                                                                                            |
|                                                                                                                                                                                                                                                                                                                         |
| La interfaz del juez opera como una aplicación offline-first (Progressive Web App o aplicación nativa ligera). Toda la lógica de registro de performances se ejecuta localmente. Los datos se persisten primero en almacenamiento local del dispositivo y luego se sincronizan con el servidor cuando hay conectividad. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

El flujo de operación del juez sigue este patrón:

  ----------------------- ------------------ ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Paso**                **Ubicación**      **Descripción**
  **1. Pre-carga**        Servidor → Local   Al abrir una disciplina, se descarga al dispositivo: la grilla de salida, los datos de atletas, y las reglas configuradas (tarjetas, penalizaciones).
  **2. Operación**        Local              El juez opera enteramente en local: llama atleta, confirma, inicia, finaliza, registra. Cada acción se persiste en almacenamiento local como evento.
  **3. Confirmación**     Local              El juez recibe confirmación visual inmediata (AC-CN-02) desde los datos locales, sin depender del servidor.
  **4. Sincronización**   Local → Servidor   Cuando hay conectividad, los eventos locales se envían al servidor. El servidor valida y persiste. En caso de conflicto, se aplica last-write-wins por andarivel (AC-CN-04: no hay conflicto entre andariveles).
  **5. Reconciliación**   Servidor → Local   El servidor confirma la recepción. Si hay discrepancias, se notifica al juez.
  ----------------------- ------------------ ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

4.2 Tecnología de Almacenamiento Local

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                                             |
|                                                                                                                                                                                                                                                          |
| Uso de IndexedDB (vía una capa de abstracción como Dexie.js) para almacenamiento estructurado en el navegador, o SQLite embebido si se opta por aplicación nativa. La elección concreta dependerá de si se implementa como PWA o como aplicación nativa. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Trade-off:**                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| PWA vs. Aplicación Nativa: una PWA permite un único código base y despliegue vía URL (simplifica distribución), pero tiene limitaciones de almacenamiento local y acceso a hardware. Una app nativa (React Native, Flutter) da más control sobre el almacenamiento y la experiencia offline, pero requiere distribución por stores. Recomendación inicial: PWA, con migración a nativa solo si las limitaciones de almacenamiento o rendimiento lo justifican. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

5\. Estrategia de Persistencia y Auditoría

5.1 Event Sourcing para la Competencia

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                            |
|                                                                                                                                                                                                                                         |
| El registro de la competencia (fase de Ejecución) se implementa con Event Sourcing: cada acción del juez se persiste como un evento inmutable. El estado actual de cada performance se reconstruye a partir de la secuencia de eventos. |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver:**                                                                                                                                                                                                                                                             |
|                                                                                                                                                                                                                                                                         |
| AC-SG-02 (log de auditoría inalterable) + AC-CN-03 (reconstruir estado desde log) + AC-SG-04 (protección contra manipulación post-cierre). El Event Sourcing satisface los tres requerimientos como un efecto natural de su diseño, no como una funcionalidad agregada. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Los eventos del dominio de competencia incluyen:

  --------------------------- -------------------------------------------------------------------------------------- ------------------------------------------------------
  **Evento**                  **Datos**                                                                              **Emitido cuando**
  **AtletaLlamado**           competencia\_id, atleta\_id, andarivel, OT, timestamp                                  El juez llama al siguiente atleta
  **PresenciaConfirmada**     competencia\_id, atleta\_id, timestamp                                                 El juez confirma que el atleta se presentó
  **DNSRegistrado**           competencia\_id, atleta\_id, timestamp                                                 El atleta no se presenta (descalificación inmediata)
  **PerformanceIniciada**     competencia\_id, atleta\_id, timestamp                                                 El juez inicia el cronómetro de la performance
  **PerformanceFinalizada**   competencia\_id, atleta\_id, timestamp, marca\_tiempo                                  El juez detiene el cronómetro
  **ResultadoRegistrado**     competencia\_id, atleta\_id, tipo (tiempo/distancia), valor, decimales                 El juez ingresa la marca final
  **TarjetaAsignada**         competencia\_id, atleta\_id, tarjeta (blanca/amarilla/roja), codigo\_penalizacion?     El juez califica la performance
  **BlackOutRegistrado**      competencia\_id, atleta\_id, distancia\_alcanzada, timestamp                           Se registra un black-out con la distancia lograda
  **ResultadoCorregido**      competencia\_id, atleta\_id, campo, valor\_anterior, valor\_nuevo, motivo, timestamp   El juez corrige un resultado (RF-EJ-06)
  --------------------------- -------------------------------------------------------------------------------------- ------------------------------------------------------

5.2 Persistencia Dual

El sistema mantiene dos representaciones de los datos de competencia:

  ----------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Representación**            **Descripción**
  **Event Store (inmutable)**   Secuencia completa de eventos. Nunca se modifica ni se elimina. Fuente de verdad para auditoría y reconstrucción. Satisface AC-SG-02 y AC-CN-03.
  **Read Model (proyección)**   Tabla materializada con el estado actual de cada performance. Se reconstruye desde los eventos. Optimizada para consultas rápidas del juez, ranking, y resultados.
  ----------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Trade-off:**                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Event Sourcing agrega complejidad al modelo de datos y requiere disciplina para mantener las proyecciones sincronizadas. Sin embargo, para el volumen de Ataraxiadive (100 atletas, \~500 performances por torneo) el costo es bajo y los beneficios (auditoría, reconstrucción, protección contra manipulación) son significativos. Para las fases no críticas (inscripción, preparación), se puede usar CRUD tradicional sin Event Sourcing. |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

6\. Motor de Configuración

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                          |
|                                                                                                                                                                                                                                       |
| El sistema implementa un motor de configuración en dos niveles: configuración global del sistema (administrador) y configuración por torneo (organizador). Las reglas de negocio configurables se modelan como datos, no como código. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver:**                                                                                                                                                                                                                                         |
|                                                                                                                                                                                                                                                     |
| El patrón de configurabilidad es el driver más transversal del sistema: disciplinas (RF-GT-02), categorías (RF-IN-01), tarjetas (RF-EJ-03), penalizaciones (RF-EJ-04), fórmula de puntos (RF-PM-01), y futuras mecánicas de disciplinas (AC-CF-05). |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

6.1 Modelo de Configuración en Cascada

  ----------------------------------------- ----------------- --------------------------------------------- ------------
  **Elemento configurable**                 **Nivel**         **Quién configura**                           **Origen**
  **Disciplinas disponibles**               Global            Administrador                                 AC-CF-01
  **Categorías (edad, género)**             Global            Administrador                                 AC-CF-03
  **Reglas de tarjetas y penalizaciones**   Global            Administrador (según federación)              AC-CF-02
  **Códigos de penalización**               Global            Administrador (según federación)              RF-EJ-04
  **Fórmula de cálculo de puntos**          Por torneo        Organizador                                   AC-CF-04
  **Disciplinas del torneo**                Por torneo        Organizador (selecciona de las disponibles)   RF-GT-02
  **OT por disciplina**                     Por competencia   Juez de competencia                           RF-PR-08
  ----------------------------------------- ----------------- --------------------------------------------- ------------

6.2 Estrategia para Reglas Extensibles

Para absorber la incorporación futura de disciplinas con mecánicas nuevas (AC-CF-05), cada disciplina se modela con un descriptor que define su mecánica:

  ------------------------------------- ---------------------------------------------------------------
  **Atributo del descriptor**           **Ejemplo**
  **Tipo de medición**                  tiempo (STA, SPE) o distancia (DNF, DYN, DBF)
  **Unidad**                            segundos, metros con decimales (RF-EJ-08)
  **Orden de salida**                   menor a mayor en todas las disciplinas (RF-PR-05)
  **Permite andariveles simultáneos**   sí/no, con cantidad máxima
  **Reglas de tarjeta aplicables**      conjunto de tarjetas y penalizaciones válidas
  **Protocolo de superficie**           registra solo efecto (RF-EJ-10)
  ------------------------------------- ---------------------------------------------------------------

Este enfoque permite que el administrador defina una nueva disciplina describiendo su mecánica a través de estos atributos, sin necesidad de cambiar código. Si en el futuro aparece una mecánica completamente nueva (ni tiempo ni distancia), el descriptor se extiende.

7\. Diseño de la Interfaz del Juez

*La interfaz del juez es el punto de máxima tensión del sistema: máxima criticidad funcional (performance irrepetible), mínima tolerancia a errores (datos oficiales), condiciones físicas adversas (agua, sol), y dispositivo limitado (celular). Cada decisión de diseño aquí tiene consecuencias directas.*

7.1 Principios de Diseño

  ----------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------
  **Principio**                             **Justificación**
  **Máximo 6 toques por performance**       AC-US-02. El flujo completo: Llamar (1) → Confirmar presencia (2) → Iniciar (3) → Finalizar (4) → Ingresar marca (5) → Asignar tarjeta (6).
  **Botones grandes, alto contraste**       AC-US-03. Operación con manos mojadas y sol directo en pantalla. Mínimo 48x48px por target táctil, idealmente 64px+.
  **Feedback inmediato visual y háptico**   AC-CN-02 + AC-RD-01 (500ms). Cada acción produce confirmación visual instantánea y vibración del dispositivo.
  **Sin navegación entre pantallas**        El flujo del juez es lineal y predecible. Una sola pantalla con estados progresivos, no múltiples páginas.
  **Estado del atleta siempre visible**     El juez debe ver en todo momento: nombre del atleta, anuncio (AP), andarivel, y estado actual del flujo.
  **Modo offline transparente**             AC-DS-03. El juez no debe percibir la diferencia entre operación online y offline. Un indicador discreto muestra el estado de conexión.
  ----------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------

7.2 Flujo de Interacción del Juez

El juez ve una pantalla principal que muestra el atleta actual y el siguiente en la grilla. El flujo es una secuencia lineal de estados:

  --------------------- ------------------------------------------------ ---------------------------------------------------------------------------------------------------------------- --------------
  **Paso**              **Acción del juez**                              **Sistema responde**                                                                                             **Toque \#**
  **Llamar**            Toca botón LLAMAR                                Muestra datos del atleta (nombre, AP, categoría). Inicia espera.                                                 1
  **Confirmar / DNS**   Toca PRESENTE o DNS                              Si presente: habilita inicio. Si DNS: registra descalificación (RF-EJ-02), pasa al siguiente.                    2
  **Iniciar**           Toca INICIAR                                     Marca timestamp de inicio. Muestra cronómetro visual (referencia, no oficial).                                   3
  **Finalizar**         Toca FINALIZAR                                   Marca timestamp de fin. Abre campo de marca si es distancia.                                                     4
  **Registrar marca**   Ingresa valor (si distancia) o confirma tiempo   Muestra marca registrada. Habilita calificación.                                                                 5
  **Calificar**         Toca tarjeta (blanca/amarilla/roja)              Si amarilla/roja: solicita código de penalización. Registra. Muestra confirmación. Avanza al siguiente atleta.   6
  --------------------- ------------------------------------------------ ---------------------------------------------------------------------------------------------------------------- --------------

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Nota:**                                                                                                                                                                                                                                                                                     |
|                                                                                                                                                                                                                                                                                               |
| Para el caso de black-out (RF-EJ-07), el flujo se bifurca después del paso 4: en lugar de registrar una marca válida, el juez toca BLACK-OUT, ingresa la distancia alcanzada, y el sistema registra automáticamente como tarjeta roja. Esto mantiene el flujo dentro de los 6 toques máximos. |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

8\. Stack Tecnológico Propuesto

*Las decisiones tecnológicas están condicionadas por los drivers de escala modesta (AC-ES-01: 4 torneos/año, 50 usuarios concurrentes), operación offline (AC-DS-03), y mantenibilidad a largo plazo (AC-MT-01 pendiente, AC-MT-03: cambios cada 2 años).*

8.1 Propuesta Tecnológica

  -------------------------- ------------------------------------------------ ------------------------------------------------------------------------------------------- ------------------------------------------
  **Capa**                   **Tecnología propuesta**                         **Justificación**                                                                           **Alternativa viable**
  **Frontend**               React + PWA (Service Workers)                    Offline-first nativo, ecosistema maduro, una sola base de código para mobile y desktop.     Flutter Web, Vue.js + PWA
  **Estado local (juez)**    IndexedDB vía Dexie.js                           Almacenamiento estructurado en navegador, soporte transaccional, persistencia robusta.      SQLite vía wa-sqlite (WASM)
  **Sincronización**         Background Sync API + Cola de eventos            Sincronización automática cuando se recupera conectividad.                                  Custom sync con Service Worker
  **Backend**                Node.js (Express/Fastify) o Python (FastAPI)     API REST/GraphQL. Ecosistema amplio, despliegue simple en la nube.                          Go, .NET
  **Base de datos**          PostgreSQL                                       Event Store + Read Models en la misma DB. Soporte JSONB para configuración flexible.        MySQL, MongoDB (solo para configuración)
  **Event Store**            Tabla de eventos en PostgreSQL                   Volumen bajo (\~500 eventos/torneo). No justifica un event store dedicado (EventStoreDB).   EventStoreDB (si escala crece)
  **Notificaciones email**   SendGrid, Amazon SES, o Resend                   Servicios gestionados con alta entregabilidad.                                              SMTP propio (no recomendado)
  **Notificaciones push**    Firebase Cloud Messaging (FCM)                   Integración nativa con PWA, gratis para el volumen esperado.                                OneSignal, Web Push API directo
  **Hosting**                Servidor en la nube (AWS, GCP, o DigitalOcean)   AC-DS-01 indica que debe estar en la nube. Escala modesta permite un solo servidor.         Railway, Render, Fly.io
  **Autenticación**          JWT + refresh tokens                             RF-US-03: mail + contraseña. Stateless, compatible con offline.                             Auth0, Firebase Auth
  -------------------------- ------------------------------------------------ ------------------------------------------------------------------------------------------- ------------------------------------------

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Trade-off:**                                                                                                                                                                                                                                                                                                                                                                                                        |
|                                                                                                                                                                                                                                                                                                                                                                                                                       |
| La escala de Ataraxiadive (50 usuarios, 4 torneos/año) no justifica microservicios ni infraestructura compleja. Un monolito modular bien estructurado (con la separación de capas de la sección 2) es más apropiado: más simple de desplegar, depurar, y mantener. La modularidad interna permite extraer servicios en el futuro si la escala lo requiere, sin el costo operacional de distribuirlos desde el inicio. |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

9\. Modelo de Seguridad

9.1 Roles y Permisos Contextuales

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                                                                                          |
|                                                                                                                                                                                                                                                                                                       |
| El modelo de permisos es contextual: un usuario tiene un rol base (administrador, organizador, juez, atleta), pero sus permisos efectivos dependen del contexto (torneo, disciplina). Un juez asignado a la disciplina STA de un torneo específico solo puede operar en esa disciplina de ese torneo. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  ------------------- ------------------------------------------------------ --------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------
  **Rol**             **Scope de permisos**                                  **Puede crear**                                                 **Restricciones clave**
  **Administrador**   Global del sistema                                     Usuarios (organizador, juez), disciplinas, categorías, reglas   No opera torneos directamente
  **Organizador**     Un torneo específico (RF-US-01: solo uno)              Torneo, grillas, transiciones de fase                           No puede modificar resultados de performances
  **Juez**            Disciplinas asignadas dentro de un torneo (RF-US-04)   Performances, tarjetas, correcciones                            Solo ve resultados finales de disciplinas no asignadas (AC-SG-03). Solo modifica dentro de disciplinas asignadas.
  **Atleta**          Su propia información                                  Inscripción, anuncios                                           Solo ve resultados finales publicados (RF-US-05)
  ------------------- ------------------------------------------------------ --------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------

9.2 Protección de Integridad de Resultados

La protección contra manipulación (AC-SG-04) se implementa en tres niveles:

  -------------------------- ------------------------------------------------------------------------------------------------------------------ --------------------------------------------------------------------------------------------------------
  **Nivel**                  **Mecanismo**                                                                                                      **Efecto**
  **Evento inmutable**       Event Store append-only. Los eventos no se modifican ni eliminan.                                                  Cualquier cambio queda registrado como un nuevo evento (ResultadoCorregido), preservando el historial.
  **Cierre de disciplina**   Una vez cerrada la disciplina, el sistema bloquea la escritura de nuevos eventos de performance.                   Ningún rol puede modificar resultados después del cierre.
  **Firma de cierre**        Al cerrar una disciplina, se genera un hash (SHA-256) de todos los eventos. Este hash se registra con el cierre.   Permite verificar post-facto que los eventos no fueron alterados.
  -------------------------- ------------------------------------------------------------------------------------------------------------------ --------------------------------------------------------------------------------------------------------

10\. Estrategia de Integración

*La zona de integración es la de mayor incertidumbre del proyecto (RF-IG-01 a RF-IG-04: todos pendientes). La estrategia arquitectónica debe absorber esta incertidumbre.*

10.1 Principio: Anti-Corruption Layer

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Decisión arquitectónica:**                                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                                            |
| Cada integración externa se encapsula detrás de un puerto (interfaz) del dominio con su correspondiente adaptador de infraestructura. El dominio nunca depende directamente de un sistema externo. Si el sistema externo cambia, solo cambia el adaptador. |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  --------------------------------- -------------------------------------------------------------- ---------------------------------------------------------------------------------- -------------------------
  **Integración**                   **Puerto (interfaz)**                                          **Adaptador inicial**                                                              **Estado**
  **BD externa de atletas (FAZ)**   RepositorioAtletasExterno: buscarPorDocumento()                Adaptador placeholder (retorna vacío). Se implementa cuando se defina protocolo.   Pendiente (RF-IG-01)
  **Exportación de resultados**     ExportadorResultados: exportar(torneo, formato)                Adaptador CSV/JSON. Se extiende para AIDA/CMAS cuando se defina formato.           Parcial (AC-IO-02)
  **Notificaciones email**          ServicioNotificacion: enviar(destinatario, plantilla, datos)   Adaptador SendGrid/SES.                                                            Definido (RF-NT-01)
  **Notificaciones push**           ServicioNotificacionPush: enviar(dispositivo, mensaje)         Adaptador FCM.                                                                     Pendiente (AC-IO-04)
  **Cronometraje electrónico**      SensorCronometraje: onMarcaRegistrada(callback)                Sin implementación. Puerto definido para futura integración.                       Futuro (AC-IO-01)
  **Pagos**                         Sin puerto definido. Actualmente es constancia manual.         N/A                                                                                No requerido (AC-IO-03)
  --------------------------------- -------------------------------------------------------------- ---------------------------------------------------------------------------------- -------------------------

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Trade-off:**                                                                                                                                                                                                                                                                                                                         |
|                                                                                                                                                                                                                                                                                                                                        |
| Definir los puertos ahora (aunque algunos adaptadores estén vacíos) tiene un costo mínimo pero un beneficio alto: cuando se concrete la integración con la base de datos de la FAZ (RF-IG-01) o el cronometraje electrónico (AC-IO-01), solo habrá que implementar un adaptador nuevo sin tocar el dominio ni la lógica de aplicación. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

11\. Decisiones Pendientes y Riesgos

Las siguientes decisiones no pueden tomarse aún porque dependen de información pendiente de resolución. Cada una tiene una estrategia de mitigación para avanzar sin bloqueo.

  ----------------------------------------- ---------------------------------------- ----------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------
  **Decisión pendiente**                    **Bloqueada por**                        **Impacto si no se resuelve**                         **Mitigación propuesta**
  **Fórmula de cálculo de puntos**          RF-PM-01 (pendiente, regla de negocio)   No se pueden generar rankings Overall (RF-PM-02)      Implementar ranking por marca absoluta como default. La fórmula se agrega como configuración por torneo cuando se defina.
  **Códigos de penalización**               RF-EJ-04 (pendiente)                     El juez no puede asignar penalizaciones específicas   Implementar tarjeta roja genérica sin código. Los códigos se agregan como configuración cuando se definan.
  **Protocolo de integración con BD FAZ**   RF-IG-01 a RF-IG-03 (todos pendientes)   Los atletas deben registrarse manualmente siempre     El puerto está definido. Se opera con registro manual. Cuando se defina el protocolo, se implementa el adaptador.
  **Mantenimiento del sistema**             AC-MT-01 (pendiente)                     Riesgo de que el sistema no evolucione                Diseñar para máxima configurabilidad y documentar decisiones arquitectónicas para facilitar el onboarding de cualquier equipo futuro.
  **Servicio de notificaciones push**       AC-IO-04 (pendiente)                     Solo se puede notificar por email                     Implementar email primero. El puerto de push está definido. Se agrega el adaptador cuando se elija el servicio.
  ----------------------------------------- ---------------------------------------- ----------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Nota:**                                                                                                                                                                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                                                                                                                                                         |
| Este documento es una propuesta inicial que debe ser revisada y validada. Las decisiones marcadas con trade-offs son puntos de discusión donde existen alternativas válidas. El objetivo no es que este documento sea definitivo, sino que haga explícitas las decisiones y sus fundamentos para facilitar la conversación informada sobre la arquitectura del sistema. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
