**ATARAXIADIVE**

Plataforma de Gestión de Torneos de Apnea

Cuestionario de Elicitación - Requerimientos Funcionales

  **Proyecto:**    Ataraxiadive
  ---------------- ----------------------------
  **Versión:**     1.0 - Borrador inicial
  **Fecha:**       Febrero 2026
  **Dimensión:**   Requerimientos Funcionales

Este cuestionario tiene como objetivo profundizar y completar la comprensión de los requerimientos funcionales del sistema Ataraxiadive. Las preguntas están organizadas por área funcional y surgen del análisis de la especificación inicial. Complete la columna \'Respuesta\' con la mayor precisión posible.

1. Gestión del Torneo
=====================

*El documento describe las 6 fases del torneo y los datos básicos de creación. Las siguientes preguntas buscan clarificar aspectos del ciclo de vida del torneo que no están completamente especificados.*

  **ID**     **Pregunta**                                                                                                                                         **Respuesta**
  ---------- ---------------------------------------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------
  RF-GT-01   ¿Un torneo puede tener más de una sede o ubicación (por ejemplo, distintas piletas para distintas disciplinas)?                                      No
  RF-GT-02   ¿Qué disciplinas específicas debe soportar el sistema? (STA, DNF, DYN, DYNB, CNF, CWT, FIM, etc.)                                                    Debe ser configurable, inicialmente: STA, DNF, DBF, DYN, SPE2X50.
  RF-GT-03   ¿Pueden existir múltiples torneos activos simultáneamente en el sistema?                                                                             SI
  RF-GT-04   ¿Qué significa exactamente \'cancelar un torneo\'? ¿Se elimina o cambia a un estado cancelado conservando la información?                            Estado cancelado conservando la información
  RF-GT-05   ¿Existen restricciones para la transición entre fases del torneo? Por ejemplo, ¿se puede volver de Ejecución a Preparación si se detecta un error?   Si
  RF-GT-06   ¿El cierre del torneo implica algún proceso de archivo o exportación de datos?                                                                       No
  RF-GT-07   ¿Se debe registrar la entidad organizadora (federación, club) además del organizador como persona?                                                   Si

2. Inscripción de Atletas
=========================

*Se identifican los datos del atleta y la integración con una base de datos externa. Estas preguntas buscan cerrar brechas sobre reglas de negocio de la inscripción.*

  **ID**     **Pregunta**                                                                                                         **Respuesta**
  ---------- -------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------
  RF-IN-01   ¿Qué categorías existen? ¿Son fijas (por ejemplo, por edad y género) o las define el organizador para cada torneo?   Hoy son fijas, pero debería pensarse como configurable, por ejemplo senior masculino de 18 a 50 años.
  RF-IN-02   ¿El número de brevet es obligatorio? ¿Qué pasa si un atleta no tiene brevet?                                         No
  RF-IN-03   ¿Existe un límite máximo de atletas inscriptos por torneo o por disciplina?                                          No
  RF-IN-04   ¿Un atleta puede cancelar su inscripción? ¿Hasta qué momento?                                                        Si, el día antes de la competencia
  RF-IN-05   ¿Se requiere alguna validación médica o apto físico como requisito de inscripción?                                   Si
  RF-IN-06   ¿La inscripción tiene costo? ¿El sistema debe gestionar o registrar pagos?                                           Si, por ahora se pide constancia del pago
  RF-IN-07   ¿Cómo se resuelve si un atleta se inscribe con datos diferentes a los que tiene la base de datos externa?            Pendiente de definicion
  RF-IN-08   ¿El género se utiliza solo para categorización o tiene algún otro efecto en la competencia?                          Solo categoría
  RF-IN-09   ¿Puede un atleta inscribirse en categorías diferentes según la disciplina?                                           No

3. Preparación de Competencias
==============================

*La fase de preparación involucra la recolección de anuncios y la generación de grillas de salida. Estas preguntas buscan precisar la mecánica del proceso.*

  **ID**     **Pregunta**                                                                                                                                               **Respuesta**
  ---------- ---------------------------------------------------------------------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------
  RF-PR-01   ¿Qué es exactamente un \'anuncio\' (AP - Announced Performance)? ¿Es la marca que el atleta declara que intentará lograr?                                  Si
  RF-PR-02   ¿Hay un valor mínimo o máximo permitido para los anuncios?                                                                                                 No permito valores 0 y negativos
  RF-PR-03   ¿Un atleta puede modificar su anuncio una vez registrado? ¿Hasta cuándo?                                                                                   No
  RF-PR-04   ¿Qué sucede si un atleta no registra su anuncio dentro del plazo?                                                                                          No compite
  RF-PR-05   ¿Cómo se determina el orden de salida? ¿De menor a mayor anuncio, de mayor a menor, u otro criterio?                                                       Depende de la disciplina. Para metros: de menor a mayor, para tiempos de mayor a menor
  RF-PR-06   ¿Qué son exactamente las \'líneas de competencia\' o \'andariveles\'? ¿Pueden competir varios atletas simultáneamente?                                     Si
  RF-PR-07   ¿El organizador puede modificar manualmente el orden de salida generado automáticamente?                                                                   Si
  RF-PR-08   ¿Cuál es la \'duración de cada performance\' que define el organizador? ¿Es el tiempo máximo permitido o el intervalo entre atletas (OT - Official Top)?   Es el tiempo entre tiempos oficiales, lo determina el juez de la competencia para cada prueba

4. Ejecución de Competencias
============================

*Esta es la fase crítica del sistema. El flujo juez-atleta-performance debe estar completamente definido para asegurar la integridad de los datos en tiempo real.*

  **ID**     **Pregunta**                                                                                                                        **Respuesta**
  ---------- ----------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------
  RF-EJ-01   ¿Puede haber más de un juez asignado a una disciplina (juez principal, jueces de línea, safety divers)?                             Si
  RF-EJ-02   ¿Qué pasa si un atleta no se presenta cuando es llamado (DNS - Did Not Start)? ¿Cuánto tiempo se espera?                            No hay espera, queda descalificado.
  RF-EJ-03   Además de tarjeta blanca (válida) y roja (descalificación), ¿se manejan tarjetas amarillas (penalizaciones parciales con puntos)?   Si, hay que manejarlas como reglas de negocio configurables.
  RF-EJ-04   ¿Cuáles son los códigos de penalización posibles? ¿Siguen las reglas AIDA/CMAS u otra federación?                                   Pendiente
  RF-EJ-05   ¿El cronometraje lo realiza el sistema (cronómetro digital) o el juez ingresa el tiempo manualmente?                                El juez lo toma manualmente,
  RF-EJ-06   ¿Un juez puede corregir un resultado ya registrado para una performance? ¿Hay un período de protesta?                               Si
  RF-EJ-07   ¿Qué información se registra en un back-out? ¿Solo el hecho o también la distancia/tiempo alcanzado?                                Es black-out, la distancia también.
  RF-EJ-08   ¿Para disciplinas de distancia (DNF, DYN, DYNB), cómo se mide? ¿Metros exactos, con decimales?                                      Si, con decimales
  RF-EJ-09   ¿El protocolo de superficie (SP) es evaluado y registrado por el sistema?                                                           No
  RF-EJ-10   ¿Se debe registrar el resultado del protocolo de superficie por separado o solo su efecto (tarjeta blanca/amarilla/roja)?           Solo el resultado

5. Premiación y Resultados
==========================

*El cálculo de resultados y la generación de rankings son el producto final visible del torneo. Estas preguntas buscan definir las reglas de cálculo y presentación.*

  **ID**     **Pregunta**                                                                                                             **Respuesta**
  ---------- ------------------------------------------------------------------------------------------------------------------------ ------------------------------------------------
  RF-PM-01   ¿Los resultados se calculan por puntos (según tablas de la federación) o por marca absoluta en cada disciplina?          Pendiente, es una regla de negocio
  RF-PM-02   ¿Existe un ranking general del torneo que combine resultados de múltiples disciplinas, o solo rankings por disciplina?   Si, se denomina Overall
  RF-PM-03   ¿Cómo se resuelven los empates en una disciplina?                                                                        Ocupan el mismo puesto, y los mismo puntos
  RF-PM-04   ¿Los certificados/diplomas deben incluir información específica (logo de la FAZ, de la federación, firmas)?              Esto no es importante por ahora
  RF-PM-05   ¿Se deben generar rankings separados por categoría y género dentro de cada disciplina?                                   si
  RF-PM-06   ¿Los resultados deben ser publicados de alguna forma (web pública, PDF descargable)?                                     Se publican en la plataforma, puede descargase

6. Usuarios, Roles y Permisos
=============================

*Se identifican 3 roles principales más un administrador. Las siguientes preguntas buscan precisar la gestión de identidad y los permisos cruzados.*

  **ID**     **Pregunta**                                                                                                 **Respuesta**
  ---------- ------------------------------------------------------------------------------------------------------------ -------------------------------------------
  RF-US-01   ¿El administrador general puede crear múltiples organizadores para un mismo torneo?                          No
  RF-US-02   ¿Un mismo usuario puede tener múltiples roles (por ejemplo, ser organizador y juez en distintos torneos)?    Si
  RF-US-03   ¿Cómo se autentican los atletas cuando se auto-registran? ¿Mail + contraseña, enlace mágico, otro?           Mail, contraseña
  RF-US-04   ¿Un juez necesita ser asignado por el organizador a disciplinas específicas, o puede actuar en cualquiera?   Hay que asignar un juez a cada disciplina
  RF-US-05   ¿Los atletas pueden ver los resultados de otros atletas durante la competencia?                              Solo los resultados finales

7. Notificaciones
=================

*El documento menciona notificaciones por email en momentos específicos. Estas preguntas buscan completar el modelo de comunicación del sistema.*

  **ID**     **Pregunta**                                                                                          **Respuesta**
  ---------- ----------------------------------------------------------------------------------------------------- ----------------
  RF-NT-01   ¿Las notificaciones son solo por email o también se contemplan notificaciones in-app o push?          Por mail, push
  RF-NT-02   ¿Se debe notificar al atleta cuando se acerca la fecha límite de anuncios?                            Si
  RF-NT-03   ¿El juez o el organizador deben recibir alguna notificación durante la ejecución de la competencia?   Pendiente
  RF-NT-04   ¿Se notifica a los atletas cuando los resultados finales están publicados?                            Si

8. Integración con Sistemas Externos
====================================

*Se menciona una base de datos externa de atletas. Estas preguntas buscan definir el alcance y las restricciones de la integración.*

  **ID**     **Pregunta**                                                                                                                                          **Respuesta**
  ---------- ----------------------------------------------------------------------------------------------------------------------------------------------------- ---------------
  RF-IG-01   ¿La base de datos externa de atletas es de la FAZ (Federación Argentina de Actividades Subacuáticas)? ¿Qué formato/protocolo se usa para accederla?   Pendiente
  RF-IG-02   ¿La consulta a la base de datos externa es solo de lectura, o el sistema también debe actualizar datos en ella?                                       Pendiente
  RF-IG-03   ¿Qué sucede si la base de datos externa no está disponible al momento de inscribirse un atleta?                                                       Pendiente
  RF-IG-04   ¿Se deben exportar resultados a algún sistema externo de rankings (AIDA, CMAS)?                                                                       Pendiente

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Nota:**                                                                                                                                                                                                                                                |
|                                                                                                                                                                                                                                                          |
| Este cuestionario es iterativo. Las respuestas a estas preguntas probablemente generen nuevas preguntas de seguimiento que permitirán refinar aún más la especificación. Se recomienda responder aunque sea parcialmente e indicar las dudas que surjan. |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
