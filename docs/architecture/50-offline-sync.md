# 50 Offline Sync

## Propósito

Describir la arquitectura objetivo para operación offline-first de la interfaz
del juez y la sincronización posterior con el backend.

Esta vista se enfoca en cómo el sistema debe seguir operando cuando la
conectividad falla durante la competencia, preservando confirmación inmediata,
durabilidad local y sincronización ordenada al reconectar.

## Alcance

Incluye:

- estrategia offline-first de la PWA del juez;
- responsabilidades de cliente, almacenamiento local y backend;
- flujo de pre-carga, operación local, sync y reconciliación;
- relación entre offline y Event Sourcing de `Competencia`;
- riesgos y restricciones arquitectónicas.

No describe la UI completa del juez ni el detalle de componentes frontend.

## Fuentes

- `docs/adr/ADR-003-offline-first-pwa.md`
- `docs/dominio/02-arquitectura_referencia.md`
- `docs/dominio/04-estrategia_desarrollo.md`
- `docs/architecture/02-container-view.md`
- `docs/architecture/10-bc-competencia.md`
- `docs/architecture/30-runtime-interactions.md`

## Estado actual

El modo offline-first está decidido arquitectónicamente, pero todavía no aparece
materializado en el código del repositorio con Service Worker, IndexedDB ni cola
de sincronización.

Por lo tanto, este documento describe la **arquitectura objetivo vigente** para
SP4 y posteriores.

## Objetivo operativo

Durante la ejecución de una disciplina, el juez debe poder:

- abrir la grilla desde el celular;
- seguir operando sin conexión;
- recibir confirmación inmediata de cada acción;
- no perder datos si la red cae;
- sincronizar los eventos cuando la conectividad vuelva.

## Principio arquitectónico

La fuente de verdad del sistema sigue estando en el backend, pero la interfaz
del juez debe comportarse como **offline-first**.

Eso implica una separación clara:

- el backend conserva el estado canónico y la auditoría oficial;
- el dispositivo del juez mantiene una cola local durable de eventos pendientes;
- el usuario no depende de un round-trip al servidor para seguir operando.

## Modelo de operación

El flujo operativo objetivo es:

1. pre-cargar la disciplina en el dispositivo;
2. operar localmente sobre datos ya descargados;
3. persistir cada acción como evento local;
4. sincronizar en orden al recuperar conexión;
5. reconciliar respuesta del servidor y estado local.

## Diagrama de sincronización

```mermaid
sequenceDiagram
    actor J as Juez
    participant PWA as PWA del juez
    participant SW as Service Worker / Sync Manager
    participant IDB as IndexedDB
    participant API as Backend API
    participant COMP as BC Competencia

    J->>PWA: abre disciplina
    PWA->>API: solicita grilla + participantes + reglas
    API->>COMP: consulta read model / estado actual
    COMP-->>API: datos de disciplina
    API-->>PWA: snapshot inicial
    PWA->>IDB: guarda snapshot local

    J->>PWA: registra acción de competencia
    PWA->>IDB: persiste evento local pendiente
    IDB-->>PWA: confirmación inmediata

    alt con conexión
        PWA->>SW: solicita sync
        SW->>IDB: lee pendientes en orden
        SW->>API: envía eventos pendientes
        API->>COMP: valida y persiste en event store
        COMP-->>API: confirmado
        API-->>SW: ack
        SW->>IDB: marca sincronizado
    else sin conexión
        SW->>IDB: mantiene cola pendiente
        IDB-->>J: indicador offline
    end

    alt reconexión
        SW->>IDB: obtiene pendientes
        SW->>API: sincroniza en orden
        API-->>SW: ack / rechazo
        SW->>IDB: actualiza estado local
        SW-->>PWA: reconciliación
    end
```

## Datos pre-cargados en el dispositivo

Antes de operar offline, el cliente necesita un snapshot mínimo de trabajo:

- grilla de salida;
- participantes;
- disciplina y unidad;
- reglas operativas aplicables;
- estado actual de la competencia relevante para ese juez.

La pre-carga evita dependencias de lectura remota durante la operación local.

## Cola local de eventos

La arquitectura objetivo usa `IndexedDB` como almacenamiento local durable,
preferentemente mediante una abstracción como `Dexie.js`.

Cada acción del juez debe registrarse localmente como evento pendiente, por
ejemplo:

- llamar atleta;
- registrar resultado;
- registrar DNS;
- asignar tarjeta;
- corregir resultado, si la política lo permite.

## Relación con Event Sourcing

El modo offline encaja naturalmente con el modelo de `Competencia` porque el BC
ya persiste una secuencia de eventos inmutables.

La estrategia objetivo es:

- generar eventos primero en local;
- sincronizarlos al backend en el mismo orden lógico;
- persistirlos en el event store canónico del BC `Competencia`;
- reconstruir el estado oficial a partir de esa secuencia.

Esto reduce la fricción conceptual entre cliente offline y backend auditor.

## Reconciliación y conflictos

La reconciliación ocurre cuando el backend responde al lote sincronizado.

Reglas arquitectónicas previstas:

- el servidor sigue validando invariantes de dominio;
- el cliente no asume aceptación automática de todo evento local;
- si un evento es rechazado, el juez debe recibir una discrepancia visible;
- la resolución de conflicto se simplifica por la partición operativa por
  andarivel o disciplina.

La documentación de referencia menciona `last-write-wins por andarivel` como
estrategia inicial, apoyada en la baja probabilidad de conflicto real entre
jueces que operan ámbitos distintos.

## Responsabilidades por componente

### PWA del juez

- renderizar estado local;
- confirmar visualmente cada acción;
- trabajar aunque la red no esté disponible.

### Service Worker / Sync Manager

- detectar conectividad;
- encolar y despachar sincronización;
- reintentar sin intervención del usuario cuando sea posible.

### IndexedDB

- persistir snapshot local;
- persistir eventos pendientes;
- conservar estado de sincronización.

### Backend API y BC Competencia

- recibir eventos sincronizados;
- validar invariantes;
- persistir en el event store oficial;
- devolver acks o rechazos utilizables para reconciliación.

## Restricciones a preservar

- la operación local debe confirmar la acción sin esperar respuesta del
  servidor;
- el backend sigue siendo la fuente de verdad oficial;
- la cola local debe ser durable ante recarga o cierre del navegador;
- la sincronización debe respetar orden lógico de eventos;
- el modo offline no debe romper la auditabilidad del BC `Competencia`.

## Riesgos y trade-offs

- Service Workers y sincronización offline agregan complejidad de debugging.
- IndexedDB introduce una capa de persistencia adicional fuera del backend.
- Los conflictos simultáneos no desaparecen; solo se vuelven poco probables y
  deben resolverse explícitamente.
- La arquitectura es más robusta operativamente, pero exige una disciplina clara
  de eventos y reconciliación.

