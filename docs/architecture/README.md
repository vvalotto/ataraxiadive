# Architecture Documentation

## Propósito

Esta carpeta concentra la **descripción arquitectónica vigente** de AtaraxiaDive.
Su objetivo es explicar **cómo está estructurada la solución**, cuáles son sus
componentes principales, cómo colaboran entre sí y qué restricciones de diseño
deben preservarse a medida que el sistema evoluciona.

No reemplaza a la documentación existente, sino que la organiza desde una
perspectiva arquitectónica y operativa.

## Alcance

La documentación de esta carpeta describe:

- la visión estructural del sistema;
- la descomposición en contenedores y bounded contexts;
- las interacciones relevantes entre contextos y componentes;
- las preocupaciones transversales de arquitectura;
- la arquitectura implementada o explícitamente objetivo para capacidades
  críticas como offline-first.

No documenta en detalle la exploración de dominio ni el razonamiento histórico
de cada decisión. Esos artefactos viven en otras carpetas.

## Relación con otras carpetas

- `docs/adr/`: registra **por qué** se tomó una decisión arquitectónica.
- `docs/design/`: describe el modelado de dominio y diseño estratégico/táctico.
- `docs/architecture/`: describe **cómo queda la solución** a partir de esas
  decisiones y modelos.

La regla práctica es:

- si el documento justifica una decisión, va en `adr/`;
- si modela dominio o bounded contexts desde DDD, va en `design/`;
- si describe la arquitectura actual o objetivo del sistema, va aquí.

## Estado actual

La arquitectura vigente, según ADRs actuales, se basa en:

- backend `FastAPI`;
- organización `BC-first`;
- arquitectura hexagonal por bounded context;
- `SQLite` con un archivo por bounded context;
- `Event Sourcing` en `Competencia` y `Notificaciones`;
- `React PWA` offline-first para la interfaz del juez.

## Estructura actual de esta carpeta

La estructura vigente es:

```text
docs/architecture/
  README.md
  STATUS.md
  01-system-context.md
  02-container-view.md
  03-bounded-contexts.md
  10-bc-competencia.md
  11-bc-torneo.md
  12-bc-registro.md
  13-bc-resultados.md
  14-bc-identidad.md
  15-bc-notificaciones.md
  20-context-map-integrations.md
  30-runtime-interactions.md
  40-cross-cutting-concerns.md
  50-offline-sync.md
  diagrams/
```

`STATUS.md` registra el estado de creación y mantenimiento de cada documento.

## Principios de documentación

Los documentos de esta carpeta deben seguir estos criterios:

- ser **descriptivos**, no aspiracionales, salvo que se indique explícitamente
  que representan arquitectura objetivo;
- evitar duplicar texto completo ya existente en `adr/` o `design/`;
- enlazar la fuente de verdad cuando una decisión o modelo ya exista;
- mantener separación entre vista estática, vista dinámica y preocupaciones
  transversales;
- acompañar cada especificación con el diagrama mínimo necesario.

## Diagramas

Se priorizarán estos tipos de diagramas:

- `C4` para contexto, contenedores y componentes;
- `sequence diagrams` para interacciones entre BCs y políticas de aplicación;
- `state diagrams` para ciclos de vida relevantes;
- diagramas de despliegue cuando la operación del sistema lo requiera.

Siempre que sea posible, los diagramas deberán mantenerse en archivos fuente
editables dentro de `docs/architecture/diagrams/`.

## Convención sugerida por documento

Cada especificación de arquitectura debería incluir, como mínimo:

- propósito del documento;
- alcance;
- fuentes relacionadas;
- decisiones o restricciones relevantes ya vigentes;
- vista o vistas arquitectónicas que describe;
- impactos o implicancias sobre implementación.

## Mantenimiento

No hay documentos pendientes registrados en `STATUS.md`.

Cuando cambie la estructura de esta carpeta, actualizar en conjunto:

1. este índice;
2. `docs/architecture/STATUS.md`;
3. los enlaces cruzados desde documentos canónicos como `README.md` y
   `CLAUDE.md`, si corresponde.
