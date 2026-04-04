# HITO-18 — El prototipo navegable como etapa de validación entre especificación e implementación

| Campo | Valor |
|-------|-------|
| **Documento** | HITO-18 — Hallazgo metodológico al inicio de INC-4.0 |
| **Fecha** | 2026-04-04 |
| **Sprint** | SP4 — La Plataforma — inicio de INC-4.0 |
| **Relacionado** | `docs/design/ux/README.md` · `docs/plans/sp4/PLAN-SP4.md` |

---

## Contexto

Al iniciar INC-4.0 —el primer incremento con frontend real en el proyecto—, el plan
original preveía producir cinco artefactos Markdown (`flujos-por-rol.md`,
`wireframes-*.md`, `decisiones-frontend.md`) como especificaciones de diseño para Code.

La primera pregunta de Victor fue directa: *"¿cómo valido la interfaz si no tengo
una visualización de alguna maqueta o wireframe?"*

Esa pregunta expuso un gap en el proceso que no era evidente en los sprints anteriores
—porque los sprints anteriores no tenían interfaz de usuario.

---

## El gap identificado

El proceso IEDD en sprints de backend sigue esta cadena:

```
Dominio → Modelo DDD → Especificación (US-IEDD) → Implementación
```

En esa cadena, la especificación es textual (precondiciones, postcondiciones, invariantes,
escenarios BDD) y es suficiente porque el dominio es lógica de negocio: o una regla
se cumple o no se cumple, y eso se puede verificar con tests automatizados.

Cuando aparece el frontend, emerge una dimensión nueva: **la interacción física**.

La interfaz del juez de AtaraxiaDive tiene restricciones que no son verificables con
tests ni con revisión de texto:
- Botones ≥ 48px — ¿se toca cómodamente con el dedo mojado en el borde de la pileta?
- Alto contraste — ¿se lee bajo sol directo?
- ≤ 6 toques por performance — ¿el flujo es naturalmente ejecutable sin mirar la pantalla?
- Tarjeta amarilla como estado transitorio — ¿el juez entiende sin texto de ayuda que
  debe resolver antes de cerrar?

Ninguna de estas preguntas tiene respuesta en un archivo Markdown. La especificación
puede describir la restricción, pero no puede validarla. Solo el ojo y el dedo en una
pantalla real pueden hacerlo.

El gap es este: **entre la especificación y la implementación, cuando hay UX con
restricciones físicas, falta una etapa de validación visual e interactiva**.

---

## La decisión tomada

Se acordó un proceso en dos pasos por cada pantalla o flujo:

```
Paso 1 — Prototipo navegable (HTML autocontenido)
    → Creado por Cowork
    → Renderizado en el chat via Claude in Chrome (GIF del flujo)
    → Abierto por Victor en el celular — validación táctil real
    → Iteración hasta aprobación visual

Paso 2 — Spec Markdown formal
    → Escrita por Cowork a partir del prototipo aprobado
    → Consumida por Code en /implement-us
    → Commiteada al repo junto con el prototipo HTML
```

El prototipo no reemplaza la spec — la precede y la fundamenta. La spec sigue siendo
el artefacto que Code consume. Pero la spec ahora describe algo que fue validado
físicamente, no solo conceptualmente.

Los prototipos se guardan en `docs/design/ux/prototipos/` y se commitean al repo.
No son descartables: son documentación viva del diseño que sirve de referencia
para SP5 cuando haya usuarios reales haciendo pruebas.

---

## El aprendizaje central

> Cuando una US-IEDD afecta una interfaz con restricciones físicas de uso,
> la especificación textual es necesaria pero no suficiente como entrada para
> la implementación. Se necesita una etapa intermedia de prototipado navegable
> que permita validar la interacción antes de formalizarla en código.

Esta etapa no es optativa cuando:
- El usuario opera bajo condiciones físicas adversas (manos mojadas, sol, tensión)
- La densidad de información por pantalla está restringida (≤ 6 toques)
- Los estados de la UI mapean a estados del dominio con invariantes duros
  (tarjeta amarilla que bloquea el cierre de disciplina)
- El dispositivo de uso difiere del dispositivo de desarrollo (mobile vs desktop)

En esos casos, el prototipo navegable actúa como un **oráculo de interacción**: no
verifica la lógica de negocio (eso lo hace el test), verifica que la interacción
diseñada es ejecutable en las condiciones reales de uso.

---

## Implicancia para IEDD como metodología

La cadena de 5 capas de IEDD no contempla explícitamente la validación de UX. Para
proyectos con frontend, la Capa 3 (Especificación) debería distinguir dos sub-tipos:

```
Capa 3a — Especificación de comportamiento (US-IEDD clásica)
          → precondiciones, postcondiciones, invariantes, BDD
          → suficiente para backend puro

Capa 3b — Especificación de interacción (cuando hay UI con restricciones físicas)
          → prototipo navegable aprobado → spec formal derivada del prototipo
          → necesaria cuando el dispositivo de uso o las condiciones físicas
            no pueden inferirse del texto
```

La distinción no invalida el proceso — lo extiende. Los proyectos sin UI o con UI
convencional (desktop, sin restricciones físicas) pueden operar con Capa 3a solamente.
Cuando el uso físico importa, Capa 3b se vuelve obligatoria antes de implementar.

---

## Herramienta que habilitó el proceso

**Claude in Chrome** es la pieza que cierra el ciclo dentro del mismo entorno de trabajo:
permite crear un HTML, abrirlo en el browser, navegar el prototipo, grabar un GIF del
flujo, y mostrarlo en el chat — sin salir de la sesión Cowork. Esto reduce la fricción
de validación al mínimo y hace que el ciclo prototipo → feedback → ajuste sea rápido
enough para iterar en una sesión.

Sin esa capacidad, el ciclo requeriría que el desarrollador abra un archivo externo,
tome capturas manualmente, y las comparta en el chat — agregando fricción suficiente
como para saltearse la validación.

---

## Regla práctica identificada

> Para cualquier pantalla con restricciones físicas de uso, el proceso es:
> prototipo navegable validado en el dispositivo real → spec formal → implementación.
> No existe atajo: la spec sin prototipo previo produce interfaces que fallan la
> validación táctil aunque sean correctas en papel.

---

## Acción incorporada

- [x] Proceso documentado en `docs/design/ux/README.md`
- [x] Prototipo HTML como artefacto de primera clase en INC-4.0
- [x] Carpeta `docs/design/ux/prototipos/` definida en la estructura del proyecto
- [ ] Evaluar si la plantilla US-IEDD debería incluir un campo
      "¿requiere prototipo navegable?" con criterio de decisión basado en
      restricciones físicas de uso

---

*Registrado al inicio de INC-4.0 — la pregunta sobre validación que reveló el gap entre spec e implementación en proyectos con frontend físicamente restringido*
