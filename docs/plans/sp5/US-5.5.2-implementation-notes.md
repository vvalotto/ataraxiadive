# US-5.5.2 - Implementation Notes

**Fecha:** 2026-04-26
**Estado:** IMPLEMENTADA

---

## Decision tecnica aplicada

La vista del organizador dejo de reconstruir AP desde la grilla y paso a consumir una consulta enriquecida de Registro:

- `GET /registro/torneos/{torneo_id}/inscriptos-detalle`

La consulta compone:

- inscripciones activas del torneo;
- datos visibles del atleta desde Registro;
- disciplinas por inscripcion;
- AP por disciplina leyendo streams `performance-*` de las competencias asociadas al torneo.

Esto evita el falso negativo que existia cuando todavia no habia grilla generada.

---

## Cambios backend

### Registro

- `ListarInscriptosHandler` ahora usa solo inscripciones activas.
- `SQLiteInscripcionRepository` incorpora `find_active_by_torneo`.
- Se agrega endpoint enriquecido `inscriptos-detalle` para organizador.

### Competencia

- No se altero la semantica de `PerformancesAPAdapter`.
- Para evitar regresiones sobre generacion de grilla, la lectura de AP para esta US se hace localmente reconstituyendo `Performance` desde event store.

---

## Cambios frontend

- `InscriptosPanel` deja de hacer `N+1` ad hoc entre atletas, competencias y grillas.
- `TablaInscriptos` muestra:
  - atleta,
  - club,
  - categoria,
  - estado de inscripcion,
  - estado AP por disciplina.
- `EstadoAPBadge` ahora usa labels de producto:
  - `AP pendiente`
  - `AP declarado`
  - `AP cerrado`
- `DetalleTorneoPage` muestra banner de solo lectura cuando el torneo ya no esta en `INSCRIPCION_ABIERTA`.

---

## Desvios y limites

- El shell global del organizador sigue sin reflejar por completo el prototipo dark con navbar superior sticky en todo el panel.
- Esta US corrige la vista de `Torneo > Inscriptos` y su semantica operativa, no el rediseño integral del rol.
