# Architecture Documentation Status

## Propósito

Este documento funciona como punto de control para la documentación de
arquitectura en `docs/architecture/`.

Sirve para:

- registrar la estructura documental definida;
- dejar explícito qué documentos ya existen;
- indicar qué documentos faltan;
- facilitar la reanudación del trabajo en futuras sesiones.

## Estructura documental definida

La estructura acordada para la documentación de arquitectura es la siguiente:

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

## Criterios acordados

- La carpeta `docs/architecture/` describe la **arquitectura vigente u objetivo**
  del sistema desde una perspectiva estructural y operativa.
- `docs/adr/` conserva el **por qué** de las decisiones.
- `docs/design/` conserva el modelado de dominio y diseño DDD.
- Los diagramas deben ser **consistentes con lo ya definido** en la documentación
  existente.
- Los diagramas nuevos deben escribirse en **Mermaid**.
- Se prioriza separar:
  - diagramas por bounded context;
  - mapa de contexto con foco en integraciones entre BCs.

## Documentos creados

| Documento | Estado | Observación |
|-----------|--------|-------------|
| `README.md` | Creado | Punto de entrada de la carpeta. |
| `01-system-context.md` | Creado | Vista de contexto del sistema. |
| `02-container-view.md` | Creado | Vista de contenedores. |
| `03-bounded-contexts.md` | Creado | Resumen de bounded contexts y enlaces a sus vistas detalladas. |
| `10-bc-competencia.md` | Creado | Arquitectura interna del BC core. |
| `11-bc-torneo.md` | Creado | Arquitectura vigente CRUD y ciclo de vida del torneo. |
| `12-bc-registro.md` | Creado | Atletas, inscripciones y ACL read-only hacia Torneo. |
| `13-bc-resultados.md` | Creado | Ranking por disciplina y ACL hacia Competencia. |
| `14-bc-identidad.md` | Creado | Usuarios, roles, autenticación y contrato JWT. |
| `15-bc-notificaciones.md` | Creado | Arquitectura objetivo del BC de notificaciones e idempotencia. |
| `20-context-map-integrations.md` | Creado | Integraciones entre bounded contexts. |
| `30-runtime-interactions.md` | Creado | Flujos síncronos y asíncronos entre BCs. |
| `40-cross-cutting-concerns.md` | Creado | Preocupaciones transversales y estado de adopción. |
| `50-offline-sync.md` | Creado | Arquitectura objetivo offline-first del juez y sincronización. |

## Documentos pendientes

| Documento | Estado | Prioridad |
|-----------|--------|-----------|
| Ninguno | — | — |

## Orden sugerido de trabajo

El orden sugerido para continuar es:

1. Revisar consistencia global de la carpeta
2. Ajustar referencias cruzadas si aparecen nuevos documentos
3. Mantener sincronizado con la evolución del código

## Convenciones ya fijadas

- `Servicio Push` se mantiene como abstracción genérica; no se fija proveedor
  concreto por ahora.
- Los documentos por BC deben enfocarse en:
  - responsabilidad;
  - estructura interna por capas;
  - aggregates y entidades principales;
  - puertos y adaptadores relevantes;
  - persistencia;
  - integraciones que cruzan la frontera del BC.
- El `Context Map` se documenta por separado del diseño interno de cada BC.

## Cómo retomar en otra sesión

Para continuar el trabajo en una nueva conversación, usar una instrucción como:

```text
Revisá docs/architecture/STATUS.md y seguimos con la documentación.
Quiero continuar con 13-bc-resultados.md.
```
