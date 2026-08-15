---
title: "Snapshot de Calidad — BL-007 / v1.0.2 (cierre del proyecto)"
type: salud
last_updated: "2026-05-30"
sources:
  - .cm/baselines/BL-007.md
  - .cm/baselines/BL-007-report.json
---

# Snapshot de Calidad — BL-007 / v1.0.2 (cierre del proyecto)

> Síntesis de los tres quality gates al cierre de SP7 + SP-ADJ-12 (2026-05-30, tag `v1.0.2`,
> extendido a `v1.0.5` por el addendum documental SP-ADJ-13 — sin cambios de arquitectura,
> estas métricas siguen vigentes).
> Para el snapshot anterior → [[calidad-BL-006]].
> Para el estado unificado del proyecto → [[proyecto]].

---

## Veredicto global

| Gate | Resultado | should_block |
|------|-----------|:---:|
| DesignReviewer (SP-ADJ-12) | 0 CRITICAL · 296 WARNING | false |
| Tests suite completa | 1049 passed · 0 failed | — |
| ArchitectAnalyst (BL-007) | 3 CRITICAL (DistanceAnalyzer) · 62 WARNING | false |

**0 CRITICAL de DesignReviewer en todos los SPs, hasta el cierre.** `should_block=false` en todos los gates.

---

## Evolución WARNING (DesignReviewer)

| Baseline | CRITICAL | WARNING | Δ | Evento |
|----------|:---:|:---:|:---:|--------|
| BL-005 (SP5) | 0 | 256 | +59 | Portales completos + FAAS + rankings |
| BL-006 post-INC-6.4 | 0 | 253 | −3 | Refactoring deuda técnica SP6 |
| BL-006 post-SP-ADJ-11 | 0 | 287 | +34 | Modelo multi-rol (complejidad nueva) |
| BL-007 (SP7 + SP-ADJ-12) | 0 | **296** | +9 | Handlers agregar/quitar rol (identidad) + `estado_aceptacion` (registro) |

Ver el detalle completo por BC y por tipo de smell en `.cm/baselines/BL-007-report.json` — no reingerido página por página en esta síntesis; disponible como fuente si hace falta profundizar.

---

## ArchitectAnalyst — decisiones técnicas de BL-007

### AA-05 — `identidad` D=0.66 ↑

SP-ADJ-12 agregó `AgregarRolHandler` / `QuitarRolHandler` y endpoints en `identidad/api/router.py`.
Código concreto sin incremento proporcional de abstracciones → D sube levemente (+0.01 vs BL-006).

**Decisión:** Aceptado. El incremento es marginal y el código añadido es la implementación
correcta del patrón hexagonal. **Criterio de intervención:** si D(identidad) > 0.70 en BL-008.

### AA-06 — `registro` D=0.59 ↑

SP-ADJ-12 agregó el enum `EstadoAceptacion`, campo en el aggregate `Inscripcion`, migración en
`SQLiteInscripcionRepository`, `CambiarAceptacionInscripcionHandler` y dos endpoints nuevos.
Mismo patrón que en BL-006: nueva entidad completa con stack infra/app → D sube.

**Decisión:** Aceptado. El patrón es correcto (domain → application → infra); el D refleja
crecimiento real del BC, no deuda arquitectónica. **Criterio de intervención:** si D(registro) > 0.65 en BL-008.

### AA-07 — `shared` D=0.63, estable

Sin cambios en `shared/` durante SP-ADJ-12. La decisión de BL-006 (AA-04, diferir
reestructuración) se mantiene, ahora diferida post-v1.1.

---

## Tests

**1049 tests passed · 0 failed** — suite completa al cierre de BL-007. No se registró
regresión respecto de la cobertura validada en BL-006.

---

## Decisiones de aceptación de deuda (vigentes al cierre)

| ID | Hallazgo | Clasificación | Acción |
|----|----------|---------------|--------|
| AA-05 | `identidad` D=0.66 | Zone of Pain — CRUD genérico con nuevos handlers | Aceptado — revisar en BL-008 si D > 0.70 |
| AA-06 | `registro` D=0.59 | Nueva entidad completa (`estado_aceptacion`) | Aceptado — revisar en BL-008 si D > 0.65 |
| AA-07 | `shared` D=0.63 | Fan-out estructural cross-BC (heredado de AA-04) | Diferido post-v1.1 |
| DR-01 | `RankingCompetencia` LCOM=2 | Falso positivo Event Sourcing | Ninguna — patrón aceptado (heredado BL-006) |
| ARCH-03 | ACL en `resultados/infrastructure` | ACL legítimo en capa infra | Ninguna — patrón DDD aceptado (heredado BL-006) |

---

## Cierre del proyecto

Con BL-007 se cierra SP7 (INC-7.1 despliegue Fly.io + INC-7.2 manual de usuario), más
SP-ADJ-12 (correcciones post-despliegue) y el addendum SP-ADJ-13 (fixes de UI y revisión
del manual contra producción, tags `v1.0.4` y `v1.0.5`, sin cambios de arquitectura). No hay
subproyecto siguiente planificado — el proyecto queda en estado cerrado a partir de esta
baseline.
