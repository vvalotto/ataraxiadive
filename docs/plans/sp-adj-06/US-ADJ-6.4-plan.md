# Plan Técnico — US-ADJ-6.4
## Refactor políticas P-10 y P-11 — duplicación y cohesión

*Generado: 2026-04-17 — Fase 2 /implement-us US-ADJ-6.4*

---

## Situación actual

Código coincide exactamente con el spec.

- `_registrar_fallo_sin_email` duplicado con firmas distintas en P-10 (recibe evento) y P-11 (recibe str)
- `_evento_fuente_id` en P-11 no usa `self` — debe ser `@staticmethod`

---

## Solución

### T1 — Crear `_helpers.py` con función compartida

```
src/notificaciones/application/policies/_helpers.py
```

Función `registrar_fallo_sin_email(evento_fuente_id, repository)` con la lógica
de la versión P-11 (la más limpia — recibe `str`, desacoplada del objeto evento).

Imports necesarios: `Notificacion`, `NotificacionRepository`, `EventoFuenteId`,
`persistir_eventos_pendientes`.

### T2 — Actualizar P-10

- Reemplazar `self._registrar_fallo_sin_email(evento)` por
  `await registrar_fallo_sin_email(evento.id, self._repository)`
- Eliminar método `_registrar_fallo_sin_email` del handler
- Limpiar imports huérfanos: `Notificacion`, `EventoFuenteId`, `persistir_eventos_pendientes`

### T3 — Actualizar P-11

- Reemplazar `self._registrar_fallo_sin_email(evento_fuente_id)` por
  `await registrar_fallo_sin_email(evento_fuente_id, self._repository)`
- Eliminar método `_registrar_fallo_sin_email` del handler
- Agregar `@staticmethod` a `_evento_fuente_id`
- Limpiar imports huérfanos: `Notificacion`, `EventoFuenteId`, `persistir_eventos_pendientes`

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `src/notificaciones/application/policies/_helpers.py` | Nuevo — función compartida |
| `src/notificaciones/application/policies/politica_p10.py` | T2 |
| `src/notificaciones/application/policies/politica_p11.py` | T3 |

## Estimación

| Tarea | Estimado |
|-------|----------|
| T1 | 5 min |
| T2 + T3 | 10 min |
| Tests + CodeGuard | 10 min |
| **Total** | **25 min** |
