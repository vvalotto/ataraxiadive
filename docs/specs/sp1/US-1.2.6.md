# US-1.2.6: Corregir Resultado

**Estado**: `Pendiente`
**Incremento**: Inc 1.2 — El Dominio Habla
**Subproyecto**: SP1 — La Performance
**Agregado principal**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero **corregir el resultado registrado de un atleta ya ejecutado**
para **rectificar un error de registro manteniendo la trazabilidad completa**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Gestiona el ciclo de vida — acepta corrección solo desde `Ejecutada` |
| Value Object | `EstadoPerformance` | Máquina de estados: `Ejecutada` permanece tras corrección |
| Domain Event | `ResultadoCorregido` | Registra el RP corregido con el valor anterior, motivo y juez |

### Lenguaje ubicuo relevante

- **CorregirResultado**: Acción del juez de rectificar un RP ya registrado tras la asignación de tarjeta.
- **Ejecutada**: Estado final nominal de la Performance (AP → Llamada → ResultadoRegistrado → Ejecutada).
- **motivo**: Razón obligatoria de la corrección — sin excepción (INV-P-12).
- **ResultadoCorregido**: Evento que registra el valor corregido; no muta eventos anteriores.

---

## Especificación del comportamiento

### Invariantes del aggregate

- **INV-P-12**: `CorregirResultado` solo permitido si Performance en estado `Ejecutada`.
- **INV-P-13**: No permitido si Performance en estado `DNS` (no hay resultado que corregir).
- **INV-P-15** *(diferido SP3)*: la corrección debe ocurrir dentro de la ventana de impugnación
  (`ventanaImpugnacion` configurada en BC Torneo — no disponible en SP1).

> INV-P-13 se satisface estructuralmente: verificar `Ejecutada` (INV-P-12) es suficiente,
> ya que `DNS` es un estado terminal diferente e irreconciliable con `Ejecutada`.

> **motivo obligatorio**: a diferencia de la tarjeta (donde solo Amarilla/Roja requieren motivo),
> toda corrección de resultado requiere motivo sin excepción.

### Precondición de estado

- Performance en estado `Ejecutada`.

### Operación principal

**Nombre**: `corregir_resultado(valor_rp: Decimal, unidad: UnidadMedida, registrado_por: str, motivo: str) -> None`

| | Descripción |
|---|---|
| **Precondición** | Performance en estado `Ejecutada` (INV-P-12). |
| **Postcondición** | Evento `ResultadoCorregido` persiste. `self._rp` actualizado. Estado permanece `Ejecutada`. |
| **Eventos generados** | `ResultadoCorregido` |
| **Excepciones** | `EstadoInvalidoParaCorregirResultado` (Performance no en `Ejecutada` — INV-P-12/13) |
| | `MotivoObligatorio` (motivo ausente o vacío — INV-P-12) |

**Ejemplo concreto:**
```
Precondición:  Performance P001 en estado Ejecutada.
               RP actual: 90.5 metros. Tarjeta: Blanca.
Operación:     corregir_resultado(valor_rp=Decimal("91.0"), unidad=Metros,
                   registrado_por="juez-001", motivo="Error de lectura en planilla")
Postcondición: Performance en estado Ejecutada (sin cambio).
               self._rp = Decimal("91.0")
Evento:        ResultadoCorregido{ performanceId=P001, participanteId=P-A01,
               disciplina="STA", valorRpAnterior="90.5", valorRpNuevo="91.0",
               unidad="Metros", motivo="Error de lectura en planilla",
               registradoPor="juez-001", corregidoEn=<timestamp> }
```

---

## Criterios de aceptación (BDD)

Ver `tests/features/US-1.2.6-corregir-resultado.feature` — 3 escenarios:
1. Corrección exitosa desde estado Ejecutada
2. Rechazo: estado AnunciadaAP/Llamada/ResultadoRegistrado/DNS (INV-P-12/13)
3. Rechazo: motivo ausente (INV-P-12)

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — se implementa con la arquitectura existente.

**Capas afectadas:**
- [x] Domain — nuevo evento `ResultadoCorregido`, método `corregir_resultado()` en `Performance`,
  nueva excepción `EstadoInvalidoParaCorregirResultado`
- [x] Application — `CorregirResultadoCommand` + `CorregirResultadoHandler`
- [ ] Infrastructure — no requiere cambios
- [ ] API — los endpoints se añaden en Inc 1.3

**Restricciones de métricas (pyproject.toml):**
- CBO actual Performance: 19/20 — +1 import (`ResultadoCorregido`) +1 excepción inline → quedará 21 → ajustar `max_cbo=22`
- WMC actual Performance: ~30/36 — +~4 WMC (`corregir_resultado()`: 2 checks + 1 evento) → quedará ~34/36

---

## Referencias

- Modelo de dominio: `docs/design/domain-model.md` §2.2 — Performance
- Event Storming Competencia: `docs/design/event-storming-competencia.md` — CorregirResultado
- ADR-005: BCs estratégico (Competencia como Core Domain)
- ADR-008: Event Store append-only
- US mapeada desde: US-P-06 (ES Competencia)
- Incremento: Inc 1.2 en `docs/plans/sp1/SP1-candidatas.md`

---

*Redactado: 2026-03-23 — IEDD Capa 3 completa*
