# US-5.1.6: Monitor de ejecución — vista del organizador durante la competencia

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1
**Bounded Context**: `frontend` (consume `competencia/api/` — endpoints existentes)
**Capas afectadas**: `frontend/src/pages/organizador/`, `frontend/src/api/competencia.ts`

---

## Descripción

Como **organizador**,
quiero **ver en tiempo real el progreso de cada disciplina en ejecución: cuántos atletas completaron, cuántos faltan, y la performance actual del juez**
para **monitorear el avance del torneo sin necesidad de intervenir en la operación del juez**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Query | `ObtenerProgresoHandler` | Devuelve `ProgresoCompetenciaDTO`: completados, pendientes, en_curso, performance_actual |
| Query | `ObtenerPerformanceActualHandler` | Atleta en `Llamada` en este momento |
| Query | `ObtenerProximasPerformancesHandler` | Próximos atletas por OT |
| Componente | `MonitorDisciplina` | Card por disciplina: barra de progreso + performance actual + próximos |
| Componente | `ProgressBar` | Visualización de completados / total |

### Lenguaje ubicuo relevante

- **En ejecución:** disciplina cuya competencia está en estado `EnEjecucion`.
- **Performance actual:** atleta actualmente en la ventana OT (estado `Llamada`).
- **Completado:** performance en estado `TarjetaAsignada` (Blanca, Blanca con Penalizaciones, Roja) o `DNSRegistrado`.
- **Progreso:** fracción de atletas completados sobre el total de la grilla.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.6-01:** El monitor solo muestra disciplinas cuyas competencias están en estado `EnEjecucion`.
- **INV-5.1.6-02:** La vista se refresca automáticamente cada 30 segundos — el organizador no opera la UI del juez desde esta pantalla.
- **INV-5.1.6-03:** Si todas las competencias del torneo están completas, el organizador ve un botón "Iniciar premiación".
- **INV-5.1.6-04:** El organizador puede ver el monitor en cualquier dispositivo — no requiere modo offline (es lectura pura).

### Operación principal — cargarProgreso

| | Descripción |
|---|---|
| **Precondición** | Torneo en estado `EnEjecucion`. Al menos una disciplina en competencia `EnEjecucion`. |
| **Postcondición** | Se muestran las cards de progreso con datos actuales. |

**Flujo de datos:**

```
1. GET /competencia?torneo_id={id} → lista de competencias del torneo
2. Filtrar: competencias en estado EnEjecucion
3. Para cada competencia en ejecución (en paralelo):
   GET /competencia/{id}/progreso → ProgresoCompetenciaDTO
   GET /competencia/{id}/performance/actual → performance en Llamada (null si libre)
   GET /competencia/{id}/proximas → próximos atletas
4. Armar MonitorDisciplina por cada competencia activa
```

**Ejemplo concreto:**

```
Torneo T1 EnEjecucion. DNF: 10 atletas totales, 6 completados, 1 en Llamada.
STA: 8 atletas, 2 completados, ninguno en Llamada.
Monitor muestra:
  DNF: [██████░░░░] 6/10 — En curso: García (OT 14:24) — Próximos: López, Ruiz
  STA: [██░░░░░░░░] 2/8  — En espera (próximo OT: 14:30 → López)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.6 — Monitor de ejecución del organizador

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR
    And el torneo "BA 2026" con id T1 está en estado EnEjecucion
    And la disciplina DNF tiene competencia C1 en estado EnEjecucion con 10 atletas
    And 6 atletas tienen performance en TarjetaAsignada
    And 1 atleta tiene performance en Llamada (García, OT 14:24)

  Scenario: organizador ve progreso en tiempo real de una disciplina
    When accede al tab "Ejecución" del torneo T1
    Then ve la card de DNF con barra de progreso "6 / 10"
    And ve "García" como atleta en curso con OT 14:24
    And ve los próximos 2 atletas

  Scenario: disciplina sin atleta en Llamada muestra estado de espera
    Given la disciplina STA tiene competencia C2 en EnEjecucion sin atleta en Llamada
    When el organizador ve la card de STA
    Then la sección "En curso" muestra "— En espera —"
    And se muestra el próximo atleta y su OT

  Scenario: refresco automático cada 30 segundos
    Given el organizador está en el tab "Ejecución"
    When pasan 30 segundos sin interacción
    Then la UI refrescar los datos llamando de nuevo a /competencia/{id}/progreso
    And los datos del monitor se actualizan sin recargar la página completa

  Scenario: todas las disciplinas completas habilita transición a premiación
    Given todas las competencias del torneo T1 están en estado CompetenciaFinalizada
    When el organizador accede al tab "Ejecución"
    Then ve el mensaje "Todas las disciplinas completadas"
    And ve el botón "Iniciar premiación" activo

  Scenario: sin disciplinas en ejecución muestra estado de espera
    Given no hay competencias en estado EnEjecucion en el torneo T1
    When el organizador accede al tab "Ejecución"
    Then ve el mensaje "Ninguna disciplina en ejecución"
```

---

## Impacto arquitectónico

- [x] No — consume endpoints existentes.

**Capa(s) afectadas:**
- [x] Frontend — componentes `MonitorDisciplina`, `ProgressBar`
- [x] Frontend — tab "Ejecución" en `DetalleTorneo` (US-5.1.2)
- [x] Frontend — `api/competencia.ts`: `obtenerProgreso()`, `obtenerPerformanceActual()`, `obtenerProximas()`

---

## Referencias

- Endpoint progreso: `src/competencia/api/router.py` — `GET /competencia/{id}/progreso` (`ObtenerProgresoHandler`)
- Endpoint performance actual: `GET /competencia/{id}/performance/actual` (`ObtenerPerformanceActualHandler`)
- Endpoint próximas: `GET /competencia/{id}/proximas` (`ObtenerProximasPerformancesHandler`)
- Endpoint por torneo: `GET /competencia?torneo_id=X` (`ObtenerCompetenciasPorTorneoHandler`)
- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.1`

---

## Notas de implementación

- **Refresco automático:** usar `setInterval` de 30s en el `useEffect` del componente; limpiar con `clearInterval` al desmontar.
- **`ProgresoCompetenciaDTO`:** ya existe en `competencia/application/queries/obtener_progreso.py` — verificar qué campos expone (completados, pendientes, en_curso).
- **Botón "Iniciar premiación":** delegar al `AccionesPanel` de US-5.1.2 — el monitor simplemente muestra el estado; el botón de transición vive en el panel de acciones global del torneo, no en el monitor.
- **Disciplinas concurrentes:** el torneo puede tener múltiples disciplinas en ejecución simultánea (multi-andarivel). Mostrar una card por disciplina en una grilla responsiva (1 columna en mobile, 2+ en desktop).
- **Sin acceso offline requerido:** el organizador monitorea desde un dispositivo con conexión. No cachear en IndexedDB.

---

*Redactado: 2026-04-20 — INC-5.1 Panel del Organizador*
