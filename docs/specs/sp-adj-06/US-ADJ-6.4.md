# US-ADJ-6.4: Refactor políticas P-10 y P-11 — duplicación y cohesión

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-06
**Agregado principal afectado**: `Notificacion`
**Bounded Context**: `notificaciones`

---

## Descripción (lenguaje de negocio)

Como **equipo de desarrollo**,
quiero eliminar la duplicación de `_registrar_fallo_sin_email` entre las políticas P-10 y P-11
y agregar `@staticmethod` al método `_evento_fuente_id` de P-11
para mejorar la consistencia y cohesión del BC Notificaciones.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Política de aplicación | `PoliticaP10Handler` | Maneja `InscripcionConfirmada` → email al atleta |
| Política de aplicación | `PoliticaP11Handler` | Maneja `ResultadosPublicados` → email a cada atleta participante |

### Hallazgos que originan esta US

De `02-analisis-bc-notificaciones.md`:

**DES-01 — `_registrar_fallo_sin_email` duplicado:**

```python
# politica_p10.py
async def _registrar_fallo_sin_email(self, evento: InscripcionConfirmada) -> None:
    if await self._repository.exists_success_by_evento_fuente_id(evento.id):
        return
    aggregate = Notificacion.registrar_fallo_de_solicitud(
        evento_fuente_id=EventoFuenteId(evento.id),
        motivo="destinatario_sin_email",
    )
    await persistir_eventos_pendientes(self._repository, aggregate)

# politica_p11.py — lógica idéntica, firma diferente
async def _registrar_fallo_sin_email(self, evento_fuente_id: str) -> None:
    if await self._repository.exists_success_by_evento_fuente_id(evento_fuente_id):
        return
    aggregate = Notificacion.registrar_fallo_de_solicitud(
        evento_fuente_id=EventoFuenteId(evento_fuente_id),
        motivo="destinatario_sin_email",
    )
    await persistir_eventos_pendientes(self._repository, aggregate)
```

La versión de P-11 (que recibe `str`) es la más limpia porque desacopla la función del
objeto evento. Con cada nueva política (P-12, P-13...) la duplicación crece linealmente.

**DES-02 — `_evento_fuente_id` sin `@staticmethod`:**

```python
# politica_p11.py
def _evento_fuente_id(
    self,
    evento: ResultadosPublicados,
    resultado: ResultadoPublicadoAtleta,
) -> str:
    return f"{evento.id}:{resultado.atleta_id}"
```

Este método no accede a ningún atributo de instancia. Debe ser `@staticmethod`.
El DesignReviewer reportó `PoliticaP11Handler` con LCOM=2 — este método sin estado
es exactamente la causa.

---

## Especificación del comportamiento

### Precondición

- `_registrar_fallo_sin_email` existe con implementaciones distintas en P-10 y P-11
- `_evento_fuente_id` en P-11 es un método de instancia que no usa `self`

### Cambio propuesto

**Fix DES-01:** extraer función compartida a nivel de módulo en
`notificaciones/application/policies/` o en un helper de aplicación:

```python
# notificaciones/application/policies/_helpers.py (nuevo) o en solicitar_envio.py
async def registrar_fallo_sin_email(
    evento_fuente_id: str,
    repository: NotificacionRepository,
) -> None:
    if await repository.exists_success_by_evento_fuente_id(evento_fuente_id):
        return
    aggregate = Notificacion.registrar_fallo_de_solicitud(
        evento_fuente_id=EventoFuenteId(evento_fuente_id),
        motivo="destinatario_sin_email",
    )
    await persistir_eventos_pendientes(repository, aggregate)
```

P-10 y P-11 usan la función compartida, extrayendo el `evento_fuente_id` antes de llamarla.

**Fix DES-02:** agregar `@staticmethod` a `_evento_fuente_id` en P-11:

```python
@staticmethod
def _evento_fuente_id(
    evento: ResultadosPublicados,
    resultado: ResultadoPublicadoAtleta,
) -> str:
    return f"{evento.id}:{resultado.atleta_id}"
```

### Postcondición

- `_registrar_fallo_sin_email` no está duplicado — existe una única implementación compartida
- P-10 y P-11 llaman a la función compartida
- `PoliticaP11Handler._evento_fuente_id` es `@staticmethod`
- DesignReviewer no reporta LCOM=2 en `PoliticaP11Handler`
- Los tests existentes de P-10 y P-11 siguen pasando sin modificación

---

## Criterios de aceptación

```gherkin
Feature: Políticas de notificación sin duplicación de código

  Scenario: P-10 registra fallo cuando el atleta no tiene email
    Given un evento InscripcionConfirmada para un atleta sin email
    When se procesa el evento con PoliticaP10Handler
    Then se registra NotificacionFallida con motivo "destinatario_sin_email"
    And no se intenta enviar ningún email

  Scenario: P-11 registra fallo para atletas sin email en resultados publicados
    Given un evento ResultadosPublicados con un atleta sin email
    When se procesa el evento con PoliticaP11Handler
    Then se registra NotificacionFallida para ese atleta con motivo "destinatario_sin_email"
    And los demás atletas con email reciben su notificación normalmente

  Scenario: La idempotencia funciona en el fallo registrado
    Given un fallo ya registrado para un evento_fuente_id dado
    When se vuelve a procesar el mismo evento
    Then no se registra un segundo fallo
    And la función retorna sin error
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — refactor de consistencia dentro del mismo BC

**Capa(s) afectadas:**
- [x] Application (`notificaciones/application/policies/`)

---

## Notas de implementación

1. La función compartida puede ir en un módulo `_helpers.py` dentro de `policies/`
   o directamente en `solicitar_envio.py` (ya importado por ambas políticas).
2. Actualizar P-10 para que extraiga el `evento_fuente_id` como `str` antes de llamar
   a la función compartida: `await registrar_fallo_sin_email(evento.id, self._repository)`.
3. Los tests de integración de P-10 y P-11 son la red de seguridad — ejecutar antes y después.
4. Verificar con DesignReviewer que LCOM de `PoliticaP11Handler` baja de 2 a 1 post-fix.

---

*Spec creada: 2026-04-16 — DES-01 y DES-02 de revisión BC Notificaciones pre-BL-004*
