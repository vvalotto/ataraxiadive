# ADR-018: Hash SHA-256 para integridad de resultados de competencia

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-04-16 |
| **Autores** | Victor Valotto |
| **Relacionado con** | ADR-001 (Event Sourcing), ADR-008 (event store SQLite), US-4.6.2 |

---

## Contexto

Los torneos de apnea pueden ser oficiales ante la FAAS (Federación Argentina de
Actividades Subacuáticas). Los resultados son disputables por atletas, entrenadores
o la propia federación. Una vez que una disciplina cierra, sus resultados no deben
poder alterarse sin evidencia detectable.

El BC Competencia usa Event Sourcing (ADR-001). El event store es inmutable **por
convención arquitectónica**: no existe endpoint ni comando que permita eliminar o
modificar eventos. Sin embargo, la inmutabilidad no es una restricción física: un
administrador con acceso directo a la base de datos SQLite podría modificar registros
sin que la aplicación lo detecte.

## Problema

La inmutabilidad del event store es una propiedad de la arquitectura, no de la
infraestructura. Si los resultados son impugnados después de un torneo, no existe
actualmente ningún mecanismo externo a la aplicación que permita verificar que el
event store no fue alterado.

## Decisión

Al cerrar una disciplina (`CerrarCompetencia`), calcular el **hash SHA-256** de la
secuencia canónica de eventos de esa disciplina y persistirlo como campo `hash_sha256`
en el payload del evento `CompetenciaCerrada`.

## Algoritmo — Secuencia canónica

El hash se calcula sobre la representación canónica de los eventos, implementada
en `CalculadorHashCompetencia` (`competencia/domain/services/`):

1. Recuperar todos los eventos del stream de la disciplina, ordenados por `sequence_number` ASC
2. Para cada evento, construir un diccionario canónico con exactamente cuatro campos:
   ```python
   {
     "datos": evento["payload"],       # payload JSON del evento
     "sequence_number": evento["sequence"],
     "timestamp": evento["occurred_at"],
     "tipo": evento["event_type"],
   }
   ```
3. Serializar cada diccionario a JSON con `sort_keys=True` (orden determinístico)
4. Concatenar los JSONs separados por `\n`
5. Calcular `sha256(concatenado.encode("utf-8")).hexdigest()`

Esta especificación es suficiente para que cualquier herramienta externa reproduzca
el cálculo y verifique la integridad sin depender de la aplicación.

## Justificación

- **SHA-256** está en la stdlib de Python (`hashlib`) — sin dependencias adicionales
- Produce un digest de 64 caracteres hexadecimales — almacenable como string en el evento
- Es el estándar de facto para integridad de datos, reconocido y verificable con
  cualquier herramienta (`sha256sum`, Python, OpenSSL, etc.)
- Persistir el hash dentro del evento `CompetenciaCerrada` lo une al event store mismo:
  cualquier auditoría que lea el event store encuentra el hash en el mismo lugar que los eventos

## Consecuencias

**Positivas:**
- Verificación offline: cualquier auditor con acceso a los eventos puede recalcular
  el hash con las especificaciones de esta ADR sin necesidad de ejecutar la aplicación
- No requiere infraestructura adicional — el hash vive en el event store existente
- El hash es calculado y emitido por el dominio (servicio de dominio
  `CalculadorHashCompetencia`) — la lógica de integridad no está en la infraestructura
- Trazabilidad automática: el evento `CompetenciaCerrada` registra exactamente cuándo
  y con qué hash se cerró cada disciplina

**Negativas:**
- El hash no protege contra un atacante con acceso a SQLite que modifique tanto los
  eventos como el evento `CompetenciaCerrada` que contiene el hash. El hash prueba
  consistencia interna, no integridad frente a un adversario con acceso físico a la DB.
- Si se necesita repudiar resultados frente a un adversario con acceso a la DB,
  se requiere un mecanismo externo (ver sección Evolución).

## Límites del diseño

- El hash protege contra alteración **posterior al cierre**. Antes del cierre, el
  organizador puede corregir performances — eso es comportamiento esperado del dominio.
- El hash no protege contra alteraciones coordinadas en la base de datos (eventos + hash).
- La API no expone ningún endpoint para modificar o eliminar eventos — la protección
  primaria sigue siendo la inmutabilidad arquitectónica.

## Evolución futura (SP5)

- **Firma digital:** firmar el hash con la clave privada del organizador. Permite
  verificar integridad incluso si alguien tiene acceso a la base de datos, ya que
  no puede falsificar la firma sin la clave privada.
- **Publicación en registro externo:** enviar el hash a una API de la federación (FAAS)
  o a un timestamp en un registro público. El hash publicado externamente no puede
  ser alterado retroactivamente aunque se modifique la DB local.
- **UI de verificación pública:** página que permite a cualquier atleta o juez
  verificar el hash de una disciplina sin necesidad de acceso de administrador.
