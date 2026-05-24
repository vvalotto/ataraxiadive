# ATARAXIADIVE — Arquitectura de Referencia

**Plataforma de Gestión de Torneos de Apnea — Estado Final Implementado**

> **Estado documental:** vigente  
> Actualizado a Mayo 2026 para reflejar el sistema tal como fue implementado en v1.0.0.  
> Decisiones de BD, infra y stack formalizadas en ADR-006 (BC-first), ADR-007 (SQLite), ADR-021 (Fly.io).  
> Fuente vigente relacionada: `docs/adr/` · `CLAUDE.md §2`

| Campo       | Valor                                                          |
|-------------|----------------------------------------------------------------|
| Proyecto    | Ataraxiadive                                                   |
| Versión     | 2.0 — Estado final implementado (v1.0.0)                       |
| Fecha       | Mayo 2026                                                      |
| Dimensión   | Arquitectura de Referencia                                     |
| Insumos     | Requerimientos Funcionales v1.0 + Atributos de Calidad v1.0   |

Este documento describe la arquitectura de alto nivel del sistema Ataraxiadive tal como fue implementada en la versión 1.0.0. Cada decisión arquitectónica se deriva de los requerimientos funcionales y atributos de calidad relevados en las dimensiones anteriores del análisis, y está formalizada en los ADRs correspondientes.

---

## 1. Drivers Arquitectónicos Priorizados

Del cruce entre los requerimientos funcionales y los atributos de calidad emergen los siguientes drivers arquitectónicos, ordenados por impacto en las decisiones de diseño:

| Prioridad | Driver                                                    | Origen                                     | Impacto                                                                 |
|:---------:|------------------------------------------------------------|---------------------------------------------|-------------------------------------------------------------------------|
| 1         | Operación offline del juez durante la competencia          | AC-DS-02, AC-DS-03, AC-CN-01                | Define la estrategia de sincronización y el modelo de datos local       |
| 2         | Interfaz del juez mobile-first bajo estrés                 | AC-US-01, AC-US-02, AC-US-03, AC-RD-01      | Define el framework de UI y el diseño de interacción crítica            |
| 3         | Configurabilidad multinivel sin cambios de código          | AC-CF-01 a AC-CF-05, RF-EJ-03, RF-IN-01     | Define el modelo de metadatos y el motor de reglas                      |
| 4         | Integridad y auditabilidad de resultados                   | AC-SG-02, AC-SG-04, AC-CN-03                | Define la estrategia de persistencia y el modelo de eventos             |
| 5         | Ciclo de vida del torneo como máquina de estados           | RF-GT-05, RF-GT-04                           | Define el flujo de negocio central y las transiciones permitidas        |
| 6         | Integración con sistemas externos bajo incertidumbre       | RF-IG-01 a RF-IG-04, AC-IO-01 a AC-IO-04    | Define la estrategia de acoplamiento débil en los bordes                |

---

## 2. Visión General de la Arquitectura

### 2.1 Estilo Arquitectónico

> **Decisión arquitectónica:**  
> Arquitectura modular por capas con separación explícita entre el núcleo de dominio, los servicios de aplicación, y los adaptadores de infraestructura. El sistema se estructura siguiendo los principios de Arquitectura Hexagonal (Ports & Adapters), donde el dominio de la competencia es el centro y todo lo demás (UI, base de datos, integraciones) son adaptadores intercambiables.

> **Driver:**  
> La combinación de configurabilidad (AC-CF-01 a AC-CF-05), integración incierta (RF-IG-01 a RF-IG-04), y la necesidad futura de nuevos tipos de disciplinas (AC-CF-05) requiere un núcleo de dominio estable y desacoplado de la infraestructura.

La elección de Arquitectura Hexagonal responde a una necesidad concreta: el dominio de la apnea competitiva tiene reglas propias que cambian según la federación (AIDA, CMAS) y que el sistema debe absorber sin modificar la estructura. Al aislar el dominio del resto, las reglas de tarjetas, penalizaciones, cálculo de puntos y disciplinas pueden evolucionar independientemente de cómo se persistan los datos o cómo se presente la interfaz.

### 2.2 Estructura de Capas

El sistema se organiza en cuatro capas concéntricas, donde las dependencias fluyen siempre hacia adentro:

| Capa                  | Responsabilidad                                        | Contenido                                                                                                                                    |
|-----------------------|--------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| **Dominio (centro)**  | Reglas de negocio puras, independientes de tecnología  | Entidades (Torneo, Atleta, Performance, Disciplina), Value Objects (AP, Tarjeta, Penalización), Reglas de validación, Máquina de estados     |
| **Aplicación**        | Orquestación de casos de uso y flujos de trabajo       | Servicios de aplicación (InscribirAtleta, RegistrarPerformance, GenerarGrilla), Comandos y Queries, Políticas de notificación                |
| **Infraestructura**   | Implementaciones técnicas concretas                    | Repositorios (persistencia), Servicios de notificación (email), Clientes de integración (BD externa FAAS)                                   |
| **Presentación**      | Interfaces de usuario adaptadas por rol                | Interfaz del Juez (mobile-first, offline-capable), Portal del Atleta (registro, anuncios, resultados), Panel del Organizador (gestión, grillas) |

---

## 3. Modelo de Dominio de Alto Nivel

El modelo de dominio se organiza alrededor de los agregados principales que emergen del análisis funcional. Cada agregado es una frontera de consistencia transaccional.

### 3.1 Agregados Principales

| Agregado         | Raíz                   | Entidades/VOs contenidos                                                    | Responsabilidad                                                                    |
|------------------|------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| **Torneo**       | Torneo                 | Fase, Disciplina seleccionada, Entidad organizadora                         | Ciclo de vida del torneo, transiciones de fase, configuración de disciplinas       |
| **Inscripción**  | Inscripción            | Datos del atleta, Categoría, Disciplinas                                    | Registro del atleta en un torneo específico con sus disciplinas                    |
| **Competencia**  | Competencia            | Grilla de salida, Slot de competencia, OT                                   | Planificación de una disciplina: orden de salida, andariveles, tiempos oficiales   |
| **Performance**  | Performance            | Marca (tiempo/distancia), Tarjeta, Penalización, Estado                     | Registro atómico de cada performance individual de un atleta                       |
| **Resultado**    | Resultado de disciplina | Ranking por categoría, Puntos, Posición                                    | Cálculo y publicación de resultados por disciplina y overall                       |

### 3.2 Máquina de Estados del Torneo

El torneo es una máquina de estados con transiciones controladas por el organizador (RF-GT-05):

| Estado origen        | Estado destino     | Condición / Acción                                                              |
|----------------------|--------------------|---------------------------------------------------------------------------------|
| Creado               | Inscripción Abierta | Organizador habilita inscripción. Se notifica apertura.                        |
| Inscripción Abierta  | Preparación        | Organizador cierra inscripción. Se notifica a atletas para anuncios.            |
| Preparación          | Ejecución          | Todos los anuncios registrados o plazo vencido. Grillas generadas.              |
| Ejecución            | Preparación        | Retroceso permitido si se detecta error (RF-GT-05).                             |
| Ejecución            | Premiación         | Todas las disciplinas cerradas. Rankings calculados.                            |
| Premiación           | Cerrado            | Organizador confirma cierre. Resultados publicados.                             |
| Cualquiera           | Cancelado          | Organizador cancela. Se conserva toda la información (RF-GT-04).                |

> **Nota:** el retroceso de Ejecución a Preparación solo es posible si no hay disciplinas con performances registradas, o si el organizador confirma explícitamente que se descartarán los resultados de disciplinas no cerradas.

---

## 4. Estrategia Offline-First para la Interfaz del Juez

*Este es el driver arquitectónico de mayor impacto. La combinación de conectividad precaria (AC-DS-02), operación offline obligatoria (AC-DS-03), y garantía de persistencia (AC-CN-01) exige una estrategia deliberada.*

### 4.1 Modelo Implementado

> **Decisión arquitectónica:**  
> La interfaz del juez opera como una PWA offline-first. Toda la lógica de registro de performances se ejecuta localmente. Los datos se persisten primero en almacenamiento local del dispositivo (IndexedDB) y luego se sincronizan con el servidor cuando hay conectividad.

| Paso                  | Ubicación         | Descripción                                                                                                                                         |
|-----------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. Pre-carga**      | Servidor → Local  | Al abrir una disciplina, se descarga al dispositivo: la grilla de salida, los datos de atletas, y las reglas configuradas (tarjetas, penalizaciones). |
| **2. Operación**      | Local             | El juez opera enteramente en local: llama atleta, confirma, inicia, finaliza, registra. Cada acción se encola localmente como comando.               |
| **3. Confirmación**   | Local             | El juez recibe confirmación visual inmediata (AC-CN-02) desde los datos locales, sin depender del servidor.                                          |
| **4. Sincronización** | Local → Servidor  | Cuando hay conectividad, los comandos de la cola se envían al servidor. El servidor valida y persiste.                                               |
| **5. Reconciliación** | Servidor → Local  | El servidor confirma la recepción. Si hay discrepancias, se notifica al juez vía `SyncStatusBadge`.                                                  |

### 4.2 Tecnología de Almacenamiento Local

> **Decisión arquitectónica (implementada):**  
> IndexedDB vía Dexie.js 4.x. La aplicación es una PWA (vite-plugin-pwa + Service Worker). Se descartó SQLite WASM y app nativa. Dexie.js gestiona dos tablas: `grilla_cache` (precarga de grilla por competencia/disciplina) y `comando_queue` (cola de comandos pendientes de sincronización).

---

## 5. Estrategia de Persistencia y Auditoría

### 5.1 Event Sourcing para la Competencia

> **Decisión arquitectónica:**  
> El registro de la competencia (fase de Ejecución) se implementa con Event Sourcing: cada acción del juez se persiste como un evento inmutable. El estado actual de cada performance se reconstruye a partir de la secuencia de eventos.

> **Driver:**  
> AC-SG-02 (log de auditoría inalterable) + AC-CN-03 (reconstruir estado desde log) + AC-SG-04 (protección contra manipulación post-cierre). El Event Sourcing satisface los tres requerimientos como un efecto natural de su diseño, no como una funcionalidad agregada.

Eventos del dominio de competencia:

| Evento                    | Datos                                                                                  | Emitido cuando                                     |
|---------------------------|----------------------------------------------------------------------------------------|----------------------------------------------------|
| **AtletaLlamado**         | competencia_id, atleta_id, andarivel, OT, timestamp                                    | El juez llama al siguiente atleta                  |
| **DNSRegistrado**         | competencia_id, atleta_id, timestamp                                                   | El atleta no se presenta                           |
| **ResultadoRegistrado**   | competencia_id, atleta_id, tipo (tiempo/distancia), valor, unidad                      | El juez ingresa la marca final                     |
| **TarjetaAsignada**       | competencia_id, atleta_id, tarjeta, motivo_dq?, distancia_blackout?, penalizaciones?   | El juez califica la performance                    |
| **RevisionResuelta**      | competencia_id, atleta_id, resolucion (Blanca/Roja), motivo_dq?                        | El juez cierra una tarjeta Amarilla                |
| **ResultadoCorregido**    | competencia_id, atleta_id, campo, valor_anterior, valor_nuevo, motivo, timestamp       | El juez corrige un resultado (RF-EJ-06)            |

### 5.2 Persistencia Dual

| Representación              | Descripción                                                                                                                                |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Event Store (inmutable)** | Secuencia completa de eventos. Nunca se modifica ni se elimina. Fuente de verdad para auditoría y reconstrucción. Satisface AC-SG-02 y AC-CN-03. |
| **Read Model (proyección)** | Tabla materializada con el estado actual de cada performance. Se reconstruye desde los eventos. Optimizada para consultas rápidas del juez, ranking y resultados. |

> **Nota:** Event Sourcing se aplica a los BCs Competencia y Notificaciones. El resto de BCs (Torneo, Registro, Resultados, Identidad) usan CRUD relacional estándar.

---

## 6. Motor de Configuración

> **Decisión arquitectónica:**  
> El sistema implementa configuración en dos niveles: global (organizador) y por torneo (organizador). Las reglas de negocio configurables se modelan como datos, no como código.

> **Driver:**  
> El patrón de configurabilidad es el driver más transversal del sistema: disciplinas (RF-GT-02), categorías (RF-IN-01), tarjetas (RF-EJ-03), penalizaciones (RF-EJ-04), fórmula de puntos (RF-PM-01), y futuras mecánicas de disciplinas (AC-CF-05).

### 6.1 Modelo de Configuración

| Elemento configurable                | Nivel          | Quién configura                              | Origen   |
|--------------------------------------|----------------|----------------------------------------------|----------|
| Disciplinas disponibles              | Global         | Organizador                                  | AC-CF-01 |
| Categorías (edad, género)            | Global         | Organizador                                  | AC-CF-03 |
| Reglas de tarjetas y penalizaciones  | Global         | Organizador (según federación)               | AC-CF-02 |
| Códigos de penalización              | Global         | Organizador (según federación)               | RF-EJ-04 |
| Fórmula de cálculo de puntos         | Por torneo     | Organizador                                  | AC-CF-04 |
| Disciplinas del torneo               | Por torneo     | Organizador (selecciona de las disponibles)  | RF-GT-02 |
| OT por disciplina                    | Por competencia | Juez de competencia                         | RF-PR-08 |

### 6.2 Estrategia para Reglas Extensibles

Cada disciplina se modela con un descriptor que define su mecánica:

| Atributo del descriptor         | Ejemplo                                          |
|---------------------------------|--------------------------------------------------|
| Tipo de medición                | tiempo (STA, SPE) o distancia (DNF, DYN, DBF)   |
| Unidad                          | Segundos o Metros con decimales (RF-EJ-08)       |
| Orden de salida                 | menor a mayor en todas las disciplinas (RF-PR-05) |
| Permite andariveles simultáneos | sí/no, con cantidad máxima                       |
| Reglas de tarjeta aplicables    | conjunto de tarjetas y penalizaciones válidas    |
| Protocolo de superficie         | registra solo efecto (RF-EJ-10)                  |

---

## 7. Diseño de la Interfaz del Juez

*La interfaz del juez es el punto de máxima tensión del sistema: máxima criticidad funcional (performance irrepetible), mínima tolerancia a errores (datos oficiales), condiciones físicas adversas (agua, sol), y dispositivo limitado (celular).*

### 7.1 Principios de Diseño

| Principio                            | Justificación                                                                                                               |
|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **Botones grandes, alto contraste**  | AC-US-03. Operación con manos mojadas y sol directo en pantalla. Mínimo 48×48px por target táctil.                         |
| **Feedback inmediato**               | AC-CN-02 + AC-RD-01 (500ms). Cada acción produce confirmación visual instantánea.                                          |
| **Sin navegación innecesaria**       | El flujo del juez es lineal y predecible. Pantalla de grilla + pantalla de performance.                                     |
| **Estado del atleta siempre visible** | El juez ve en todo momento: nombre, AP, andarivel, OT programado y estado actual.                                          |
| **Modo offline transparente**        | AC-DS-03. El juez no percibe la diferencia entre online y offline. `SyncStatusBadge` muestra el estado de conexión.        |
| **Proyección optimista**             | Los comandos encolados offline se reflejan inmediatamente en la UI sin esperar confirmación del servidor.                   |

### 7.2 Flujo de Interacción del Juez

El juez navega desde la grilla (lista de atletas asignados) a la pantalla de performance. El flujo tiene 7 pasos, con variantes según disciplina y resultado:

| Paso                                    | Acción del juez                                                          | Sistema responde                                                                                                     | Toque # |
|-----------------------------------------|--------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|:-------:|
| **Seleccionar atleta**                  | Toca fila del atleta en la grilla                                        | Navega a pantalla de performance con datos del atleta (nombre, AP, andarivel, OT programado).                        | —       |
| **Llamar**                              | Toca LLAMAR                                                              | Emite `AtletaLlamado`. Estado: Llamada.                                                                              | 1       |
| **Presente / DNS**                      | Toca PRESENTE o DNS                                                      | DNS: registra `DNSRegistrado`, completa, vuelve a grilla. PRESENTE: activa ventana de OT.                            | 2       |
| **Iniciar cronómetro**                  | Toca INICIAR cuando comienza la performance                              | Marca timestamp de inicio. Muestra cronómetro de referencia (no oficial).                                            | 3       |
| **Finalizar cronómetro**                | Toca FINALIZAR al terminar la performance                                | Marca timestamp de fin. Para distancia: habilita ingreso de metros + centímetros. Para STA: muestra tiempo cronometrado. | 4    |
| **Registrar marca**                     | Ingresa metros y centímetros (distancia) o confirma tiempo (STA)        | Habilita selección de tarjeta.                                                                                       | 5       |
| **Asignar tarjeta**                     | Elige: Blanca · Blanca con Penalizaciones · Amarilla · Roja · BKO       | Blanca/BlancaConPenalizaciones/Roja: registra resultado + tarjeta, completa. Amarilla: abre revisión (paso 7).       | 6       |
| **Resolver revisión** *(solo Amarilla)* | Elige tarjeta definitiva: Blanca o Roja (+ motivoDQ si Roja)            | Cierra revisión. Performance completa.                                                                               | 7       |

**Variantes del paso 6:**

| Tarjeta                    | Datos requeridos                                      | Estado resultante  |
|----------------------------|-------------------------------------------------------|--------------------|
| **Blanca**                 | Ninguno adicional                                     | Ejecutada          |
| **Blanca con Penalizaciones** | Lista de penalizaciones técnicas (N × 3m)          | Ejecutada          |
| **Amarilla**               | Ninguno (revisión pendiente)                          | EnRevision → paso 7 |
| **Roja**                   | MotivoDQ (BKO_SUPERFICIE · BKO_SUBACUATICO · NO_PROTOCOLO · etc.) | Ejecutada |
| **BKO**                    | MotivoDQ + distancia alcanzada (solo disciplinas de distancia) | Ejecutada (Roja automática) |

---

## 8. Stack Tecnológico Implementado

| Capa                      | Tecnología                                              | Notas                                                                                       |
|---------------------------|---------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **Frontend**              | React 19 + Vite 6 + TypeScript + Tailwind v4 + PWA      | vite-plugin-pwa para Service Worker. Una sola base de código para mobile y desktop.         |
| **Estado local (juez)**   | IndexedDB vía Dexie.js 4.x                              | `grilla_cache` + `comando_queue`. Persistencia robusta en navegador.                        |
| **Sincronización**        | Cola de comandos custom (`useSyncQueue` + `useComandoQueue`) | Sincronización al recuperar conectividad. `SyncStatusBadge` como indicador visual.     |
| **Estado global**         | Zustand 5.x                                             | Estado de conexión, sesión y atleta activo.                                                 |
| **Fetching**              | TanStack Query 5.x                                      | Cache y revalidación de datos del servidor.                                                 |
| **Backend**               | Python 3.12 + FastAPI                                   | API REST. Monolito modular por Bounded Contexts.                                            |
| **Base de datos**         | SQLite — un archivo por BC (ADR-007)                    | Event Store + Read Models por BC. No justifica motor externo al volumen esperado.           |
| **Event Store**           | Tabla de eventos en SQLite por BC                       | Competencia y Notificaciones con Event Sourcing. Resto CRUD relacional.                     |
| **Notificaciones email**  | Resend                                                  | `resend_email_adapter.py` + adaptador de logging para entornos sin credenciales.            |
| **Notificaciones push**   | No implementado                                         | Puerto definido en dominio. Pendiente para versión futura.                                  |
| **Hosting**               | Fly.io (ADR-021)                                        | Despliegue en contenedor. Un solo servidor — escala modesta lo justifica.                   |
| **Autenticación**         | JWT (PyJWT) + modelo multi-rol (ADR-020)                | Mail + contraseña. Un usuario puede tener múltiples roles (organizador, juez, atleta).      |

---

## 9. Modelo de Seguridad

### 9.1 Roles y Permisos

> **Decisión arquitectónica (implementada — ADR-020):**  
> Modelo multi-rol: un usuario puede tener múltiples roles simultáneamente (organizador, juez, atleta). Los permisos efectivos dependen del rol activo en el contexto (torneo, disciplina).

| Rol              | Scope de permisos                            | Puede crear                                              | Restricciones clave                                              |
|------------------|----------------------------------------------|----------------------------------------------------------|------------------------------------------------------------------|
| **Organizador**  | Torneos que gestiona                         | Torneo, grillas, transiciones de fase, asignación de jueces | No puede modificar resultados de performances                 |
| **Juez**         | Disciplinas asignadas dentro de un torneo    | Performances, tarjetas, correcciones                     | Solo opera en disciplinas asignadas. Lectura al resto.           |
| **Atleta**       | Su propia información                        | Inscripción, declaración de AP                           | Solo ve resultados finales publicados                            |

### 9.2 Protección de Integridad de Resultados

| Nivel                   | Mecanismo                                                                                     | Efecto                                                                                           |
|-------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| **Evento inmutable**    | Event Store append-only. Los eventos no se modifican ni eliminan.                             | Cualquier cambio queda registrado como nuevo evento (`ResultadoCorregido`), preservando el historial. |
| **Cierre de disciplina** | Una vez cerrada la disciplina, el sistema bloquea la escritura de nuevos eventos de performance. | Ningún rol puede modificar resultados después del cierre.                                     |
| **Firma de cierre**     | Al cerrar una disciplina, se genera un hash (SHA-256) de todos los eventos.                   | Permite verificar post-facto que los eventos no fueron alterados.                                |

---

## 10. Estrategia de Integración

> **Decisión arquitectónica (implementada):**  
> Cada integración externa se encapsula detrás de un puerto (interfaz) del dominio con su correspondiente adaptador de infraestructura. El dominio nunca depende directamente de un sistema externo. Si el sistema externo cambia, solo cambia el adaptador.

| Integración                    | Puerto                                                    | Adaptador                                         | Estado                  |
|--------------------------------|-----------------------------------------------------------|---------------------------------------------------|-------------------------|
| **BD externa de atletas (FAAS)** | `RepositorioAtletasExterno.buscarPorDocumento()`        | Placeholder (retorna vacío). Protocolo no definido. | Pendiente (RF-IG-01)  |
| **Exportación de resultados**  | `ExportadorResultados.exportar(torneo, formato)`          | CSV/JSON implementado.                            | Implementado (AC-IO-02) |
| **Notificaciones email**       | `ServicioNotificacion.enviar(destinatario, plantilla, datos)` | Resend + adaptador logging.                  | Implementado (RF-NT-01) |
| **Notificaciones push**        | `ServicioNotificacionPush.enviar(dispositivo, mensaje)`   | Sin adaptador. Puerto definido.                   | Pendiente (AC-IO-04)    |
| **Cronometraje electrónico**   | `SensorCronometraje.onMarcaRegistrada(callback)`          | Sin implementación. Puerto definido.              | Futuro (AC-IO-01)       |
| **Pagos**                      | Sin puerto definido. Constancia manual.                   | N/A                                               | No requerido (AC-IO-03) |

---

## 11. Decisiones Pendientes al Cierre de v1.0.0

| Decisión                        | Estado                          | Impacto                            | Nota                                                                 |
|---------------------------------|---------------------------------|------------------------------------|----------------------------------------------------------------------|
| **Protocolo BD FAAS**           | Pendiente (RF-IG-01 a RF-IG-03) | Los atletas se registran manualmente | Puerto definido. Adaptador se implementa cuando se defina el protocolo. |
| **Notificaciones push**         | Pendiente (AC-IO-04)            | Solo se notifica por email         | Puerto definido. Adaptador pendiente de elección de servicio.        |
| **Cronometraje electrónico**    | Futuro (AC-IO-01)               | Sin integración de hardware        | Puerto definido. Sin plan de implementación definido.                |
