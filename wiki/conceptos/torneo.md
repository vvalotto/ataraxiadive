---
title: "Torneo"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Torneo

Evento competitivo de apnea que agrupa una o más [[disciplina|disciplinas]], organizado en fases secuenciales bajo responsabilidad de un [[roles|Organizador]].

## Datos del torneo

| Campo | Descripción |
|-------|-------------|
| Nombre | Identificación del evento |
| Ciudad | Lugar de realización |
| Fechas inicio/fin | Rango de duración |
| Disciplinas | Selección de pruebas que se realizarán |

## Ciclo de vida (etapas)

```
Apertura → Inscripción → Preparación → Ejecución → Premiación → Cierre
```

El [[roles|Organizador]] es el único responsable de avanzar entre etapas.

| Etapa | Habilita |
|-------|---------|
| **Apertura** | Configuración del torneo, habilitación de inscripciones |
| **Inscripción** | Registro de [[atleta|atletas]] con datos y disciplinas elegidas |
| **Preparación** | Recolección de [[anuncio|anuncios]] de marcas; armado de [[grilla|grillas]] |
| **Ejecución** | Competencia activa disciplina a disciplina |
| **Premiación** | Cálculo de resultados, podio por disciplina y categoría |
| **Cierre** | Fin del torneo |

## Relaciones

- Un torneo contiene múltiples [[disciplina|disciplinas]].
- Un torneo tiene múltiples [[atleta|atletas]] inscriptos.
- Cada disciplina tiene su propia [[grilla]] de salida.
- Cada atleta produce una [[performance]] por disciplina en la que compite.

## Nota documental

> Este concepto fue elicitado en la fase inicial del proyecto (feb 2026).
> La implementación vigente está distribuida en los BCs [[competencia]] y [[torneo]].
