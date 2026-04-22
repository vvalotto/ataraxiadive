# Integracion - US-5.1.10

## Estado

Waiver de automatizacion.

La US afecta el flujo `GET /torneos/{id}` / `GET /torneos` → normalizacion frontend →
`AccionesPanel`. El repo no tiene harness browser/DOM con mocks HTTP para validar el DOM.

## Flujo critico a validar manualmente

- `estado: "EJECUCION"` muestra `Volver a preparacion` e `Iniciar premiacion`.
- `estado: "En ejecución"` se normaliza a `EJECUCION`.
- `estado: "PREPARACION"` muestra `Iniciar ejecucion`.
- Estado desconocido falla de forma explicita con `ApiError`.

## Gates sustitutos

- `npm run build`
- `npm run lint`
