# ADR-017: Event Sourcing en BC Notificaciones para garantía exactly-once

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-04-16 |
| **Autores** | Victor Valotto |
| **Relacionado con** | ADR-001 (ES en Competencia), ADR-008 (event store SQLite), US-4.5.1 |

---

## Contexto

El BC Notificaciones es un BC **genérico**: no contiene lógica de negocio propia del
dominio de apnea. Normalmente, un BC genérico se implementa con CRUD estándar.

Sin embargo, el BC Notificaciones tiene un requisito de calidad fuerte: **exactly-once
delivery** — cada email debe enviarse exactamente una vez, aunque el handler se dispare
múltiples veces (reintentos ante fallos del servidor, reinicios del proceso, eventos
duplicados en el bus).

## Problema

Sin mecanismo de deduplicación, un reintento del handler que dispara la política P-10
enviaría el mismo email de confirmación de inscripción dos veces al atleta.

La garantía exactly-once no es negociable: un email duplicado de "descalificado" (P-11)
o de "inscripción confirmada" (P-10) es un error visible para el usuario final.

## Alternativa descartada — CRUD con tabla `notificaciones_enviadas`

Agregar una tabla relacional con una columna `evento_fuente_id` indexada como UNIQUE.
Antes de enviar, consultar si el `evento_fuente_id` ya tiene registro.

**Problemas de esta alternativa:**
- Lógica de idempotencia ad-hoc fuera del aggregate — el dominio no la encapsula
- Sin audit trail natural: no hay registro del estado de transición ni del motivo de fallo
- Si se agregan nuevos canales (Push, SMS), la lógica de deduplicación debe duplicarse
- La tabla de "enviadas" y la tabla de "notificaciones" se desacoplan — consistencia más frágil

## Decisión

Se adopta **Event Sourcing en BC Notificaciones**.

## Justificación

El event store resuelve el problema de idempotencia de forma estructural:

1. Antes de crear una nueva `Notificacion`, `SolicitarEnvioHandler` consulta si existe
   un evento `NotificacionEnviada` para ese `evento_fuente_id` en el store.
2. Si existe → el aggregate `Notificacion.solicitar_envio()` devuelve `None`. No se crea
   ni se envía nada. El handler termina limpiamente.
3. Si no existe → se crea la `Notificacion`, se persiste `NotificacionSolicitada`, y se
   procede con el envío.

La infraestructura del event store SQLite (ADR-008) ya existe en el proyecto para el
BC Competencia. El BC Notificaciones la reutiliza sin overhead adicional.

El aggregate `Notificacion` encapsula la lógica de estados y la invariante de idempotencia —
el dominio es la fuente de verdad, no la infraestructura.

## Trade-off explícito

**ES en un BC genérico es una decisión inusual y debe justificarse.**

En este caso, la justificación es exclusivamente el requisito de idempotencia. No es
una decisión de "usar ES siempre" ni de "ES es mejor que CRUD". Si el requisito de
exactly-once no existiera, este BC sería CRUD.

La regla general del proyecto sigue siendo: ES solo donde la lógica de dominio lo justifica
(Competencia) o donde hay un requisito de infraestructura que ES resuelve naturalmente
(Notificaciones). Para Torneo, Registro, Resultados e Identidad, CRUD es la decisión correcta.

## Consecuencias

**Positivas:**
- Idempotencia garantizada por el aggregate, sin lógica ad-hoc en infraestructura
- Audit trail natural: cada transición de estado (`Solicitada → Enviada | Fallida`) queda
  registrada en el event store con timestamp
- El modelo escala a nuevos canales (Push, SMS en SP5) sin cambiar la lógica de idempotencia:
  el aggregate y el store soportan cualquier `CanalEnvio`
- Infraestructura compartida con Competencia — sin overhead de setup adicional

**Negativas:**
- Mayor complejidad que CRUD para un BC que no necesitaría ES por su lógica de dominio
- El equipo debe entender el patrón ES para mantener el BC — documentación obligatoria
  (resuelta por esta US y por el documento `docs/design/notificaciones.md`)
