---
title: "Vista de Dominio"
type: vista
last_updated: "2026-05-21"
sources:
  - wiki/conceptos/
  - wiki/arquitectura/
  - docs/dominio/01-dominio_torneos_apnea.md
  - docs/dominio/05-requerimientos_funcionales.md
---

# Vista de Dominio

> El sistema visto desde el negocio y el lenguaje ubicuo.

## Propósito

Responder preguntas sobre qué hace el sistema, qué conceptos maneja, quiénes son los actores y cómo se organizan las responsabilidades entre los Bounded Contexts. Es la vista de entrada para onboarding, domain experts y cualquier persona que necesita entender el sistema antes de modificarlo.

## Stakeholder principal

Domain expert, nuevo integrante del equipo, product owner.

---

## Preguntas características y recorridos

### 1. ¿Qué hace AtaraxiaDive?

AtaraxiaDive gestiona torneos de apnea competitiva: desde la inscripción de atletas hasta el registro de performances en tiempo real y la publicación de resultados.

**Recorrido:**
[[torneo]] (concepto) → [[arquitectura/bc-torneo]] → [[arquitectura/competencia]] → [[arquitectura/resultados]]

---

### 2. ¿Qué es una Performance y cuál es su ciclo de vida?

Una [[performance]] es la actuación de un atleta en una disciplina. Es el concepto más rico del dominio: puede terminar en válida (tarjeta blanca), descalificación (tarjeta roja), DNS o black-out.

**Recorrido:**
[[performance]] → [[tarjeta]] → [[anuncio]] → [[arquitectura/competencia]]

El aggregate `Performance` en el BC Competencia es el custodio del ciclo de vida completo. Las correcciones de resultado no mutan estado previo: agregan nuevos eventos.

---

### 3. ¿Qué diferencia hay entre Torneo, Competencia, Disciplina y Grilla?

| Concepto | Descripción |
|----------|-------------|
| [[torneo]] | El evento macro. Tiene sede, fecha, organizador. Pasa por etapas: Apertura → Inscripción → Preparación → Ejecución → Cierre. |
| Competencia | Una instancia de ejecución dentro del torneo para una disciplina específica. Gestionada por el BC [[arquitectura/competencia]]. |
| [[disciplina]] | Modalidad de prueba (tiempo o distancia). Tiene reglas de puntuación propias. |
| [[grilla]] | Planilla de salida: qué atleta compite en qué orden dentro de una disciplina. Se genera y puede ajustarse en Preparación. |

**Recorrido:**
[[disciplina]] → [[grilla]] → [[arquitectura/competencia]] → [[ADR-004-reglas-como-datos]]

---

### 4. ¿Quiénes son los actores y qué puede hacer cada uno?

El sistema define cuatro roles con responsabilidades diferenciadas. Ver [[roles]] para la tabla completa de acciones por etapa.

| Rol | Responsabilidad principal |
|-----|--------------------------|
| Organizador | Gestiona el [[torneo]]: crea, habilita inscripción, configura disciplinas, avanza etapas |
| Juez | Opera la [[disciplina]] en vivo: llama atletas, registra performances, emite [[tarjeta|tarjetas]] |
| Atleta | Se inscribe, declara [[anuncio|anuncios]] de marcas, compite |
| Administrador | Gestiona usuarios y acceso al sistema |

**Recorrido:**
[[roles]] → [[arquitectura/identidad]] → [[ADR-020-modelo-usuarios-roles]]

---

### 5. ¿Cómo se organizan las responsabilidades entre los seis Bounded Contexts?

El sistema aplica DDD estratégico: cada BC tiene una base de datos propia, sin joins cruzados. La integración es por eventos de dominio e interfaces de puerto explícitas.

| BC | Tipo DDD | Responsabilidad |
|----|----------|----------------|
| [[arquitectura/competencia]] | Core Domain | Grilla, performances, tarjetas, trazabilidad deportiva |
| [[arquitectura/bc-torneo]] | Supporting | Ciclo de vida del torneo, sede, disciplinas |
| [[arquitectura/registro]] | Supporting | Atletas, inscripciones, validación de participación |
| [[arquitectura/resultados]] | Supporting | Rankings derivados, overall, exportación |
| [[arquitectura/identidad]] | Generic | Usuarios, roles, JWT — cross-cutting |
| [[arquitectura/notificaciones]] | Generic | Ciclo de vida de notificaciones, exactly-once delivery |

**Recorrido:**
[[arquitectura/context-map]] → [[ADR-005-bounded-contexts-ddd-estrategico]] → [[ADR-006-estructura-bc-first]]

---

### 6. ¿Qué reglas del deporte de apnea impactan en el modelo?

Las reglas de apnea se modelan como datos (ADR-004), no como código hardcodeado. Esto permite actualizar la normativa sin cambiar el sistema.

Reglas clave con impacto directo en el modelo:
- El Juez asigna tarjeta blanca o roja con código de penalización explícito
- Las penalizaciones son acumulables: `rp_penalizado = rp_medido - Σpenalizaciones` ([[ADR-014-penalizaciones-acumulables]])
- Un DNS implica descalificación inmediata; un black-out registra la distancia alcanzada
- El [[anuncio]] previo es la marca declarada por el atleta, que condiciona el puntaje final

**Recorrido:**
[[ADR-004-reglas-como-datos]] → [[ADR-014-penalizaciones-acumulables]] → [[performance]] → [[tarjeta]]

---

## Páginas hub de esta vista

Estas páginas son el punto de entrada más frecuente para consultas de dominio:

| Página | Por qué es hub |
|--------|----------------|
| [[arquitectura/competencia]] | Core Domain; concentra la mayor lógica de negocio |
| [[performance]] | Concepto más rico; relaciona tarjeta, disciplina, atleta, anuncio |
| [[roles]] | Describe quién hace qué en cada etapa del torneo |
| [[grilla]] | Estructura de la competencia; punto de entrada a la ejecución |
| [[arquitectura/context-map]] | Mapa de integración entre los seis BCs |
| [[torneo]] (concepto) | Punto de partida del ciclo de vida completo |

---

## Conceptos del lenguaje ubicuo (glosario rápido)

| Término | Página |
|---------|--------|
| Performance | [[performance]] |
| Grilla | [[grilla]] |
| Tarjeta (blanca/roja) | [[tarjeta]] |
| Anuncio | [[anuncio]] |
| Disciplina | [[disciplina]] |
| Atleta | [[atleta]] |
| Torneo | [[torneo]] |
| Roles (Organizador, Juez, Atleta, Admin) | [[roles]] |
| Atributos de calidad del sistema | [[atributos-calidad]] |
