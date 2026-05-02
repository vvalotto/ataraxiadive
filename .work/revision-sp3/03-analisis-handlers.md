# Análisis de Handlers — Cierre SP3

**Fecha:** 2026-04-02
**Alcance:** commands/ y queries/ de todos los BCs

---

## Patrón general

FeatureEnvy es **estructuralmente esperado** en los handlers de la capa application:
los Command Handlers cargan aggregate desde repo, ejecutan comando, persisten eventos.
Por definición acceden a múltiples campos/métodos del aggregate → FeatureEnvy alto.

**Regla para este análisis:** FeatureEnvy en handlers es falso positivo del patrón DDD.
Solo se registra como issue cuando el handler tiene lógica de negocio propia (reglas, cálculos).

---

## Handlers con issues reales

### RegistrarAPHandler (commands/registrar_ap.py)
- LongMethod: 71/20 — genuinamente largo
- Contiene validaciones de AP (unidad, valor, límites) que podrían delegarse al VO
- **Candidato:** mover validaciones a `AP` value object

### AsignarTarjetaHandler (commands/asignar_tarjeta.py)
- LongMethod: 46/20
- Orquesta carga de Performance + TarjetaAsignada + validación de estado
- `TarjetaAsignacion` como VO (US-ADJ-3.2) reduciría este handler considerablemente
- **Candidato:** US-ADJ-3.2

### LlamarAtletaHandler (commands/llamar_atleta.py)
- LongMethod: 54/20 + FeatureEnvy 15/5
- Alta coordinación con el aggregate — refleja la complejidad del OT en apnea
- Aceptar por ahora

### CalcularOverallHandler (commands/calcular_overall.py — nuevo SP3)
- LongMethod: 25/20, módulo: 24/20
- Nuevo en US-3.5.2 — lógica de orquestación del overall
- Moderado, sin urgencia

---

## Handlers nuevos en SP3 (BCs Torneo, Registro, Identidad, Resultados)

| Handler | BC | Issues | Evaluación |
|---------|-----|--------|------------|
| CrearTorneoHandler | torneo | FeatureEnvy 9/1 | Falso positivo — CRUD handler |
| AsignarDisciplinasHandler | torneo | FeatureEnvy 3/2 | Falso positivo |
| AsignarJuezHandler | torneo | FeatureEnvy 4/2 | Falso positivo |
| RegistrarUsuarioHandler | identidad | FeatureEnvy 6/2, LongMethod 21/20 | Incluye hashing — moderado |
| AutenticarUsuarioHandler | identidad | FeatureEnvy 3/2 | Falso positivo |
| InscribirAtletaHandler | registro | FeatureEnvy 12/4, LongMethod 31/20 | Orquesta inscripción + validación cupo |
| RegistrarAtletaHandler | registro | FeatureEnvy 9/2 | Falso positivo |

**Evaluación general:** los handlers de los nuevos BCs CRUD son simples. Los issues son falsos positivos del patrón. Sin acciones requeridas.

---

## Queries con issues reales

### ObtenerRankingHandler (queries/obtener_ranking.py)
- LongMethod: 31/20 — construye respuesta de ranking con formato complejo
- Pre-existente SP2, sin cambios

### ObtenerProximasPerformancesHandler
- LongMethod: 29/20 — filtrado y ordenamiento de performances activas
- Pre-existente SP2, sin cambios

**Observación:** las queries largas son aceptables en la capa de lectura — construyen DTOs complejos. Sin urgencia.
