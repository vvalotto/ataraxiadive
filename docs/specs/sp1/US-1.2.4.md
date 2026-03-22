# US-1.2.4: Asignar Tarjeta

**Estado**: `Pendiente`
**Incremento**: Inc 1.2 — El Dominio Habla
**Subproyecto**: SP1 — La Performance
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **asignar la tarjeta (blanca, amarilla o roja) a un atleta una vez registrado su resultado**
para **determinar la validez de la performance y cerrar el ciclo de actuación**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Gestiona el ciclo de vida — transiciona de `ResultadoRegistrado` a `Ejecutada` |
| Value Object | `TipoTarjeta` | Enum: Blanca / Amarilla / Roja |
| Value Object | `EstadoPerformance` | Máquina de estados: `ResultadoRegistrado → Ejecutada` |
| Domain Event | `TarjetaAsignada` | Registra el tipo de tarjeta, motivo (opcional) y juez asignante |

### Lenguaje ubicuo relevante

- **Tarjeta blanca**: Performance válida — el atleta completó sin penalización.
- **Tarjeta amarilla**: Penalización parcial con deducción — motivo obligatorio.
- **Tarjeta roja**: Descalificación — motivo obligatorio (ej: black-out, protocolo, superficie).
- **`Ejecutada`**: Estado final de la Performance tras la asignación de tarjeta.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-P-07**: `AsignarTarjeta` solo permitido si Performance en estado `ResultadoRegistrado`.
- **INV-P-10**: `TarjetaAsignada` es el estado final — no modificable (excepto vía `CorregirResultado`, SP2).
- **INV-P-11**: `motivo` es obligatorio si tarjeta = amarilla o roja.

### Precondición de estado

- Performance en estado `ResultadoRegistrado`.

### Operación principal

**Nombre**: `asignar_tarjeta(tipo: TipoTarjeta, asignada_por: str, motivo: str | None) -> None`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `ResultadoRegistrado` (INV-P-07). |
| **Postcondición** | Evento `TarjetaAsignada` persiste en el stream. Performance pasa a `Ejecutada`. |
| **Eventos generados** | `TarjetaAsignada` |
| **Excepciones** | `EstadoInvalidoParaAsignarTarjeta` (Performance no en `ResultadoRegistrado`) |
| | `MotivoObligatorio` (tarjeta amarilla o roja sin motivo — INV-P-11) |

**Ejemplo concreto — tarjeta blanca:**
```
Precondición:  Performance P001 en estado ResultadoRegistrado.
Operación:     asignar_tarjeta(tipo=Blanca, asignada_por="juez-001", motivo=None)
Postcondición: Performance en estado Ejecutada.
Evento:        TarjetaAsignada{ performanceId=P001, tipo=Blanca, motivo=null,
               asignadaPor="juez-001", asignadaEn=<timestamp> }
```

**Ejemplo concreto — tarjeta roja:**
```
Precondición:  Performance P001 en estado ResultadoRegistrado.
Operación:     asignar_tarjeta(tipo=Roja, asignada_por="juez-001", motivo="black-out")
Postcondición: Performance en estado Ejecutada.
Evento:        TarjetaAsignada{ performanceId=P001, tipo=Roja, motivo="black-out",
               asignadaPor="juez-001", asignadaEn=<timestamp> }
```

---

## Criterios de aceptación (BDD)

Ver `tests/features/US-1.2.4-asignar-tarjeta.feature` — 6 escenarios:
1. Tarjeta blanca exitosa
2. Tarjeta amarilla con motivo
3. Tarjeta roja con motivo
4. Rechazo: amarilla sin motivo (INV-P-11)
5. Rechazo: roja sin motivo (INV-P-11)
6. Rechazo: estado incorrecto (INV-P-07)

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente.

**Capas afectadas:**
- [x] Domain — nuevo VO `TipoTarjeta`, nuevo evento `TarjetaAsignada`, método `asignar_tarjeta()` en `Performance`, nuevas excepciones `EstadoInvalidoParaAsignarTarjeta` y `MotivoObligatorio`
- [x] Application — `AsignarTarjetaCommand` + `AsignarTarjetaHandler`
- [ ] Infrastructure — no requiere cambios
- [ ] API — los endpoints se añaden en Inc 1.3

**Restricciones de métricas (pyproject.toml):**
- CBO actual Performance: 13/14 — 1 import disponible (`TipoTarjeta` reutiliza el mismo módulo)
- WMC actual Performance: ~21/25 — 4 puntos disponibles (método `asignar_tarjeta` ≈ 3 ramas)

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 3
- ADR-005: BCs estratégico (Competencia como Core Domain)
- ADR-008: Event Store append-only
- US mapeada desde: US-P-04 (ES Competencia)
- Incremento: Inc 1.2 en `docs/plans/sp1/SP1-candidatas.md`

---

*Redactado: 2026-03-22 — IEDD Capa 3 completa*
