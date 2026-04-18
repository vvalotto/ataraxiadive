# US-4.3.4: Tarjeta amarilla — flujo de revisión y resolución desde la UI

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.3
**Bounded Context**: `frontend` + `competencia` (nuevo comando de dominio + endpoint HTTP)
**Capas afectadas**: `competencia/domain/`, `competencia/application/`, `competencia/api/router.py`, `frontend/`

---

## Descripción

Como **juez**,
quiero **asignar tarjeta amarilla cuando hay duda sobre el resultado de una performance y resolverla más tarde como blanca o roja**
para **cumplir con el reglamento CMAS 1.2.3.1 que permite hasta 3 minutos de deliberación antes de emitir la tarjeta definitiva**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Estado `EnRevision` — tarjeta amarilla asignada, esperando resolución |
| Command (nuevo) | `ResolverRevisionCommand` | Cierra la deliberación con resolución Blanca o Roja |
| Evento (nuevo) | `RevisionResuelta` | Registro de la decisión final post-deliberación |
| Estado (nuevo) | `EnRevision` | Estado intermedio entre ResultadoRegistrado y TarjetaAsignada |
| Página | `ResultadoAmarilla` | Pantalla S-10 — resolución inmediata post-asignación |
| Página | `RevisionDesdeGrilla` | Pantalla S-15 — resolución diferida desde la grilla |
| Componente | `AlertaRevision` | Card con botones Blanca y Roja, aviso de bloqueo de cierre |

### Lenguaje ubicuo relevante

- **Tarjeta Amarilla:** estado transitorio de revisión — la performance está en deliberación. No es un resultado final.
- **Revisión:** deliberación post-performance según CMAS 1.2.3.1. Máximo 3 minutos (timer informativo, no bloqueante).
- **Resolución:** decisión que cierra la revisión — puede ser Blanca (válida), Blanca con penalizaciones, o Roja (DQ).
- **EnRevision:** estado del aggregate Performance mientras hay una amarilla sin resolver.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.3.4-01:** `AsignarTarjeta(Amarilla)` solo es válido desde el estado `ResultadoRegistrado`.
- **INV-4.3.4-02:** `ResolverRevision(Blanca|Roja)` solo es válido desde el estado `EnRevision`.
- **INV-4.3.4-03:** Una Performance en `EnRevision` bloquea el cierre de la competencia (precondición de `CerrarCompetencia` — se aplica en INC-4.6).
- **INV-4.3.4-04:** La resolución como Roja requiere `motivo_dq` obligatorio.
- **INV-4.3.4-05:** Desde la grilla, las filas con estado `EnRevision` tienen borde amarillo y son tappables (→ S-15).

### Operación: AsignarTarjeta Amarilla

Usa el endpoint existente `POST /competencia/{id}/asignar-tarjeta` con `tarjeta = "Amarilla"`.
El backend mueve la Performance a `EnRevision`.

### Operación: ResolverRevision (nueva)

**Nombre**: `POST /competencia/{competencia_id}/resolver-revision`

| | Descripción |
|---|---|
| **Precondición** | Performance en `EnRevision`. `resolucion` ∈ {Blanca, Roja}. |
| **Postcondición** | Performance en `TarjetaAsignada`. Evento `RevisionResuelta{resolucion, motivo_dq?}` persistido. |
| **Excepciones** | 409 si Performance no está en `EnRevision`. 422 si `resolucion=Roja` sin `motivo_dq`. |

**Body:**
```json
{
  "participante_id": "uuid",
  "disciplina": "DNF",
  "resolucion": "Blanca",
  "penalizaciones": 0,
  "motivo_dq": null,
  "resuelto_por": "juez@ataraxia.com"
}
```

**Ejemplo concreto:**

```
Precondición:  García, Ana — ResultadoRegistrado con RP=75m
Paso 6:        POST asignar-tarjeta { tarjeta: Amarilla }
               → Performance en EnRevision
Pantalla S-10: juez delibera (timer informativo 3 min)
Resolución:    POST resolver-revision { resolucion: Blanca, penalizaciones: 0 }
               → RevisionResuelta{Blanca}
               → Performance en TarjetaAsignada (Blanca)
Postcondición: grilla muestra García con ✓ BLANCA, opacidad reducida
```

```
Precondición:  García, Ana — EnRevision (quedó pendiente, volvió a la grilla)
Pantalla S-15: juez accede desde la fila con borde amarillo
Resolución:    POST resolver-revision { resolucion: Roja, motivo_dq: NO_PROTOCOLO }
               → RevisionResuelta{Roja, NO_PROTOCOLO}
               → Performance en TarjetaAsignada (Roja)
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.3.4 — Tarjeta amarilla y resolución de revisión

  Background:
    Given el juez "juez@ataraxia.com" está autenticado
    And la competencia C1 de DNF está en EnEjecucion

  Scenario: asignar amarilla y resolver inmediatamente como blanca
    Given el juez está en el Paso 6 de García, Ana (RP=75m)
    When toca "TARJETA AMARILLA"
    Then el backend recibe asignar-tarjeta con tarjeta=Amarilla
    And ve la pantalla S-10 con alerta de revisión pendiente
    And ve los botones "RESOLVER → BLANCA" y "RESOLVER → ROJA"
    When toca "RESOLVER → BLANCA"
    Then el backend recibe POST /competencia/C1/resolver-revision con resolucion=Blanca
    And ve la pantalla S-09 "Performance completada — TARJETA BLANCA"
    And regresa a la grilla con García marcada como BLANCA

  Scenario: volver a la grilla con amarilla pendiente
    Given el juez asignó tarjeta amarilla a García, Ana
    When toca "Volver a la grilla (queda en revisión)"
    Then regresa a la grilla S-02
    And la fila de García muestra badge "⚠ REVISIÓN" con borde amarillo
    And la fila es tappable

  Scenario: resolver amarilla pendiente desde la grilla (S-15)
    Given García, Ana tiene una tarjeta amarilla pendiente en la grilla
    When el juez toca la fila de García
    Then ve la pantalla S-15 con los datos de García y los botones de resolución
    When toca "RESOLVER → ROJA" y selecciona motivo "NO_PROTOCOLO"
    Then el backend recibe resolver-revision con resolucion=Roja y motivo_dq=NO_PROTOCOLO
    And la grilla actualiza García a estado ✓ ROJA

  Scenario: resolver como roja sin motivo falla
    Given el juez está en S-10 con una amarilla de García
    When toca "RESOLVER → ROJA" sin seleccionar motivo
    Then el botón de confirmar está deshabilitado hasta seleccionar un MotivoDQ
```

---

## Impacto arquitectónico

- [x] Sí → nuevo estado de dominio + comando + evento en BC Competencia

**Cambios en el dominio:**
1. `Performance` — nuevo estado `EnRevision`
2. `Performance.asignar_tarjeta(Amarilla)` → transition a `EnRevision`
3. `Performance.resolver_revision(resolucion, motivo_dq?)` → nuevo método, transition a `TarjetaAsignada`
4. Nuevo evento `RevisionResuelta{resolucion: TipoTarjeta, motivo_dq: MotivoDQ | None}`
5. `ResolverRevisionCommand` + `ResolverRevisionHandler` en `application/commands/`

**Capa(s) afectadas:**
- [x] Domain — `Performance` (nuevo estado + método), `RevisionResuelta` (nuevo evento)
- [x] Application — `ResolverRevisionCommand` + `ResolverRevisionHandler`
- [x] Infrastructure / API — `competencia/api/router.py` (nuevo endpoint)
- [x] Frontend — `ResultadoAmarilla` (S-10), `RevisionDesdeGrilla` (S-15), `AlertaRevision`

---

## Referencias

- Wireframes: `docs/design/ux/wireframes-juez.md §S-10, S-15`
- Máquina de estados actual: `src/competencia/domain/aggregates/performance.py`
- Plan SP4 notas: `docs/plans/sp4/PLAN-SP4.md §Tarjeta amarilla — flujo de revisión`
- CMAS 1.2.3.1 — deliberación post-performance

---

## Notas de implementación

- **Nuevo estado `EnRevision`:** agregar a `PerformanceState` enum. La transición desde `ResultadoRegistrado` la dispara `asignar_tarjeta(Amarilla)`. La transición desde `EnRevision` la dispara `resolver_revision()`.
- **`RevisionResuelta`:** evento con campos `resolucion: TipoTarjeta`, `motivo_dq: MotivoDQ | None`, `penalizaciones: int`. Al reconstriuir, la Performance aplica la resolución como si fuera la tarjeta definitiva.
- **Grilla:** el adapter de estado debe reconocer `EnRevision` y mapearlo al badge `⚠ REVISIÓN` con borde amarillo.
- **Timer de 3 minutos:** informativo, no bloqueante. El juez puede resolver en cualquier momento. Mostrar en S-10 con colores (verde→amarillo→rojo conforme pasa el tiempo).
- **`CerrarCompetencia` (INC-4.6):** la precondición `all(p.estado != EnRevision)` se implementará cuando se exponga ese endpoint. Documentar INV-4.3.4-03 ahora; la validación efectiva va en INC-4.6.
- **`resolver_revision(Blanca con penalizaciones)`:** pasar `penalizaciones > 0` es válido si la disciplina lo permite. El RP final se calcula igual que en `AsignarTarjeta`.

---

*Redactado: 2026-04-11 — INC-4.3 Interfaz del Juez*
