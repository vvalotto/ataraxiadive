# Contexto Validado — US-4.3.2

| Campo | Valor |
|-------|-------|
| **US** | `US-4.3.2` — Flujo de performance — los 6 pasos conectados al backend |
| **Producto** | `frontend` + `competencia` |
| **Sprint** | SP4 |
| **Incremento** | INC-4.3 |
| **Puntos** | 5 (default operativo para tracking) |
| **Fecha** | 2026-04-11 |

---

## Resultado de Fase 0

La US está lista para avanzar a BDD y planificación, con varios ajustes que
deben respetar el código real del repo.

### Backend existente confirmado

- Los handlers ya existen:
  - `LlamarAtletaHandler`
  - `RegistrarResultadoHandler`
  - `AsignarTarjetaHandler`
- El router `src/competencia/api/router.py` **todavía no** expone:
  - `POST /competencia/{id}/llamar`
  - `POST /competencia/{id}/registrar-resultado`
  - `POST /competencia/{id}/asignar-tarjeta`
- `JuezDep` ya existe y puede reutilizarse para autenticar esos endpoints.

### Frontend existente confirmado

- `US-4.3.1` ya dejó:
  - `GrillaPage` stub
  - `useCompetenciaStore`
  - selección de `torneoId`, `competenciaId`, `disciplinaActiva`
- `frontend` usa React + Zustand + TanStack Query + Vite proxy.

### Hallazgos relevantes para el plan

1. **La spec no coincide 1:1 con los commands reales del backend**
   - `AsignarTarjetaCommand` usa `tipo: TipoTarjeta`, no `tarjeta`
   - `registrado_por` / `asignada_por` puede salir del JWT server-side
   - `UnidadMedida` y `TipoTarjeta` tienen valores concretos que deben reflejarse
     en los schemas HTTP

2. **La grilla del juez aún es stub**
   `US-4.3.2` no es solo wizard de pasos; también tiene que reemplazar
   `GrillaPage` por una pantalla funcional para seleccionar atleta y ver estado.

3. **Esta US toca dos capas reales**
   - backend API en `competencia/api/router.py`
   - frontend juez en `frontend/src/pages/juez/`

### Quality gates aplicables

- backend / repo:
  - tests focalizados de `competencia/api` y flujo impactado
  - `pytest` puntual donde haya cobertura útil
- frontend:
  - `npm run build`
  - `npm run lint`
- validación funcional:
  - manual UI con backend corriendo

---

## Conclusión

`US-4.3.2` puede continuar con:

1. feature BDD revisado contra contratos reales,
2. plan de implementación full-stack,
3. aprobación de Fase 2,
4. implementación.
