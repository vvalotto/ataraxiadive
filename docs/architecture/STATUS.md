# Architecture Documentation — Estado por documento

> Estado documental: vigente
> Fuente de verdad para: estado de creación y mantenimiento de los documentos de `docs/architecture/`
> Última actualización: 2026-05-31

Registra el estado de cada documento de la carpeta. La estructura de carpeta y los
criterios de la documentación viven en [`README.md`](README.md) (no se repiten aquí).

## Documentos

| Documento | Estado | Observación |
|-----------|--------|-------------|
| `README.md` | Creado | Punto de entrada, alcance y estructura de la carpeta. |
| `01-system-context.md` | Creado | Vista de contexto del sistema. |
| `02-container-view.md` | Creado | Vista de contenedores. |
| `03-bounded-contexts.md` | Creado | Resumen de bounded contexts y enlaces a sus vistas detalladas. |
| `10-bc-competencia.md` | Creado | Arquitectura interna del BC core. |
| `11-bc-torneo.md` | Creado | CRUD y ciclo de vida del torneo. |
| `12-bc-registro.md` | Creado | Atletas, inscripciones y ACL read-only hacia Torneo. |
| `13-bc-resultados.md` | Creado | Ranking por disciplina y ACL hacia Competencia. |
| `14-bc-identidad.md` | Creado | Usuarios, roles, autenticación y contrato JWT. |
| `15-bc-notificaciones.md` | Creado | Notificaciones e idempotencia. |
| `20-context-map-integrations.md` | Creado | Integraciones entre bounded contexts. |
| `30-runtime-interactions.md` | Creado | Flujos síncronos y asíncronos entre BCs. |
| `40-cross-cutting-concerns.md` | Creado | Preocupaciones transversales y estado de adopción. |
| `50-offline-sync.md` | Creado | Arquitectura objetivo offline-first del juez y sincronización. |
| `60-deployment-view.md` | Creado | Vista de despliegue en Fly.io — Dockerfile multi-stage, volumen SQLite. |

No hay documentos pendientes.

## Mantenimiento

Cuando cambie la estructura de la carpeta, actualizar en conjunto:

1. el árbol en [`README.md`](README.md);
2. esta tabla de estado;
3. los enlaces cruzados desde documentos canónicos (`README.md` raíz, `CLAUDE.md`) si corresponde.
