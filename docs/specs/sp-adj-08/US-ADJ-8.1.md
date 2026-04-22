# US-ADJ-8.1: Clarificar estados y lenguaje operativo del panel organizador — UAT-5.2 UX

**Estado**: `Pendiente`
**Iteracion / Sprint**: SP-ADJ-08
**Tipo**: fix UX funcional frontend
**Agregado principal afectado**: `DetalleTorneoPage` / paneles de organizador
**Bounded Context**: frontend organizador

---

## Descripcion (lenguaje de negocio)

Como **organizador**,
quiero distinguir claramente estados de carga, estados vacios, errores y acciones pendientes
para operar el torneo sin interpretar mensajes tecnicos internos.

---

## Contexto del dominio

### Problema

La UAT de cierre de INC-5.2 detecto mensajes ambiguos o tecnicos en el panel organizador:

- `UAT-5.2-01`: inscriptos vacios se comunica como error.
- `UAT-5.2-03`: jueces no diferencia loading, vacio y error.
- `UAT-5.2-04`: la disciplina seleccionada en ejecucion no se destaca lo suficiente.
- `UAT-5.2-06`: ejecucion muestra estados tecnicos como mensajes principales.
- `UAT-5.2-07`: lenguaje de acciones de fase requiere precision.

Estos hallazgos no agregan reglas de dominio nuevas; corrigen comunicacion, jerarquia visual
y lenguaje operativo.

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | `DetalleTorneoPage` | Contenedor principal del flujo organizador |
| Componente | `InscriptosPanel` o equivalente | Lista/estado de inscriptos del torneo |
| Componente | `JuecesPanel` | Gestion de jueces por disciplina |
| Componente | `EjecucionPanel` | Maestro-detalle de ejecucion por disciplina |
| Componente | `AccionesPanel` | Acciones de fase del torneo |

---

## Especificacion del comportamiento

### Precondicion

Existe un torneo visible para el organizador y las consultas frontend pueden estar en
estado `loading`, `success` con lista vacia, `success` con datos o `error`.

### Postcondicion

Cada panel comunica un estado unico y accionable:

- loading: mensaje de carga.
- vacio valido: mensaje de estado vacio de negocio.
- error tecnico: mensaje de error.
- bloqueo operativo: accion concreta y lugar donde resolverla.

### Invariantes

| ID | Invariante |
|----|------------|
| INV-ADJ-8.1-01 | Una respuesta HTTP exitosa con lista vacia no debe renderizar mensaje de error. |
| INV-ADJ-8.1-02 | Loading, vacio y error deben ser estados visual y textualmente distintos. |
| INV-ADJ-8.1-03 | Los bloqueos de ejecucion deben indicar la accion concreta y el tab donde resolverla. |
| INV-ADJ-8.1-04 | La disciplina seleccionada en ejecucion debe quedar asociada visualmente con su detalle. |
| INV-ADJ-8.1-05 | En `EJECUCION`, la accion de fase debe nombrarse `Pasar a premiacion`. |
| INV-ADJ-8.1-06 | En `PREMIACION`, la accion de cierre debe nombrarse `Cerrar torneo`. |

---

## Criterios de aceptacion

```gherkin
Feature: Claridad operativa del panel organizador

  Scenario: Inscriptos vacios no se muestran como error
    Given la API de inscriptos responde 200 con lista vacia
    When el organizador abre el panel de inscriptos
    Then ve "Todavia no hay inscriptos para este torneo"
    And no ve "No se pudieron cargar los inscriptos del torneo"

  Scenario: Error real de inscriptos se muestra como error
    Given la API de inscriptos falla
    When el organizador abre el panel de inscriptos
    Then ve "No se pudieron cargar los inscriptos del torneo"

  Scenario: Jueces diferencia loading, vacio y error
    Given el panel de jueces esta cargando
    Then muestra "Cargando jueces..."
    When la consulta termina exitosamente sin jueces asignados
    Then muestra "Todavia no hay jueces asignados"
    When la consulta falla
    Then muestra "No se pudieron cargar los jueces"

  Scenario: Disciplina seleccionada queda asociada al detalle
    Given el torneo tiene disciplinas DNF y STA
    When el organizador selecciona DNF en el tab Ejecucion
    Then el item DNF se destaca visualmente
    And el panel detalle usa un tratamiento visual consistente con DNF seleccionado

  Scenario: Bloqueo operativo indica accion concreta
    Given DNF no tiene grilla confirmada
    When el organizador abre el detalle de ejecucion de DNF
    Then ve "Falta confirmar la grilla de DNF en el tab Grilla"
    And no ve solo un estado tecnico interno como mensaje principal

  Scenario: Lenguaje de fase es preciso
    Given el torneo esta en EJECUCION
    Then la accion visible se llama "Pasar a premiacion"
    Given el torneo esta en PREMIACION
    Then la accion visible se llama "Cerrar torneo"
```

---

## Impacto arquitectonico

**Esta US requiere una decision arquitectonica?**
- [x] No — se implementa con componentes frontend existentes.

**Capa(s) afectadas:**
- [x] Frontend — paneles de organizador.
- [ ] Backend.
- [ ] Dominio.

---

## Artefactos a modificar

| Artefacto | Cambio |
|-----------|--------|
| `frontend/src/pages/organizador/DetalleTorneoPage.tsx` | Ajustar textos/estados si concentra paneles o acciones. |
| `frontend/src/components/organizador/JuecesPanel.tsx` | Separar loading/vacio/error. |
| `frontend/src/components/organizador/EjecucionPanel.tsx` | Destacar seleccion y reemplazar estados tecnicos por mensajes accionables. |
| Panel de inscriptos correspondiente | Separar lista vacia exitosa de error tecnico. |
| `frontend/src/components/organizador/AccionesPanel.tsx` | Usar textos `Pasar a premiacion` y `Cerrar torneo`. |

---

## Notas de implementacion

1. No esconder datos utiles; el cambio es de jerarquia y lenguaje, no de perdida de informacion.
2. Evitar duplicar strings dispersos si ya existe un componente/helper de estado vacio.
3. Verificar en viewport mobile y desktop que el destaque de disciplina seleccionada no degrade legibilidad.

---

*Spec creada: 2026-04-22 — hallazgos UAT-5.2-01, 03, 04, 06 y 07*
