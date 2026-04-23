**ATARAXIADIVE**

Plataforma de Gestión de Torneos de Apnea

Cuestionario de Elicitación - Atributos de Calidad

> **Estado documental:** referencia historica de elicitacion — Febrero 2026.
> Preserva drivers de calidad iniciales. Las decisiones arquitectonicas vigentes
> estan en `docs/adr/` y `docs/architecture/`.

  **Proyecto:**    Ataraxiadive
  ---------------- ------------------------
  **Versión:**     1.0 - Borrador inicial
  **Fecha:**       Febrero 2026
  **Dimensión:**   Atributos de Calidad

Este cuestionario explora los atributos de calidad (requisitos no funcionales) del sistema Ataraxiadive. Las preguntas se derivan directamente del análisis de los requerimientos funcionales ya relevados y buscan capturar las restricciones y expectativas que condicionarán las decisiones de arquitectura.

Cada sección incluye un recuadro verde que indica el driver arquitectónico que motivó las preguntas, vinculándolo con los requerimientos funcionales de origen. Esto permite rastrear por qué cada atributo de calidad es relevante para Ataraxiadive.

1. Rendimiento (Performance)
============================

*El sistema opera en tiempo real durante la competencia. El juez registra acciones secuenciales críticas (llamar, confirmar, iniciar, finalizar, registrar) que no admiten demoras perceptibles.*

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                            |
|                                                                                                                                                                                                 |
| RF-EJ-05 establece que el juez ingresa tiempos manualmente. RF-PR-06 confirma múltiples andariveles simultáneos. La interfaz del juez es el cuello de botella del sistema durante la ejecución. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                                                    **Respuesta**
  ---------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -------------------------
  AC-RD-01   Durante la ejecución de una competencia, ¿cuál es el tiempo máximo aceptable para que el sistema registre una acción del juez (llamar atleta, iniciar/finalizar performance)?   500 mseg
  AC-RD-02   ¿Cuántos atletas simultáneos se esperan como máximo en una misma disciplina (considerando múltiples andariveles)?                                                               3
  AC-RD-03   ¿Cuántos usuarios concurrentes se estima que usarán el sistema durante un torneo? (jueces + organizadores + atletas consultando)                                                50
  AC-RD-04   ¿Cuál es el volumen máximo esperado de atletas inscriptos en un torneo?                                                                                                         100
  AC-RD-05   ¿El cálculo de rankings y resultados debe ser en tiempo real o puede tener un retardo (por ejemplo, se calculan al cerrar la disciplina)?                                       Al cerrar la disciplina

2. Disponibilidad (Availability)
================================

*Una caída del sistema durante la ejecución de una competencia tiene impacto directo e irreversible: los atletas están en el agua, el cronómetro corre, y los resultados deben registrarse en el momento.*

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                      |
| RF-EJ-02 indica que un DNS es descalificación inmediata. No hay tolerancia para \'esperar que el sistema vuelva\'. La competencia no se detiene por el sistema. Además, las competencias frecuentemente se realizan en ambientes acuáticos donde la conectividad puede ser precaria. |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                                       **Respuesta**
  ---------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------ -------------------------------------------------------------------------------------
  AC-DS-01   Si el sistema se cae durante la ejecución de una competencia, ¿cuál es el tiempo máximo aceptable de interrupción antes de que sea crítico?                        Se pasa a registro manual, el sistema debe estar alojado en un servidor en la nube.
  AC-DS-02   ¿Las competencias se realizan en lugares con conectividad a internet confiable, o es frecuente que haya problemas de conectividad (piletas, lagos, mar abierto)?   Hay problemas de conectivdad
  AC-DS-03   ¿El juez debe poder seguir operando si se pierde temporalmente la conexión a internet? (modo offline)                                                              si
  AC-DS-04   ¿Existe un plan B manual (planillas en papel) si el sistema no está disponible, o el sistema es la única vía de registro?                                          Si
  AC-DS-05   ¿En qué horarios se realizan las competencias? ¿El sistema necesita estar disponible 24/7 o solo durante ventanas específicas?                                     Ventanas especificasc

3. Usabilidad (Usability)
=========================

*El juez opera el sistema bajo presión temporal y condiciones ambientales adversas (agua, sol, frío). Cada segundo de fricción con la interfaz es un riesgo para la integridad de los datos de la competencia.*

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                            |
|                                                                                                                                                                                                                                                 |
| RF-EJ-05 (cronometraje manual) + RF-EJ-07 (registro de black-out con distancia) + RF-EJ-03 (tarjetas configurables) generan un flujo de interacción complejo que debe resolverse con mínima fricción desde un dispositivo probablemente mojado. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                                                                                          **Respuesta**
  ---------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------
  AC-US-01   ¿El juez opera el sistema desde un celular, tablet, o notebook al borde de la pileta? ¿Qué dispositivo es el principal?                                                                                               Principalmente celular, puede ser tablet
  AC-US-02   ¿El juez necesita registrar la performance con el mínimo número de toques/clics posible? ¿Cuántas acciones máximas serían aceptables para un flujo completo (llamar → confirmar → iniciar → finalizar → registrar)?   Si, y como máximo son 6 acciones.
  AC-US-03   ¿La interfaz del juez debe funcionar bajo condiciones adversas (sol directo en pantalla, manos mojadas, guantes)?                                                                                                     probablemente
  AC-US-04   ¿Los atletas que se auto-registran tienen experiencia con tecnología, o se espera un rango amplio de perfiles (jóvenes, adultos mayores)?                                                                             Amplio rango
  AC-US-05   ¿Se necesita soporte multi-idioma o el sistema será exclusivamente en español?                                                                                                                                        Por ahora español, pero debe ser tenido en cuenta
  AC-US-06   ¿El organizador debe poder armar la grilla de salida desde un celular o se espera que use una pantalla más grande (notebook/desktop)?                                                                                 La grilla de salida debe esta ya planificada antes de las competencia y debe ser visible en el celular

4. Configurabilidad (Configurability)
=====================================

*Múltiples respuestas del cuestionario funcional indican que el sistema debe ser adaptable sin cambios de código: disciplinas, categorías, tarjetas, penalizaciones, y reglas de cálculo son todas configurables.*

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                                                        |
|                                                                                                                                                                                                                                                                             |
| RF-GT-02 (disciplinas configurables) + RF-IN-01 (categorías configurables) + RF-EJ-03 (tarjetas como reglas configurables) + RF-PM-01 (cálculo de puntos pendiente, será regla de negocio). Este patrón recurrente de configurabilidad es un driver arquitectónico central. |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                                      **Respuesta**
  ---------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- ------------------------------
  AC-CF-01   Cuando se dice que las disciplinas son \'configurables\', ¿quién las configura? ¿El administrador del sistema o el organizador de cada torneo?                    El administrador del sistema
  AC-CF-02   ¿Las reglas de tarjetas (blanca/amarilla/roja) y penalizaciones deben poder cambiar entre torneos, o cambian solo cuando la federación actualiza el reglamento?   Las definen las federaciones
  AC-CF-03   ¿Las categorías configurables (ej: senior masculino 18-50) deben poder definirse por torneo o son globales del sistema?                                           Son globales
  AC-CF-04   ¿La fórmula de cálculo de puntos (cuando se defina) debe ser configurable por torneo, o es única para todo el sistema?                                            Es por torneo
  AC-CF-05   ¿Se prevé que en el futuro se agreguen nuevos tipos de disciplinas con mecánicas diferentes a las actuales (distancia/tiempo)?                                    si

5. Seguridad (Security)
=======================

*El sistema maneja datos personales de atletas, resultados oficiales de competencias deportivas, y flujos de trabajo con permisos diferenciados. La integridad de los resultados es la credibilidad del torneo.*

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                                                   |
|                                                                                                                                                                                                                                                                        |
| RF-US-02 (roles múltiples por usuario) + RF-US-04 (juez asignado a disciplina específica) + RF-EJ-06 (corrección de resultados). La combinación de roles flexibles con permisos granulares por contexto (torneo/disciplina) requiere un modelo de seguridad cuidadoso. |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                                                        **Respuesta**
  ---------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ------------------
  AC-SG-01   ¿Los datos de los atletas (documento, contacto, historial) se consideran datos sensibles que requieren protección especial (ej: ley de protección de datos personales argentina)?   No son sensibles
  AC-SG-02   ¿Se requiere que las acciones del juez durante la competencia queden registradas en un log de auditoría inalterable?                                                                si
  AC-SG-03   ¿Un juez debería poder ver/modificar resultados de disciplinas donde no está asignado?                                                                                              Solo ver
  AC-SG-04   ¿Se necesita protección contra manipulación de resultados (por ejemplo, que alguien modifique una performance después de cerrada la disciplina)?                                    si
  AC-SG-05   ¿El organizador debe poder delegar acciones específicas a otra persona sin darle el rol completo de organizador?                                                                    no

6. Confiabilidad (Reliability)
==============================

*Cada performance es un evento único e irrepetible. Un dato perdido o corrupto no puede reconstruirse pidiendo al atleta que repita su performance. La confiabilidad del registro es existencial para el sistema.*

+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                                        |
|                                                                                                                                                                                                                                                             |
| RF-EJ-06 (corrección de resultados) + RF-EJ-07 (black-out registra distancia) + RF-PR-06 (andariveles simultáneos). El sistema debe garantizar que cada acción del juez se persista correctamente, incluso bajo condiciones adversas de red o concurrencia. |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                             **Respuesta**
  ---------- -------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------
  AC-CN-01   Si el juez registra una performance y el sistema falla inmediatamente después, ¿es aceptable perder ese registro o debe garantizarse que se persistió?   Se debe garantizar
  AC-CN-02   ¿Se necesita algún mecanismo de confirmación visual para el juez después de registrar cada performance (ej: pantalla de resumen, sonido)?                si
  AC-CN-03   ¿Debe existir la posibilidad de reconstruir el estado completo de una competencia a partir de un log de eventos?                                         si
  AC-CN-04   ¿Qué sucede si dos jueces (en andariveles distintos) intentan registrar performances simultáneamente? ¿Hay riesgo de conflicto de datos?                 no
  AC-CN-05   ¿Se requiere backup automático de los datos del torneo durante la ejecución?                                                                             no

7. Escalabilidad (Scalability)
==============================

*El sistema nace para torneos nacionales argentinos, pero las decisiones de hoy condicionan el crecimiento futuro. Entender el horizonte de escala evita tanto el sobre-diseño como el sub-diseño.*

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                                      |
|                                                                                                                                                                                                                                                           |
| RF-GT-03 (múltiples torneos simultáneos) + RF-PM-02 (ranking Overall que combina disciplinas) + RF-PM-06 (publicación de resultados descargables). El volumen de datos crece con cada torneo y la demanda de consultas se concentra en picos predecibles. |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                     **Respuesta**
  ---------- ------------------------------------------------------------------------------------------------------------------------------------------------ ----------------------------------
  AC-ES-01   ¿Cuántos torneos por año se estima que gestionará el sistema inicialmente? ¿Y en 3-5 años?                                                       4 torneos por año, y por 5 años
  AC-ES-02   ¿Se prevé que el sistema se use fuera de Argentina (otras federaciones de la región)?                                                            Por el momento no
  AC-ES-03   ¿El volumen de datos históricos (torneos pasados, performances) debe mantenerse accesible indefinidamente o puede archivarse?                    En principio debe mantenerse
  AC-ES-04   ¿Se espera que el sistema soporte streaming de resultados en vivo para espectadores (familiares, público) o es solo para los roles operativos?   No hay streaming por el momento.

8. Mantenibilidad (Maintainability)
===================================

*Un sistema deportivo federativo evoluciona al ritmo de los cambios reglamentarios. La capacidad de adaptar el sistema sin depender de un desarrollador para cada cambio es clave para su sostenibilidad a largo plazo.*

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                                                                           |
|                                                                                                                                                                                                                                                                                                |
| RF-EJ-04 (códigos de penalización pendientes, siguen reglamento federativo) + RF-PM-01 (cálculo de puntos pendiente, regla de negocio) + RF-GT-02 (disciplinas iniciales con posibilidad de agregar). Las reglas del dominio cambiarán y el sistema debe absorber esos cambios con bajo costo. |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                                                       **Respuesta**
  ---------- -------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------------------------------------------
  AC-MT-01   ¿Quién se encargará del mantenimiento y evolución del sistema? ¿Un equipo de desarrollo dedicado, el propio organizador, o un proveedor externo?   Pendiente
  AC-MT-02   ¿Se espera que el organizador pueda configurar reglas de negocio (penalizaciones, categorías, disciplinas) sin intervención de un desarrollador?   si
  AC-MT-03   ¿Con qué frecuencia se espera que cambien las reglas de la federación que afectan al sistema?                                                      Es muy esporádica, cada 2 años como una idea
  AC-MT-04   ¿Se requiere que el sistema pueda actualizarse sin interrumpir un torneo en curso?                                                                 No, se actualiza en instancias donde no hay competencias

9. Interoperabilidad (Interoperability)
=======================================

*El sistema no opera aislado: consume datos externos de atletas, envía notificaciones por múltiples canales, y potencialmente alimenta rankings internacionales. Cada punto de integración es un punto de falla y de acoplamiento.*

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Driver arquitectónico detectado:**                                                                                                                                                                                                  |
|                                                                                                                                                                                                                                       |
| RF-IG-01 a RF-IG-04 (todos pendientes, integración con BD externa y sistemas de ranking) + RF-NT-01 (mail + push) + RF-IN-06 (constancia de pago). La zona de integración es la de mayor incertidumbre y riesgo técnico del proyecto. |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  **ID**     **Pregunta**                                                                                                    **Respuesta**
  ---------- --------------------------------------------------------------------------------------------------------------- -------------------
  AC-IO-01   ¿Se prevé integración futura con sistemas de cronometraje electrónico (touchpads, sensores)?                    si
  AC-IO-02   ¿Los resultados deben poder exportarse en algún formato estándar (CSV, JSON, formato AIDA/CMAS)?                si
  AC-IO-03   ¿Se necesita integración con servicios de pago para la inscripción, o siempre será constancia manual?           No por el momento
  AC-IO-04   ¿El sistema de notificaciones push debe integrarse con algún servicio específico (Firebase, OneSignal, otro)?   pendiente

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Nota:**                                                                                                                                                                                                                                                                                                                                                                                                        |
|                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Las respuestas a este cuestionario, junto con los requerimientos funcionales ya relevados, constituirán los insumos principales para la tercera dimensión del análisis: la Arquitectura de Referencia. Es esperable que algunas respuestas sean \'no sé\' o \'depende\' --- eso también es información valiosa que ayuda a identificar dónde se necesitan decisiones arquitectónicas que absorban incertidumbre. |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
