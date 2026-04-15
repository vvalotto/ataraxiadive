# US-4.6.4: Exportación de resultados — CSV y JSON

**Estado**: `To Do`
**Sprint**: SP4 — La Plataforma
**Incremento**: INC-4.6
**Bounded Context**: `resultados/api/`
**Capas afectadas**: `resultados/api/`, `resultados/application/queries/`

---

## Descripción

Como **organizador**,
quiero **descargar los resultados completos de un torneo en formato CSV o JSON**
para **compartirlos con la federación (FAAS), publicarlos en redes sociales o importarlos en herramientas externas**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento DDD | Nombre | Responsabilidad |
|---|---|---|
| Agregado | `RankingCompetencia` | Fuente del ranking por disciplina |
| Agregado | `RankingOverall` | Fuente del ranking global del torneo |
| Query | `ExportarResultados` | Consolida rankings de todas las disciplinas del torneo |

### Lenguaje ubicuo relevante

- **Exportación:** descarga de los resultados finales de un torneo en formato estructurado. Incluye todos los atletas de todas las disciplinas.
- **Ranking por disciplina:** posición, atleta, AP, RP, tarjeta, puntos — ordenado por RP descendente con reglas de empate.
- **Overall:** ranking global que agrega puntos de todas las disciplinas de un mismo atleta.

---

## Especificación del comportamiento

### Invariantes

- **INV-4.6.4-01:** La exportación incluye **todas las disciplinas** del torneo, no solo las cerradas. Las disciplinas en ejecución se exportan con los resultados parciales disponibles.
- **INV-4.6.4-02:** El endpoint acepta exactamente dos formatos: `csv` y `json`. Cualquier otro valor devuelve 400.
- **INV-4.6.4-03:** Solo el organizador puede exportar resultados.
- **INV-4.6.4-04:** La respuesta HTTP incluye el header `Content-Disposition: attachment; filename="resultados-{torneo_id}.{format}"` para forzar la descarga desde el browser.
- **INV-4.6.4-05:** El CSV usa punto y coma (`;`) como separador (convención FAAS / Excel en locales europeos).

### Operación principal

**Nombre**: `GET /resultados/{torneo_id}/export?format=csv|json`

| | Descripción |
|---|---|
| **Precondición** | El torneo existe; el solicitante es organizador |
| **Postcondición** | Se devuelve el archivo de resultados como descarga |
| **Excepciones** | 404 si el torneo no existe · 400 si el format no es csv ni json · 403 si no es organizador |

**Estructura del CSV:**

```
disciplina;posicion;atleta_nombre;categoria;club;ap;rp;tarjeta;penalizaciones;puntos
DNF;1;Martín García;Hombre Open;Club Náutico;60.0;58.0;Blanca;0;100
DNF;2;Ana Flores;Mujer Open;Club Náutico;70.0;62.0;BlancaConPenalizaciones;2;95
DNF;3;Roberto Chen;Hombre Open;FAAS;80.0;0.0;Roja;0;0
DNF;4;Diego Vega;Hombre Open;Club BA;40.0;0.0;DNS;0;0
STA;1;...
Overall;1;...
```

**Estructura del JSON:**

```json
{
  "torneo_id": "trn-001",
  "torneo_nombre": "Open Buenos Aires 2026",
  "exportado_en": "2026-05-15T18:00:00Z",
  "disciplinas": [
    {
      "disciplina": "DNF",
      "estado": "Cerrada",
      "hash_sha256": "a3f7c2...",
      "ranking": [
        {
          "posicion": 1,
          "atleta_id": "ath-123",
          "atleta_nombre": "Martín García",
          "categoria": "Hombre Open",
          "club": "Club Náutico",
          "ap": 60.0,
          "rp": 58.0,
          "tarjeta": "Blanca",
          "penalizaciones": 0,
          "puntos": 100
        }
      ]
    }
  ],
  "overall": [
    { "posicion": 1, "atleta_nombre": "...", "puntos_totales": 195 }
  ]
}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-4.6.4 — Exportación de resultados CSV y JSON

  Background:
    Given existe el torneo "trn-001" con disciplinas DNF y STA
    And el organizador está autenticado

  Scenario: exportar en formato JSON
    When hace GET /resultados/trn-001/export?format=json
    Then la respuesta es 200 OK
    And el Content-Type es "application/json"
    And el header Content-Disposition contiene "resultados-trn-001.json"
    And el cuerpo contiene las secciones "disciplinas" y "overall"
    And el ranking de DNF lista todos los atletas en orden de posición

  Scenario: exportar en formato CSV
    When hace GET /resultados/trn-001/export?format=csv
    Then la respuesta es 200 OK
    And el Content-Type es "text/csv; charset=utf-8"
    And el header Content-Disposition contiene "resultados-trn-001.csv"
    And la primera línea es el encabezado con columnas separadas por punto y coma
    And los datos de atletas están ordenados: primero por disciplina, luego por posición

  Scenario: format inválido devuelve 400
    When hace GET /resultados/trn-001/export?format=xlsx
    Then la respuesta es 400 Bad Request
    And el mensaje de error indica los formatos aceptados: "csv" y "json"

  Scenario: torneo inexistente devuelve 404
    When hace GET /resultados/torneo-inexistente/export?format=json
    Then la respuesta es 404 Not Found

  Scenario: juez no puede exportar
    Given el usuario autenticado tiene rol juez
    When hace GET /resultados/trn-001/export?format=json
    Then la respuesta es 403 Forbidden

  Scenario: disciplina en ejecución se exporta con resultados parciales
    Given la disciplina STA está en estado EnEjecucion con 2 de 3 atletas completados
    When el organizador exporta
    Then la disciplina STA aparece en la exportación con estado "EnEjecucion"
    And muestra los 2 atletas que ya tienen resultado registrado
    And el campo "hash_sha256" de STA está ausente (la disciplina no está cerrada)

  Scenario: el JSON de disciplina cerrada incluye el hash SHA-256
    Given la disciplina DNF está cerrada con hash "a3f7c2..."
    When el organizador exporta en JSON
    Then la sección de DNF incluye "hash_sha256": "a3f7c2..."
```

---

## Impacto arquitectónico

- [ ] No — se implementa con la arquitectura existente

**Capa(s) afectadas:**
- [x] Application — nueva query `ExportarResultados` en `resultados/application/queries/`
- [x] API — nuevo endpoint en `resultados/api/router.py`
- [x] Infrastructure — la query lee de las tablas de ranking ya existentes + event store para el hash

---

## Referencias

- Plan SP4 §INC-4.6 — US-4.6.4
- BC Resultados — `RankingCompetencia` y `RankingOverall`
- US-4.6.2: el hash SHA-256 se incluye en el JSON de exportación cuando la disciplina está cerrada
- RF-RP-05: exportación de resultados para la federación

---

*Redactado: 2026-04-15 — INC-4.6 Auditoría y Exportación*
