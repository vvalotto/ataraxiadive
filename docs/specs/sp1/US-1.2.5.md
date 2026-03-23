# US-1.2.5: Registrar DNS

**Estado**: `Pendiente`
**Incremento**: Inc 1.2 — El Dominio Habla
**Subproyecto**: SP1 — La Performance
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **registrar que un atleta no se presentó a su Official Top (DNS)**
para **cerrar el ciclo de actuación sin resultado y sin tarjeta**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Gestiona el ciclo de vida — transiciona de `Llamada` a `DNS` |
| Value Object | `EstadoPerformance` | Máquina de estados: `Llamada → DNS` |
| Domain Event | `DNSRegistrado` | Registra el DNS con el OT programado y el juez que lo registra |

### Lenguaje ubicuo relevante

- **DNS (Did Not Start)**: El atleta fue llamado al OT pero no se presentó para comenzar su performance.
- **`DNS`**: Estado final de la Performance — mutuamente excluyente con `ResultadoRegistrado`.
- **OT Programado**: Momento programado para el Official Top, registrado al llamar al atleta.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-P-08**: `RegistrarDNS` solo permitido si Performance en estado `Llamada`.
- **INV-P-09**: `DNSRegistrado` y `ResultadoRegistrado` son mutuamente excluyentes.

> INV-P-09 se satisface estructuralmente: si la Performance está en `Llamada`, el evento
> `ResultadoRegistrado` no puede haber ocurrido todavía (lo requiere). Validar INV-P-08 es
> suficiente para garantizar ambos invariantes.

### Precondición de estado

- Performance en estado `Llamada`.

### Operación principal

**Nombre**: `registrar_dns(registrado_por: str) -> None`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `Llamada` (INV-P-08). |
| **Postcondición** | Evento `DNSRegistrado` persiste en el stream. Performance pasa a `DNS`. |
| **Eventos generados** | `DNSRegistrado` |
| **Excepciones** | `EstadoInvalidoParaRegistrarDNS` (Performance no en `Llamada` — INV-P-08) |

**Nota de diseño:** `ot_programado` se extrae del estado interno de Performance
(almacenado al aplicar `AtletaLlamado`) — no se pasa como parámetro al método.

**Ejemplo concreto:**
```
Precondición:  Performance P001 en estado Llamada.
               OT programado: 2026-03-23T10:30:00.
Operación:     registrar_dns(registrado_por="juez-001")
Postcondición: Performance en estado DNS.
Evento:        DNSRegistrado{ performanceId=P001, participanteId=P-A01,
               disciplina="STA", otProgramado="2026-03-23T10:30:00",
               registradoPor="juez-001", registradoEn=<timestamp> }
```

---

## Criterios de aceptación (BDD)

Ver `tests/features/US-1.2.5-registrar-dns.feature` — 3 escenarios:
1. DNS exitoso desde estado Llamada
2. Rechazo: estado AnunciadaAP (INV-P-08)
3. Rechazo: estado ResultadoRegistrado (INV-P-09 / INV-P-08)

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente.

**Capas afectadas:**
- [x] Domain — nuevo evento `DNSRegistrado`, método `registrar_dns()` en `Performance`, nueva excepción `EstadoInvalidoParaRegistrarDNS`, almacenamiento de `_ot_programado` en `_apply_stored`
- [x] Application — `RegistrarDNSCommand` + `RegistrarDNSHandler`
- [ ] Infrastructure — no requiere cambios
- [ ] API — los endpoints se añaden en Inc 1.3

**Restricciones de métricas (pyproject.toml):**
- CBO actual Performance: 15/17 — +1 import (`DNSRegistrado`) → quedará 16/17
- WMC actual Performance: 27/36 — +~3 WMC (`registrar_dns()`: 1 check + 1 evento) → quedará ~30/36

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — Flujo 3 (Variante DNS)
- ADR-005: BCs estratégico (Competencia como Core Domain)
- ADR-008: Event Store append-only
- US mapeada desde: US-P-05 (ES Competencia)
- Incremento: Inc 1.2 en `docs/plans/sp1/SP1-candidatas.md`

---

*Redactado: 2026-03-23 — IEDD Capa 3 completa*
