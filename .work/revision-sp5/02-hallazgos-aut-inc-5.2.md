# Hallazgos UAT — INC-5.2 Ejecucion por Disciplina

**Fecha:** 2026-04-22
**Origen:** smoke test funcional del panel organizador luego de US-5.2.1 y US-5.2.2
**Alcance:** mensajes de estado, filtros por torneo, acciones de fase y ergonomia del flujo organizador

## Resumen

Los hallazgos son mayormente de UX funcional y consistencia de lenguaje. Hay dos
hallazgos con impacto de regla de negocio:

- la transicion de `EJECUCION` a `PREMIACION` no deberia estar disponible si hay
  competencias sin ejecutar/finalizar;
- el selector de grilla no deberia ofrecer disciplinas que no pertenecen al torneo.

## Hallazgos

### UAT-5.2-01 — Estado vacio de inscriptos se comunica como error

**Severidad:** Media
**Area:** Frontend — panel de inscriptos

**Situacion observada:**

Cuando un torneo no tiene inscriptos, la pantalla muestra un mensaje del tipo
`No se pudieron cargar los inscriptos del torneo`.

**Problema:**

Ese texto comunica un error tecnico de carga, pero la ausencia de inscripciones
es un estado valido del negocio.

**Comportamiento esperado:**

- Si la API responde correctamente con lista vacia, mostrar un estado vacio:
  `Todavia no hay inscriptos para este torneo`.
- Si la API falla, mostrar un error real:
  `No se pudieron cargar los inscriptos del torneo`.

**Criterio de aceptacion:**

Con respuesta HTTP exitosa y lista vacia, la UI no debe mostrar mensaje de error.

---

### UAT-5.2-02 — El selector de disciplinas para grilla muestra opciones fuera del torneo

**Severidad:** Alta
**Area:** Frontend — generacion de grilla

**Situacion observada:**

En la generacion de grilla, el listbox de disciplinas puede mostrar disciplinas
que no estan configuradas para el torneo actual.

**Problema:**

El organizador puede intentar operar sobre disciplinas que no pertenecen al
torneo, lo que rompe la expectativa del flujo y puede generar errores evitables.

**Comportamiento esperado:**

El listbox debe incluir solo disciplinas definidas en el torneo consultado.

**Criterio de aceptacion:**

Dado un torneo configurado solo con `STA` y `DNF`, el selector de grilla muestra
solo `STA` y `DNF`.

---

### UAT-5.2-03 — Mensaje de jueces ambiguo o poco especifico

**Severidad:** Baja
**Area:** Frontend — panel de jueces

**Situacion observada:**

Al cargar jueces o disciplinas asignadas a jueces, el mensaje mostrado no deja
claro si se trata de carga, estado vacio o error.

**Problema:**

El usuario no puede distinguir entre:

- no hay jueces asignados;
- todavia se esta cargando la informacion;
- hubo un error tecnico.

**Comportamiento esperado:**

Separar los tres estados con mensajes distintos:

- loading: `Cargando jueces...`;
- vacio: `Todavia no hay jueces asignados`;
- error: `No se pudieron cargar los jueces`.

**Criterio de aceptacion:**

Cada estado de la consulta renderiza un mensaje distinto y no ambiguo.

---

### UAT-5.2-04 — La disciplina seleccionada en ejecucion no se destaca lo suficiente

**Severidad:** Baja
**Area:** Frontend — ejecucion por disciplina

**Situacion observada:**

En el tab `Ejecucion`, al seleccionar una disciplina para ver su detalle, la
relacion visual entre item seleccionado y panel detalle no es suficientemente
clara.

**Problema:**

El usuario puede perder contexto sobre que disciplina esta mirando, especialmente
cuando hay varias disciplinas listadas.

**Comportamiento esperado:**

Destacar la disciplina seleccionada y su detalle con un tratamiento visual
consistente, por ejemplo un azul tenue o borde/acento compartido.

**Criterio de aceptacion:**

Al seleccionar `DNF`, el item `DNF` y el panel detalle quedan visualmente
asociados sin depender solo del texto.

---

### UAT-5.2-05 — La transicion a premiacion debe depender del cierre de competencias

**Severidad:** Alta
**Area:** Frontend + regla de negocio de fase

**Situacion observada:**

En estado `EJECUCION`, la UI muestra una accion para avanzar a premiacion aunque
pueda existir una disciplina/competencia todavia en ejecucion o sin resultados
generados.

**Problema:**

La etapa de premiacion supone que las competencias del torneo ya fueron
ejecutadas y que los resultados necesarios estan generados. Avanzar a
`PREMIACION` antes de ese punto deja al torneo en una fase incoherente.

**Comportamiento esperado:**

- Cambiar el texto del boton de `Iniciar premiacion` a `Pasar a premiacion`.
- Habilitar `Pasar a premiacion` solo cuando todas las competencias del torneo
  esten finalizadas.
- Si hay competencias pendientes o en ejecucion, mantener la accion deshabilitada
  u oculta y mostrar el motivo.

**Criterio de aceptacion:**

Dado un torneo en `EJECUCION` con al menos una competencia en `EnEjecucion`,
el organizador no puede ejecutar la transicion a `PREMIACION`.

Dado un torneo en `EJECUCION` con todas sus competencias `Finalizada`, el
organizador ve la accion `Pasar a premiacion` habilitada.

---

### UAT-5.2-06 — Estados tecnicos de ejecucion confunden al organizador

**Severidad:** Media
**Area:** Frontend — ejecucion por disciplina

**Situacion observada:**

En el detalle de ejecucion aparecen carteles como `Configurar competencia` o
`Confirmar grilla antes de habilitar`.

**Problema:**

Desde la perspectiva del organizador, la ejecucion deberia ocurrir despues de
haber generado y confirmado las grillas necesarias. Esos mensajes exponen estados
tecnicos internos y pueden ser confusos si el flujo normal ya deberia haberlos
resuelto.

**Comportamiento esperado:**

- Si esos estados son imposibles en el flujo normal, no mostrarlos como estados
  principales de ejecucion.
- Si son posibles por datos incompletos, expresarlos como accion concreta:
  `Falta confirmar la grilla de DNF en el tab Grilla`.

**Criterio de aceptacion:**

El usuario entiende que accion debe realizar y en que tab, sin tener que conocer
el estado tecnico interno de la competencia.

---

### UAT-5.2-07 — Lenguaje de premiacion y cierre del torneo requiere precision

**Severidad:** Media
**Area:** Frontend — acciones de fase

**Situacion observada:**

El boton actual `Iniciar premiacion` no expresa con claridad la intencion del
usuario. Durante la revision se propuso `Finalizar Torneo`, pero el modelo de
dominio distingue dos pasos:

1. `EJECUCION -> PREMIACION`
2. `PREMIACION -> CERRADO`

**Problema:**

Usar `Finalizar Torneo` para pasar a premiacion mezclaria la transicion hacia
premiacion con el cierre definitivo del torneo.

**Comportamiento esperado:**

- Para `EJECUCION -> PREMIACION`, usar `Pasar a premiacion`.
- Para `PREMIACION -> CERRADO`, mantener o revisar como `Cerrar torneo`.

**Criterio de aceptacion:**

En `EJECUCION`, la accion visible es `Pasar a premiacion`.
En `PREMIACION`, la accion visible es `Cerrar torneo`.

---

### UAT-5.2-08 — Cancelar torneo necesita zona de peligro y confirmacion fuerte

**Severidad:** Media
**Area:** Frontend — acciones destructivas

**Situacion observada:**

La accion `Cancelar torneo` esta visualmente cerca de acciones operativas de fase.

**Problema:**

Cancelar un torneo es una accion destructiva o de alto impacto. Deberia estar
separada de las acciones normales y requerir confirmacion fuerte.

**Comportamiento esperado:**

- Mover `Cancelar torneo` a una region separada del layout, por ejemplo una
  zona de peligro.
- Pedir confirmacion escribiendo el nombre exacto del torneo.
- Ejecutar la cancelacion solo si el texto coincide.

**Criterio de aceptacion:**

El organizador no puede cancelar el torneo con un click accidental; debe ingresar
el nombre del torneo para confirmar.
