# US-4.6.8: Documentación de arquitectura — Auditoría y exportación

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Tipo**: Documentación de arquitectura y diseño
**Artefactos producidos**: `docs/design/auditoria.md` · `docs/adr/ADR-018-hash-sha256-auditoria.md`

---

## Descripción

Como **equipo de desarrollo y futuros colaboradores**,
quiero **documentación completa del diseño de auditoría e integridad de resultados implementado en INC-4.6**
para **entender por qué el event store es la fuente del audit log, cómo funciona el hash SHA-256 como mecanismo de integridad, y qué restricciones existen sobre la mutabilidad de los datos de resultados**.

---

## Contexto

INC-4.6 implementa auditoría y exportación. La auditoría es consecuencia directa del Event Sourcing: el event store ya contiene el historial completo. El hash SHA-256 agrega una capa de verificación de integridad post-cierre. Esta US documenta esas decisiones formalmente.

**ADRs existentes relacionados:**
- **ADR-001** (Event Sourcing en Competencia): establece la inmutabilidad del event store como propiedad fundamental. El audit log es una consecuencia natural — no una decisión nueva.
- No hay ADR sobre integridad de datos / hashing.

**Decisiones a formalizar:**
1. El event store como fuente del audit log (extensión de ADR-001, no una nueva decisión)
2. SHA-256 sobre la secuencia canónica de eventos como mecanismo de integridad (nueva decisión — ADR-018)

---

## Especificación — qué debe contener la documentación

### ADR-018 — Hash SHA-256 para integridad de resultados

**Contexto a documentar:**
- Los torneos de apnea son oficiales ante FAAS. Los resultados son disputables.
- Una vez que una disciplina cierra, sus resultados no deben poder alterarse sin evidencia.
- El event store es inmutable en diseño, pero no lo es en el nivel de la base de datos (SQLite).

**Contenido mínimo del ADR:**

| Sección | Contenido |
|---------|-----------|
| Contexto | Resultados disputables ante federación; necesidad de verificación de integridad post-cierre |
| Problema | La inmutabilidad del event store es una propiedad arquitectónica, no una restricción física de la DB. Un administrador con acceso a la DB podría modificar eventos. El hash cierra ese gap a nivel de protocolo. |
| Decisión | SHA-256 sobre la secuencia canónica de eventos al cierre de cada disciplina |
| Justificación | SHA-256 está en la stdlib de Python (sin dependencias); produce un digest de 64 chars; es el estándar de facto para integridad de datos; verificable por cualquier herramienta externa |
| Secuencia canónica | Eventos ordenados por `sequence_number` ASC; cada evento serializado a JSON con campos ordenados alfabéticamente; concatenados con `\n` |
| Dónde se persiste | Como campo `hash_sha256` en el payload del evento `CompetenciaCerrada` — parte del event store, no en tabla separada |
| Consecuencias positivas | Verificación offline posible (cualquiera con acceso a los eventos puede recalcular el hash); no requiere infraestructura adicional |
| Consecuencias negativas | Si la DB es alterada también se puede alterar el evento `CompetenciaCerrada` que contiene el hash. Mitigación en SP5: firma digital o publicación del hash a un sistema externo |
| Evolución futura | En SP5 evaluar firma del hash con clave privada del organizador o publicación en registro externo (blockchain, registro federativo) |

---

### docs/design/auditoria.md — Documento nuevo

El documento debe cubrir los siguientes bloques:

**1. Por qué el event store es el audit log**

El BC Competencia usa Event Sourcing (ADR-001). El estado de cualquier aggregate se deriva de su secuencia de eventos. Como consecuencia estructural, el event store contiene el historial completo y cronológico de cada performance sin ningún trabajo adicional. No es una funcionalidad diseñada separadamente — es una propiedad emergente del diseño.

Contrastar con la alternativa descartada: tabla `audit_log` separada, poblada por triggers o listeners, que replica información ya presente en el event store (duplicación, posibilidad de divergencia).

**2. Qué contiene el audit log de una performance**

Tabla de tipos de eventos y su significado en términos de auditoría:

| Evento | Qué registra | Cuándo ocurre |
|--------|-------------|---------------|
| `PerformanceRegistrada` | AP anunciada, momento de registro | Al crear la performance |
| `ResultadoRegistrado` | RP medido | Al registrar el resultado |
| `TarjetaAsignada` | Tarjeta (Blanca/Roja/Amarilla), penalizaciones | Al asignar tarjeta |
| `DNSRegistrado` | No-presentación del atleta | Al marcar DNS |
| `ResultadoCorregido` | RP corregido + motivo + RP anterior | Al corregir (no reemplaza el evento anterior) |
| `TarjetaResuelta` | Resolución de tarjeta amarilla → Blanca o Roja | Al resolver revisión |

**3. El mecanismo de hash SHA-256**

Diagrama del flujo de cálculo:

```
CerrarCompetencia(competencia_id, disciplina)
        │
        ▼
Recuperar eventos de la disciplina del event store
(ORDER BY sequence_number ASC)
        │
        ▼
CalculadorHashCompetencia.calcular(eventos)
  para cada evento:
    json_canonico = json.dumps(evento.to_dict(), sort_keys=True)
  concatenado = "\n".join(jsons)
  hash = sha256(concatenado.encode("utf-8")).hexdigest()
        │
        ▼
CompetenciaCerrada emitido con hash_sha256 en payload
```

Ejemplo de verificación manual (herramienta externa puede reproducir el cálculo).

**4. Cómo verificar la integridad externamente**

Pasos para que un auditor externo (ej: representante FAAS) verifique que los resultados no fueron alterados:

1. Exportar el event store de la disciplina (CSV o JSON con todos los eventos)
2. Calcular SHA-256 sobre la secuencia canónica usando el mismo algoritmo
3. Comparar con el hash almacenado en el evento `CompetenciaCerrada`

Este proceso es completamente independiente de la aplicación.

**5. Exportación de resultados**

- Endpoint: `GET /resultados/{torneo_id}/export?format=csv|json`
- El JSON incluye el `hash_sha256` de cada disciplina cerrada — vincula el resultado exportado con la integridad del event store
- El CSV usa `;` como separador (convención Excel España/Latinoamérica y FAAS)
- Las disciplinas en ejecución se exportan con resultados parciales sin hash

**6. Límites y restricciones**

- El hash protege contra alteración posterior al cierre, pero no contra alteración antes del cierre (el organizador puede corregir performances hasta que cierra la disciplina — eso es by design)
- Un administrador con acceso directo a SQLite podría alterar tanto los eventos como el hash. Mitigación en SP5: firma digital.
- La auditoría es de solo lectura desde la API. No existe endpoint para modificar o eliminar eventos.

**7. Evolución futura**

- SP5: publicación del hash a un registro externo (API federativa FAAS, o un timestamp en blockchain público)
- SP5: firma del hash con clave privada del organizador para no-repudio
- SP5: UI de verificación pública donde cualquiera (atleta, juez) pueda verificar el hash de una disciplina sin necesidad de acceso a la app

---

## Criterios de aceptación

```gherkin
Feature: US-4.6.8 — Documentación auditoría y exportación

  Scenario: ADR-018 creado y completo
    Given el ADR-018 creado en docs/adr/
    Then documenta la decisión SHA-256 con contexto, justificación y consecuencias
    And describe la secuencia canónica de serialización de eventos
    And documenta explícitamente el límite: el hash no protege contra alteración en la DB
    And describe la evolución futura hacia firma digital o registro externo

  Scenario: docs/design/auditoria.md existe y es completo
    Given el documento creado
    Then contiene los 7 bloques especificados
    And incluye la tabla de eventos con su significado en auditoría
    And incluye el diagrama del flujo de cálculo del hash
    And incluye los pasos de verificación manual por un auditor externo
    And describe el formato de exportación CSV y JSON

  Scenario: consistencia con ADR-001
    Then auditoria.md referencia ADR-001 como fundamento del audit log
    And no contradice ninguna afirmación de ADR-001
    And deja claro que el audit log es consecuencia del ES, no una decisión adicional
```

---

## Impacto arquitectónico

No aplica — esta US produce solo documentación. No modifica código.

**Artefactos a producir:**
1. `docs/adr/ADR-018-hash-sha256-auditoria.md`
2. `docs/design/auditoria.md`

---

## Referencias

- US-4.6.1 (API audit log), US-4.6.2 (hash SHA-256), US-4.6.3 (UI), US-4.6.4 (exportación)
- ADR-001: Event Sourcing — fundamento del audit log
- ADR-008: event store SQLite — estructura física
- `competencia/domain/aggregates/` — aggregate Performance y sus eventos
- RF-CO-09: trazabilidad de resultados para la federación

---

*Redactado: 2026-04-15 — INC-4.6 documentación transversal*
