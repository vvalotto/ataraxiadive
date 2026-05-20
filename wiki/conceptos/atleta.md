---
title: "Atleta"
type: concepto
last_updated: "2026-05-20"
sources:
  - docs/dominio/01-dominio_torneos_apnea.md
---

# Atleta

Participante de un [[torneo]] de apnea. Actor del sistema con rol específico y datos de identidad deportiva.

## Datos de identidad

| Campo | Descripción |
|-------|-------------|
| Nombre y apellido | Identidad civil |
| Mail | Contacto y notificaciones |
| Fecha de nacimiento | Para cálculo de categoría |
| Teléfono | Contacto secundario |
| Categoría | Clasificación competitiva (define ranking separado) |
| Brevet | Número de licencia federativa del atleta |
| Tipo y número de documento | Identificación oficial |

## Inscripción en un torneo

El atleta puede:
1. **Registro nuevo:** ingresa todos sus datos.
2. **Registro existente:** ingresa su número de documento y el sistema recupera sus datos, que puede corregir.

Al inscribirse selecciona las [[disciplina|disciplinas]] en las que participará. Puede inscribirse en múltiples disciplinas.

Al confirmar la inscripción, el sistema envía un mail de confirmación.

## Acciones del atleta en el sistema

| Acción | Etapa del torneo |
|--------|-----------------|
| Inscribirse | Inscripción |
| Declarar [[anuncio]] (marca previa) | Preparación |
| Competir (pasivo — el [[roles|Juez]] registra) | Ejecución |

## Categoría

Clasifica al atleta para el ranking. Los resultados finales se calculan por [[disciplina]] **y** por categoría. El podio se determina por categoría.

## Relaciones

- Un atleta existe en el BC [[identidad]] (como usuario con rol atleta).
- Un atleta se inscribe en el BC [[registro]].
- Las [[performance|performances]] del atleta las registra el [[roles|Juez]] en el BC [[competencia]].
- El ranking del atleta lo calcula el BC [[resultados]].
