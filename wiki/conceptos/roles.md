---
title: "Roles del sistema"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Roles del sistema

AtaraxiaDive define cuatro roles con responsabilidades y permisos diferenciados.

## Organizador

Responsable de la gestión del [[torneo]].

| Acción | Etapa |
|--------|-------|
| Crear torneo | Apertura |
| Habilitar inscripción | Apertura |
| Cerrar inscripción | Preparación |
| Abrir periodo de preparación | Preparación |
| Configurar [[disciplina|disciplinas]] y generar [[grilla|grillas]] | Preparación |
| Avanzar entre etapas del torneo | Todo el ciclo |
| Pedir anuncios a atletas | Preparación |

## Juez

Responsable de la ejecución de una [[disciplina]].

| Acción | Descripción |
|--------|-------------|
| Abrir disciplina | Inicia la ejecución de una disciplina |
| Llamar atleta | Convoca al siguiente [[atleta]] según la [[grilla]] |
| Confirmar presencia | Verifica que el atleta esté listo |
| Iniciar performance | Arranca el cronómetro |
| Confirmar finalización | Registra el fin de la [[performance]] |
| Emitir tarjeta | Blanca (válida) o roja (descalificación + código) |
| Ingresar valor | Distancia, si la disciplina lo requiere |

Se asigna un juez por [[disciplina]] de la [[competencia]].

## Atleta

Participante de las competencias.

| Acción | Etapa |
|--------|-------|
| Inscribirse en el torneo | Inscripción |
| Declarar [[anuncio|anuncios]] de marcas | Preparación |
| Competir (pasivo — el Juez registra) | Ejecución |

Ver [[atleta]] para datos de identidad y detalles de inscripción.

## Administrador

Usuario con privilegios de gestión del sistema.

| Acción | Descripción |
|--------|-------------|
| Crear usuarios Organizador | Gestión de acceso |
| Crear usuarios Juez | Gestión de acceso |
| Gestionar sistema | Configuración general |

Los [[atleta|atletas]] crean su propio usuario individualmente.

## Relaciones

- Los roles están implementados en el BC [[identidad]].
- Ver [[ADR-020-modelo-usuarios-roles]] para la decisión de arquitectura sobre el modelo de roles.
