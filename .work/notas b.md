---                                                                                                                                 
  Análisis: PLAN-SP-ADJ-03 vs hallazgos de software                                                                                   
                                                                                                                                      
  El PLAN-SP-ADJ-03 está significativamente desactualizado respecto del 07-issues-consolidados.md. Aquí el detalle:                   
                                                                                                                                      
  ---                                                                                                                               
  Lo que YA ESTÁ en el PLAN (y está correcto)                                                                                         
                                                                                                                                      
  ┌────────────┬──────────────────────────────┬───────────────────┐
  │     ID     │              US              │      Fuente       │                                                                   
  ├────────────┼──────────────────────────────┼───────────────────┤                                                                 
  │ US-ADJ-3.1 │ Extraer GrillaDeSalida VO    │ ADJ-01 + SOLID-01 │                                                                   
  ├────────────┼──────────────────────────────┼───────────────────┤                                                                 
  │ US-ADJ-3.2 │ Extraer TarjetaAsignacion VO │ ADJ-02            │                                                                   
  └────────────┴──────────────────────────────┴───────────────────┘
                                                                                                                                      
  ---                                                                                                                               
  Lo que está en 07-issues-consolidados pero NO en el PLAN
                                                                                                                                      
  ┌────────────┬─────────────────────┬───────────────────────────────────────────────────────────────────────┬───────────────────┐ 
  │     US     │       Issues        │                              Descripción                              │     Prioridad     │    
  ├────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────┼───────────────────┤  
  │ US-ADJ-3.3 │ ADJ-03 + ADJ-04 +   │ Refactorizar app.py (build_app 51 líneas) + constante event type en   │ Media             │    
  │            │ SOLID-04            │ calcular_overall.py                                                   │                   │  
  ├────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ US-ADJ-3.4 │ ADJ-05              │ Mover OrganizadorDep/AtletaDep/JuezDep a shared/api/dependencies.py   │ Alta (3 BCs       │ 
  │            │                     │                                                                       │ acoplados)        │    
  ├────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────┼───────────────────┤  
  │ US-ADJ-3.5 │ ADJ-06              │ Limpiar imports competencia.domain.value_objects.* → shared.domain.*  │ Baja              │    
  │            │                     │ en ports                                                              │                   │    
  ├────────────┼─────────────────────┼───────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ US-ADJ-3.6 │ SOLID-02 + SOLID-03 │ TokenServicePort + PasswordHashingPort en Identidad                   │ Alta (DIP         │    
  │            │                     │                                                                       │ violation)        │    
  └────────────┴─────────────────────┴───────────────────────────────────────────────────────────────────────┴───────────────────┘
                                                                                                                                      
  El PLAN menciona D-05 y D-06 como "acciones" sueltas, pero US-ADJ-3.3 y US-ADJ-3.4 los absorben con mejor granularidad.             
   
  ---                                                                                                                                 
  Lo que está en los HITOs pero NO en el PLAN ni en 07-issues-consolidados                                                          
                                                                                                                                      
  HITO-15 — acción pendiente explícita (marcada con [ ]):
                                                                                                                                      
  ┌──────────────────────────────────────────────────────────────────────────┬──────────────────────────────────┬─────────────────┐ 
  │                                 Hallazgo                                 │            Ubicación             │     Estado      │   
  ├──────────────────────────────────────────────────────────────────────────┼──────────────────────────────────┼─────────────────┤ 
  │ Proyección competencias_por_torneo: ObtenerCompetenciasPorTorneoHandler  │                                  │ No está en      │
  │ hace load_all_streams_with_prefix + filter en memoria (O(n)). HITO-15 lo │ competencia/application/queries/ │ ningún          │
  │  marca explícitamente para SP-ADJ-03 o SP4.                              │                                  │ documento del   │   
  │                                                                          │                                  │ plan            │
  └──────────────────────────────────────────────────────────────────────────┴──────────────────────────────────┴─────────────────┘   
                                                                                                                                    
  HITO-14 — D-06 sin US asignada:

  ┌──────────────────────────────────────────────────────────────────────────────────┬────────────────────────────┬───────────────┐
  │                                     Hallazgo                                     │         Ubicación          │    Estado     │
  ├──────────────────────────────────────────────────────────────────────────────────┼────────────────────────────┼───────────────┤   
  │ resultados/infrastructure/repositories/resultados_competencia_adapter.py —       │                            │ Referenciado  │
  │ imports directos cross-BC. El PLAN lo menciona como "audit D-06 ← independiente" │ resultados/infrastructure/ │ pero sin US   │   
  │  pero nunca se mapeó a una US concreta ni se clasificó como "aceptable /         │                            │ ni decisión   │   
  │ temporal / corregir".                                                            │                            │ tomada        │
  └──────────────────────────────────────────────────────────────────────────────────┴────────────────────────────┴───────────────┘   
                                                                                                                                    
  ---
  Lo que NO aplica a software (de HITOs 14 y 16)
                                                                                                                                      
  - HITO-14 D-01/D-02/D-03/D-07/D-08/D-09/D-10: documentales, tooling, metodología — fuera del scope
  - HITO-16: sobre secuencialidad del pipeline — proceso, no código                                                                   
                                                                                                                                      
  ---                                                                                                                                 
  Resumen de brechas                                                                                                                  
                                                                                                                                    
  ┌────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────┐
  │                       Brecha                       │                          Acción sugerida                           │
  ├────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤         
  │ US-ADJ-3.3 a 3.6 no están en el PLAN               │ Agregar las 4 US al PLAN                                           │
  ├────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤         
  │ Proyección competencias_por_torneo (HITO-15 [ ])   │ Decidir: ¿nueva US en SP-ADJ-03 o diferir a SP4?                   │         
  ├────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤         
  │ D-06 cross-BC en resultados_competencia_adapter.py │ Decidir: ¿auditar y formalizar como US-ADJ-3.7 o dejarlo para SP4? │         
  └────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────┘  
  

HITO-15 — Proyección no materializada en Competencia
                                                                                                                                      
  El problema: cuando el juez pide "dame todas las competencias de este torneo", el handler hace esto:                              
                                                                                                                                      
  # Carga TODOS los event streams del BC competencia
  streams = await self._event_store.load_all_streams_with_prefix("competencia-")                                                      
  # Filtra en memoria los que tienen el torneo_id buscado                                                                             
                                                                                                                                      
  Es decir: si hay 100 competencias en el sistema, carga los 100 streams aunque el torneo tenga solo 3. Funciona bien ahora con datos 
  de prueba. En producción con torneos reales, cada request de grilla va a escalar O(n) con el total histórico de competencias del    
  sistema.                                                                                                                            
              
  La solución es una tabla de proyección competencias_por_torneo que se actualiza cada vez que se crea una competencia. Lectura pasa  
  de O(n) a O(1).
                                                                                                                                      
  ---         
  HITO-14 — D-05 y D-06 (los dos son de código)
                                                                                                                                      
  D-05 — routers de BCs CRUD importan dominio/infraestructura directamente
                                                                                                                                      
  La regla de arquitectura dice que api/ solo puede importar application/. Pero en la realidad:                                       
                                                                                                                                      
  - identidad/api/router.py — usa JWTService (infraestructura) directamente                                                           
  - registro/api/router.py — idem
  - torneo/api/router.py — idem                                                                                                       
              
  El app.py debería ser el composition root: crear los servicios concretos y pasarlos vía inyección. Los routers no deberían saber que
   JWTService existe. Hoy violan eso.
                                                                                                                                      
  D-06 — resultados importa tipos concretos de competencia directamente                                                               
   
  La regla dice que la comunicación entre BCs va solo por puertos/ACLs. Pero                                                          
  resultados/infrastructure/repositories/resultados_competencia_adapter.py importa tipos del BC competencia directamente (no a través
  de un puerto).                                                                                                                      
              
  La pregunta que quedó abierta es: ¿ese import es aceptable como ACL (el adapter es la capa anticorrupción), o es una violación      
  porque consume el aggregate concreto del upstream en lugar de un DTO/contrato delgado?
                                                                                          