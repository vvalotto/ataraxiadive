# Plan de Implementacion: US-4.6.4 - Exportacion de resultados CSV y JSON

**Sprint:** SP4 - La Plataforma  
**Incremento:** INC-4.6  
**Bounded Context:** `resultados`  
**Patron:** `hexagonal-ddd-bc`  
**Estimacion total:** 4h 40min  
**Estado:** Pendiente de aprobacion

## Objetivo

Agregar una exportacion descargable de resultados por torneo en formatos `csv`
y `json`, consolidando rankings por disciplina, overall, estado de disciplina y
`hash_sha256` cuando la competencia ya fue finalizada.

## Hallazgos de contexto

- `resultados/api/router.py` hoy solo expone ranking por competencia y overall
- No existe query agregada de exportacion en `resultados/application/queries/`
- `US-4.6.3` ya expone `hash_sha256` via `GET /competencia/{id}/estado`
- `ObtenerCompetenciasPorTorneo` ya existe en BC Competencia y permite listar
  disciplinas del torneo
- BC Resultados no tiene hoy ACL para nombre y club de atleta; solo existe
  `AtletaCategoriaAdapter`
- El nombre del torneo tendra que resolverse desde `torneo.db`

## Componentes a ajustar

### 1. Application - query de exportacion consolidada

- [ ] Nueva query `resultados/application/queries/exportar_resultados.py` (60 min)
  - Consolidar disciplinas del torneo
  - Leer ranking por competencia, overall y estado/hash de cada disciplina
  - Resolver metadata de torneo
  - Producir DTO exportable independiente del formato

### 2. Infrastructure - ACLs faltantes

- [ ] ACL a Registro para datos de atleta (35 min)
  - Nombre completo
  - Club
  - Reutilizar categoria ya resuelta donde convenga

- [ ] ACL a Torneo para metadata basica (20 min)
  - Nombre del torneo
  - Validacion de existencia

- [ ] Reutilizacion/consulta a Competencia (30 min)
  - Listar competencias por torneo
  - Consultar estado y `hash_sha256` por competencia

### 3. API - endpoint de descarga

- [ ] `src/resultados/api/router.py` (40 min)
  - Nuevo endpoint `GET /resultados/{torneo_id}/export`
  - Validar `format=csv|json`
  - Restringir a organizador/admin
  - Responder con `Content-Disposition` correcto
  - Serializar JSON y CSV con `;` como separador

### 4. Serializacion de formatos

- [ ] JSON (20 min)
  - Estructura con `disciplinas` y `overall`
  - Incluir `hash_sha256` solo cuando corresponda

- [ ] CSV (25 min)
  - Filas por disciplina y overall
  - Encabezado estable y separador `;`
  - Orden por disciplina y posicion

### 5. Tests

- [ ] Tests unitarios de la query de exportacion (30 min)
  - consolidacion de disciplinas
  - inclusion condicional de hash
  - validacion de formatos

- [ ] Tests de API en `resultados/api` (35 min)
  - 200 JSON
  - 200 CSV
  - 400 format invalido
  - 403 por rol
  - 404 torneo inexistente

### 6. Validacion

- [ ] Ejecutar pytest focalizado de `resultados` + adapters tocados (10 min)
- [ ] Ejecutar `codeguard` focalizado (10 min)
- [ ] Evaluar waiver BDD si no hay step definitions reaprovechables (10 min)

## Dependencias y decisiones

- La exportacion debe tomar todas las disciplinas del torneo, aun si el ranking
  de alguna no fue calculado o esta parcial.
- Para disciplinas en ejecucion, el hash no se expone.
- La resolucion de atleta debe salir de Registro, no de snapshots duplicados en Resultados.
- El endpoint de exportacion pertenece a BC Resultados aunque consulte otros BCs
  por ACL, porque su responsabilidad es consolidar resultados publicables.

## Riesgos

- El overall puede no existir para todos los torneos; la exportacion debe tolerar
  lista vacia sin fallar.
- Si alguna disciplina no tiene ranking calculado, hay que decidir si exportar
  arreglo vacio o resultados parciales derivados; la spec sugiere exportar lo
  disponible sin bloquear.
- El CSV puede requerir aplanar estructuras que en JSON son naturales.

## Checklist de salida

- [ ] Endpoint `/resultados/{torneo_id}/export` funcional en `csv` y `json`
- [ ] `Content-Disposition` correcto
- [ ] Hash visible solo para disciplinas finalizadas
- [ ] Exportacion incluye todas las disciplinas del torneo
- [ ] Tests focalizados y quality gate en verde

*Plan generado: 2026-04-16 - US-4.6.4 INC-4.6 SP4*
