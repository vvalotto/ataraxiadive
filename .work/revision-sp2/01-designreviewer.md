# Revisión de Calidad — Cierre SP2
## DesignReviewer — Hallazgos y Análisis Experimental

**Fecha:** 2026-03-28
**Comando:** `designreviewer src/`
**Resultado:** 11 CRITICAL · 78 WARNING · 0 INFO

---

## CRITICAL — Mapa completo

| Clase | Analyzer | Valor/Umbral | Capa |
|---|---|---|---|
| `Competencia` | CBO | 23/5 | aggregates |
| `Competencia` | GodObject | 21/20 | aggregates |
| `Competencia` | WMC | 60/20 | aggregates |
| `Performance` | CBO | 22/5 | aggregates |
| `Performance` | GodObject | 25/20 | aggregates |
| `Performance` | WMC | 46/20 | aggregates |
| `RankingCompetencia` | CBO | 8/5 | aggregates (nuevo en US-2.4.2) |
| `RegistrarAPHandler` | CBO | 10/5 | commands |
| `LlamarAtletaHandler` | CBO | 7/5 | commands |
| `ObtenerProximasPerformancesHandler` | CBO | 6/5 | queries |
| `AndarivelesActivosAdapter` | CBO | 7/5 | repositories |

Los primeros 10 son pre-existentes. El 11 (RankingCompetencia) fue introducido en US-2.4.2.

---

## WARNING — Patrones destacados

- **LongMethod en aggregates:** métodos de 86, 127, 56 líneas en `Competencia`; 48, 56 líneas en `Performance`
- **FeatureEnvy en todos los Handlers (commands y queries):** RegistrarAPHandler 22/5, CorregirResultadoHandler 10/2, ObtenerPerformanceActualHandler 6/2, etc.
- **DataClumps en router.py:** 4 parámetros que viajan juntos (candidato a Value Object o DTO)
- **LongMethod en SQLiteEventStore:** 5 métodos entre 22–30 líneas
- **LCOMAnalyzer en Competencia y RankingCompetencia:** cohesión baja (2/1)

---

## Análisis Experimental — Tres Patrones

### Patrón 1 — Complejidad esencial del Core Domain
`Competencia` (CBO 23, WMC 60) y `Performance` (CBO 22, WMC 46) concentran 6 de los 11 CRITICALs.
Son los aggregates del Core Domain con Event Sourcing, donde múltiples eventos, value objects y políticas convergen por diseño.

**Pregunta experimental:** ¿Es complejidad accidental (diseño mejorable) o complejidad esencial del dominio de apnea?

Señal adicional: los métodos largos (86, 127 líneas en `Competencia`) sí son candidatos reales a refactor — ahí hay complejidad accidental mezclada con la esencial.

❯ Ok, vamo a atacar el hallazgo del patrón 1. Claramente para mi necesitan ser refactorizadas tanto competencia como performance. Si    
son agregados singnifica que son concepto compuestos de otro conceptos, politicas, OV y eventos. Primera pregunta porque no hablamos de 
 entidades del dominio?                                                                                                                 
                                                                                                                                        
⏺ Buena pregunta, y toca el núcleo del problema.                                                                                        
                                                                                                                                      
  La respuesta corta: un Aggregate es una entidad (el Aggregate Root es siempre una entidad con identidad), pero el término "aggregate" 
  agrega algo que "entity" no dice: define una frontera de consistencia transaccional.
                                                                                                                                        
  La diferencia conceptual:                                                                                                             
   
  ┌───────────────────────────────────────────────────┬────────┬──────────────┐                                                         
  │                                                   │ Entity │  Aggregate   │
  ├───────────────────────────────────────────────────┼────────┼──────────────┤
  │ Tiene identidad             (   │ ✅  e   o        ││✅  (  │r✅ (el root) │
  ├───────────────────────────────────────────────────┼────────┼──────────────┤
  │ Tiene estado que cambia         │ ✅               ││✅     │ ✅           │                                                           
  ├───────────────────────────────────────────────────┼────────┼──────────────┤                                                         
  │ Define frontera de consistencia                   ││❌     │ ✅           │                                                           
  ├───────────────────────────────────────────────────┼────────┼──────────────┤                                                         
  │ Agrupa otras entidades/VOs bajo su control        ││❌     │ ✅           │
  ├───────────────────────────────────────────────────┼────────┼──────────────┤                                                         
  │ Nada externo referencia sus internos directamente │ ❌     │ ✅           │
  ├───────────────────────────────────────────────────┼────────┼──────────────┤                                                         
  │ En ES: genera y aplica eventos                    │ ❌     │ ✅           │
  └───────────────────────────────────────────────────┴────────┴──────────────┘                                                         
                                                      
  Competencia es una entidad y es un aggregate root. Se llama aggregate porque es el único punto de entrada para modificar todo lo que  
  vive dentro de su frontera. Nadie toca la grilla, los andariveles, ni las performances directamente — todo pasa por Competencia.
                                                                                                                                        
  ---                                                 
  Ahora el problema real: en Event Sourcing el aggregate root absorbe cuatro responsabilidades simultáneas:
                                                                                                                                        
  1. Estado — mantener los datos de la competencia
  2. Invariantes — enforcar las reglas de dominio antes de aceptar un comando                                                           
  3. Generación de eventos — producir los domain events cuando algo cambia                                                              
  4. Aplicación de eventos — los métodos _apply_* para reconstruir estado desde el event store                                          
                                                                                                                                        
  En CRUD, un aggregate root puede ser compacto. En ES, se infla inevitablemente porque acumula esas cuatro capas.                      
                                                                                                                                        
  Eso explica el WMC 60 de Competencia — no es que el diseño sea malo, es que la clase está haciendo todo lo que le corresponde hacer   
  dentro del patrón, sin separar las responsabilidades que sí se pueden separar.
                                                                                                                                        
  ---                                                 
  Lo que se puede refactorizar sin romper la frontera:
                                                                                                                                        
  - Extraer la lógica de _apply_* a un objeto separado (patrón EventApplier o StateRebuilder)
  - Mover las políticas (P-08, reglas de tarjeta) a objetos de política explícitos en lugar de métodos internos                         
  - Identificar si hay entidades internas (Grilla, Andarivel) que hoy viven como lógica en el root y podrían ser objetos propios       


### Patrón 2 — Falso positivo sistemático: FeatureEnvy en Handlers
*Todos* los command handlers y casi todos los query handlers tienen FeatureEnvy.
En CQRS, un handler *por diseño* delega al aggregate — eso es exactamente su responsabilidad.
El analyzer lo lee como "la clase trabaja más con datos de otra clase".

**Conclusión:** Falso positivo estructural del analyzer cuando se aplica a arquitectura CQRS/ES.
El patrón aparece en 100% de los handlers sin excepción — es evidencia del límite del análisis estático frente a patrones DDD.

### Patrón 3 — CBO en infraestructura y queries (señal real, moderada)
`AndarivelesActivosAdapter` (CBO 7/5), `ObtenerProximasPerformancesHandler` (6/5), `LlamarAtletaHandler` (7/5).
Más cercanos al umbral. Son candidatos a revisión genuina, pero no tan urgentes como los aggregates.

---

## Hallazgos para el Experimento (candidatos a HITO/BL-002)

### H-A — El umbral CBO=5 no está calibrado para Event Sourcing
Un aggregate ES que maneja 12 tipos de eventos y 10 value objects *necesita* CBO alto.
La herramienta no distingue entre acoplamiento accidental y acoplamiento estructural obligatorio del patrón ES/CQRS.
Las métricas estáticas son ciegas al contexto arquitectural.

**Implicancia para el experimento:** Los quality gates de software_limpio requieren ajuste manual de umbrales cuando se usa ES/CQRS. Sin ese ajuste, la señal es ruidosa y puede generar fatiga de falsos positivos.

### H-B — FeatureEnvy es un falso positivo predecible en CQRS
El patrón es 100% consistente: todos los handlers lo tienen.
No es una señal sobre el código — es una señal sobre la inadecuación del analyzer para este patrón arquitectural.

**Implicancia:** En proyectos IEDD con CQRS, FeatureEnvy debería ser suprimido o reconfigurado en capas `application/commands/` y `application/queries/`.

### H-C — Los métodos largos en aggregates sí son señal real
Un método de 127 líneas en `Competencia` es complejidad accidental, no esencial.
La señal de LongMethod es más confiable que CBO/FeatureEnvy en este contexto arquitectural.

---

## Pendiente de investigación
- [ ] Abrir `Competencia` y `Performance`: identificar qué métodos son los más largos y si hay OCP/SRP violados
- [ ] Verificar si `AndarivelesActivosAdapter` (CBO 7) tiene acoplamiento justificado o no
- [ ] Evaluar DataClumps en `router.py`: ¿hay un DTO que extraer?
