# Plan de Implementacion - US-ADJ-9.5: Resultados dentro del shell aprobado

**Sprint:** SP-ADJ-09
**Patron:** React/Vite frontend
**Estimacion total:** 120 min

---

## Diagnostico

`ResultadosPage.tsx` ya cumple buena parte del alcance funcional heredado de
`US-5.6.5` y `US-5.6.6`: selector de torneo, tabla por disciplina, podios por
categoria y bloqueo/disponibilidad del overall. El gap actual es de shell y
composicion UX:

- superficies claras dentro del shell dark;
- header y subtitulo poco alineados a `S-04`;
- jerarquia visual difusa entre tabla de disciplina y overall;
- selector inicial de torneo y secciones secundarias con estilo heredado.

La US no requiere cambios de backend ni de dominio. Debe reencuadrar
`ResultadosPage` y sus componentes para que la experiencia quede consistente con
el organizador post `US-ADJ-9.4`.

---

## Cambios por area

### 1. Reencuadre de `ResultadosPage`

- [ ] Rehacer el estado selector de torneo bajo lenguaje visual dark (15 min)
  - mantener `torneo_id` como entrada de contexto
  - alinear cards, botones y copy al shell del organizador

- [ ] Ajustar el header operativo de la pantalla (15 min)
  - subtitulo con torneo + disciplina activa + estado del ranking/progreso
  - accion principal consistente con `S-04`
  - evitar framing de "volver" como accion dominante

- [ ] Reorganizar el layout principal en dos columnas (20 min)
  - columna principal para ranking/tabla por disciplina
  - columna secundaria para overall y/o resumen relacionado
  - preservar responsividad razonable para pantallas menores

### 2. Refinamiento de bloques visuales

- [ ] Reestilizar selector de disciplina y contenedor de tabla (15 min)
  - tabs dark coherentes con shell
  - estados de carga/error/empty dentro del mismo lenguaje visual

- [ ] Reestilizar `PodiosSection` y `PanelCategoria` para el shell dark (20 min)
  - adaptar bordes, fondos, subtitulos y empty states
  - reforzar separacion visual entre podios de disciplina y overall

- [ ] Revisar jerarquia visual del overall (10 min)
  - bloqueado: empty state claro
  - disponible: misma familia visual pero distinguible del bloque principal

### 3. Conservacion funcional

- [ ] Mantener sin regresion la funcionalidad de tabla por disciplina (5 min)
- [ ] Mantener sin regresion la funcionalidad de podios por categoria (5 min)
- [ ] Mantener sin regresion la disponibilidad condicional del overall (5 min)

### 4. Validacion

- [ ] Crear escenario BDD fisico de `US-ADJ-9.5` y mantenerlo alineado con la implementación (5 min)
- [ ] `npm run build` en `frontend/` (5 min)
- [ ] `npm run lint` en `frontend/` (5 min)
- [ ] Validacion manual de:
  - shell dark en Resultados
  - item activo en navbar
  - claridad visual entre disciplina y overall
  - conservacion de tabla y podios (10 min)

---

## Decisiones clave

- No tocar reglas de negocio ni algoritmos de ranking/overall.
- Priorizar reutilizacion de la logica de datos ya existente en `ResultadosPage`.
- Resolver la US desde composición UX y no desde una reimplementacion completa.
- Mantener `Resultados` como seccion primaria del shell del organizador.

---

## Riesgos y mitigaciones

- Riesgo: romper la tabla actual al forzar layout nuevo.
  Mitigacion: aislar los cambios a contenedores, header y estilos antes que a la logica de join.

- Riesgo: uniformar demasiado disciplina y overall y perder jerarquia.
  Mitigacion: usar bloques y subtitulos claramente diferenciados.

- Riesgo: introducir deuda duplicando componentes.
  Mitigacion: ajustar `PodiosSection` y `PanelCategoria` existentes en lugar de recrearlos.

---

## Criterio de salida

La implementación de esta US termina cuando:

1. `Resultados` vive visualmente dentro del shell dark aprobado;
2. la tabla de disciplina, los podios y el overall conservan sus capacidades;
3. la relacion visual entre disciplina y overall queda clara y consistente con `S-04`;
4. build y lint quedan ejecutados;
5. los artefactos de documentación y reporte final quedan creados antes del commit.
