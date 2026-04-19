# US-ADJ-7.1: Comando `CorregirResultadoTrasDNS` — BUG-SP4-003

**Estado**: `Implementada`
**Iteración / Sprint**: SP-ADJ-07
**Tipo**: feat de dominio (bug fix)
**Agregado principal afectado**: `Performance`
**Bounded Context**: `competencia`

---

## Descripción (lenguaje de negocio)

Como **juez**,
quiero poder corregir un DNS registrado por error
para que el atleta no quede descalificado cuando en realidad sí se presentó al Official Top.

---

## Contexto del dominio

### Problema

La máquina de estados actual de `Performance` es:

```
AnunciadaAP → Llamada → ResultadoRegistrado → Ejecutada  (camino nominal)
AnunciadaAP → Llamada → DNS                              (atleta no se presentó)
```

`registrar_dns()` transiciona `Llamada → DNS`. Una vez en `DNS`, no existe ningún
comando que permita retomar el flujo. `corregir_resultado()` solo acepta `Ejecutada`
(INV-P-12), lo que hace irreversible un DNS registrado por error.

### Solución propuesta

Nuevo comando que abre la transición `DNS → ResultadoRegistrado`, emitiendo un evento
de auditoría explícito. Una vez en `ResultadoRegistrado`, el flujo normal de
`AsignarTarjeta` continúa sin cambios.

Estado final de la máquina de estados:

```
AnunciadaAP → Llamada → ResultadoRegistrado → Ejecutada  (camino nominal)
AnunciadaAP → Llamada → DNS                              (DNS correcto)
                         └→ ResultadoRegistrado           (corrección via CorregirResultadoTrasDNS)
                                  └→ Ejecutada            (AsignarTarjeta — sin cambios)
```

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Aggregate | `Performance` | Aplica el nuevo comando y emite el evento |
| Domain Event | `ResultadoCorregidoTrasDNS` | Nuevo — captura el resultado real y el motivo de corrección |
| Command | `CorregirResultadoTrasDNSCommand` | Nuevo |
| Command Handler | `CorregirResultadoTrasDNSHandler` | Nuevo |

---

## Especificación del comportamiento

### Precondición

- La Performance está en estado `DNS`.
- `valor_rp` ≥ 0 (puede ser 0 en BKO, pero BKO ya produce tarjeta roja automática).
- `motivo_correccion` no es vacío.
- `registrado_por` no es vacío.

### Postcondición

- Se emite el evento `ResultadoCorregidoTrasDNS` en el stream
  `performance-{competencia_id}-{atleta_id}-{disciplina}`.
- El estado de la Performance transiciona a `ResultadoRegistrado`.
- El handler de `AsignarTarjeta` puede ejecutarse a continuación sin cambios.
- Si `CorregirResultadoTrasDNS` es el último comando que deja una disciplina con
  todos sus atletas en `ResultadoRegistrado` o `Ejecutada`, la política P-08
  (`CompetenciaFinalizada`) **no** se dispara — se dispara solo cuando todos tienen
  `Ejecutada` (invariante existente, sin cambio).

### Invariantes

| ID | Invariante |
|----|-----------|
| INV-BUG-003-1 | Solo permitido desde estado `DNS` — cualquier otro estado lanza `EstadoInvalidoParaCorregirResultadoTrasDNS` |
| INV-BUG-003-2 | `motivo_correccion` obligatorio y no vacío |
| INV-BUG-003-3 | `valor_rp` ≥ 0 |
| INV-BUG-003-4 | `unidad` debe ser una `UnidadMedida` válida |

---

## Criterios de aceptación

```gherkin
Feature: Corrección de DNS registrado por error

  Background:
    Given una competencia en estado EnEjecucion con una disciplina configurada
    And un atleta en estado DNS en esa disciplina

  Scenario: Un juez corrige un DNS registrado por error
    When el juez ejecuta CorregirResultadoTrasDNS con valor_rp=50, unidad=metros, motivo="Error de juez"
    Then la Performance transiciona a estado ResultadoRegistrado
    And el event store contiene un evento ResultadoCorregidoTrasDNS con el valor_rp y el motivo
    And el juez puede ejecutar AsignarTarjeta a continuación

  Scenario: No se puede corregir DNS si la Performance está en Ejecutada
    Given un atleta en estado Ejecutada (ya completó el flujo normal)
    When el juez intenta ejecutar CorregirResultadoTrasDNS
    Then se lanza EstadoInvalidoParaCorregirResultadoTrasDNS
    And el estado de la Performance no cambia

  Scenario: No se puede corregir DNS si la Performance está en Llamada
    Given un atleta en estado Llamada
    When el juez intenta ejecutar CorregirResultadoTrasDNS
    Then se lanza EstadoInvalidoParaCorregirResultadoTrasDNS

  Scenario: El motivo de corrección es obligatorio
    Given un atleta en estado DNS
    When el juez ejecuta CorregirResultadoTrasDNS sin motivo_correccion (vacío o ausente)
    Then se lanza MotivoObligatorio
    And el estado de la Performance no cambia

  Scenario: Flujo completo desde DNS hasta Ejecutada
    When el juez ejecuta CorregirResultadoTrasDNS con valor_rp=60, unidad=metros, motivo="AP incorrecto"
    And el juez asigna tarjeta blanca al atleta
    Then la Performance está en estado Ejecutada con tarjeta blanca
    And el event store contiene: ResultadoCorregidoTrasDNS, TarjetaAsignada (en ese orden)
```

---

## Artefactos a crear / modificar

| Artefacto | Acción |
|-----------|--------|
| `src/competencia/domain/events/resultado_corregido_tras_dns.py` | Crear nuevo evento de dominio |
| `src/competencia/domain/aggregates/performance_events.py` | Agregar `crear_resultado_corregido_tras_dns()` factory |
| `src/competencia/domain/aggregates/performance.py` | Agregar método `corregir_resultado_tras_dns()` + transición de estado + nueva excepción |
| `src/competencia/domain/aggregates/performance_state.py` | Agregar `apply_resultado_corregido_tras_dns()` |
| `src/competencia/domain/exceptions.py` | Agregar `EstadoInvalidoParaCorregirResultadoTrasDNS` |
| `src/competencia/application/commands/corregir_resultado_tras_dns.py` | Crear command + handler |
| `src/competencia/api/router.py` | Agregar endpoint `POST /{competencia_id}/performances/{performance_id}/corregir-resultado-tras-dns` |
| `tests/unit/competencia/domain/test_performance_corregir_dns.py` | Tests unitarios |
| `tests/integration/competencia/test_corregir_resultado_tras_dns.py` | Test de integración HTTP |

---

## Evento de dominio: `ResultadoCorregidoTrasDNS`

```python
@dataclass(frozen=True)
class ResultadoCorregidoTrasDNS(DomainEvent):
    performance_id: str
    participante_id: str
    disciplina: str
    valor_rp: str          # Decimal serializado como str
    unidad: str            # UnidadMedida.value
    registrado_por: str
    motivo_correccion: str
```

El campo `motivo_correccion` lo diferencia de `ResultadoRegistrado` (evento nominal)
y garantiza la trazabilidad del cambio para auditoría.

---

## Endpoint HTTP

```
POST /competencias/{competencia_id}/performances/{performance_id}/corregir-resultado-tras-dns
```

**Body:**
```json
{
  "atleta_id": "uuid",
  "disciplina": "DNF",
  "valor_rp": "52.5",
  "unidad": "metros",
  "registrado_por": "juez-01",
  "motivo_correccion": "Atleta sí se presentó al OT — error de registro"
}
```

**Response:** `204 No Content`

**Errores:**
- `409 Conflict` + código `ESTADO_INVALIDO` si la Performance no está en `DNS`
- `422` si faltan campos obligatorios

---

## Notas de implementación

1. La transición de estado en `apply_resultado_corregido_tras_dns()` debe setear
   `self._estado = EstadoPerformance.ResultadoRegistrado` y guardar `valor_rp` en
   `self._rp_medido` — igual que `apply_resultado_registrado`.
2. El handler `AsignarTarjetaHandler` no requiere cambios: ya acepta `ResultadoRegistrado`.
3. La política P-08 (`CompetenciaFinalizada`) no se activa tras este comando — solo
   se activa desde `AsignarTarjetaHandler` o `RegistrarDNSHandler` como hasta ahora.
4. Verificar que `reconstitute()` aplique correctamente el nuevo evento al replay.

---

*Spec creada: 2026-04-19 — BUG-SP4-003 de BL-004*
