# US-5.5.1: Inscripción completa del atleta + Declarar/Modificar AP

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.5
**Bounded Context**: `registro` + `competencia` + `frontend`
**Capas afectadas**: `frontend/src/pages/atleta/`, `frontend/src/components/atleta/`, `registro/api/`, `competencia/api/`, `identidad/`

---

## Descripcion

Como **atleta**,
quiero **inscribirme a un torneo mediante el flujo UX aprobado y luego declarar o modificar mi AP por disciplina antes del cierre**,
para **gestionar mi participación completa desde el portal del atleta, con navegación móvil y estados claros por torneo y disciplina**.

---

## Fuente de verdad UX

Esta US se redefine tomando como contrato primario:

- `docs/design/ux/flujos-por-rol.md`
- `docs/design/ux/wireframes-atleta.md`
- `docs/design/ux/prototipos/prototipo-atleta.html`
- `.work/revision-sp5/04-hallazgos-ux-portal-atleta.md`

En particular corrige los gaps `UX-ATL-01..03`, `UX-ATL-08..12`.

---

## Contexto de diseño

El flujo aprobado para el atleta no es un dashboard único con paneles inline. La UX define:

1. shell móvil dark (`max-width: 430 px`) con `header` sticky y `tabbar` inferior persistente
2. navegación entre pantallas `S-01..S-08`
3. wizard de inscripción `S-04` con 3 pasos
4. pantalla dedicada `S-05 Mis inscripciones`
5. pantalla dedicada `S-06 Declarar / Modificar AP`

Esta US debe respetar esa estructura. Cualquier decisión técnica debe adaptarse al flujo UX, no reemplazarlo.

---

## Alcance funcional

### A. Shell base del portal del atleta

El portal del atleta debe usar el shell definido en UX:

- tema dark con tokens de `wireframes-atleta.md`
- header sticky
- tab bar persistente con tabs `Inicio`, `Torneos`, `Mis inscr.`, `Resultados`
- navegación por pantallas/rutas, no composición single-page obligatoria

### B. S-03 / S-04 — Inscripción completa

El atleta debe poder abrir el detalle del torneo y ejecutar el wizard `Inscribirme` de 3 pasos:

- **Paso 1 — Personales**: correo readonly, nombre y apellido, fecha de nacimiento, género, documento, teléfono
- **Paso 2 — Competencia**: selección de disciplinas, categoría calculada/revisable, nº brevet opcional
- **Paso 3 — Requisitos**: certificado médico y comprobante de pago obligatorios

El envío genera una inscripción en estado de verificación.

### C. S-05 — Mis inscripciones

La pantalla debe concentrar el estado de participación por torneo y disciplina:

- sección `En ejecución`
- sección `Inscripciones abiertas`
- estado visible por disciplina
- `deadline` de cierre de anuncios visible cuando corresponda

### D. S-06 — Declarar / Modificar AP

El AP se declara o modifica desde una pantalla dedicada, no inline:

- card de contexto con torneo, disciplina y horario
- input principal de AP
- deadline visible
- acción `Guardar AP`

La UX aprobada exige **ingresar / modificar AP** antes del cierre. No se permite redefinir esta historia como “alta única” si el período de anuncios sigue abierto.

---

## Invariantes

- **INV-5.5.1-01:** El portal del atleta usa shell móvil dark y tab bar persistente según `wireframes-atleta.md`.
- **INV-5.5.1-02:** La inscripción al torneo se realiza mediante wizard de 3 pasos; no puede reducirse a un panel inline de disciplinas.
- **INV-5.5.1-03:** Certificado médico y comprobante de pago son obligatorios para completar la inscripción (`INV-ATL-08`).
- **INV-5.5.1-04:** La categoría competitiva debe poder revisarse antes del envío y deriva de la fecha de nacimiento (`INV-ATL-07`).
- **INV-5.5.1-05:** El atleta puede declarar **o modificar** su AP mientras el período de anuncios siga abierto (`INV-ATL-01`).
- **INV-5.5.1-06:** Una vez cerrado el período de anuncios, la UI pasa a estado de solo lectura y muestra `AP cerrado`.
- **INV-5.5.1-07:** Durante la ejecución de la performance, la experiencia del atleta es solo lectura.

---

## Especificacion del comportamiento

### Operacion principal 1 — inscribirse a un torneo

**Flujo UX:**

```text
S-02 Torneos
  -> S-03 Detalle del torneo
      -> CTA "Inscribirme en este torneo"
          -> S-04 Inscribirme (wizard 3 pasos)
              -> Enviar inscripción
                  -> S-05 Mis inscripciones
```

**Comportamiento esperado:**

- el paso 1 precarga la información conocida del atleta y permite completarla/corregirla
- el paso 2 selecciona disciplinas y muestra categoría calculada
- el paso 3 exige ambos adjuntos antes de habilitar `Enviar inscripción`
- al enviar, la inscripción queda visible en `S-05`

### Operacion principal 2 — declarar o modificar AP

**Flujo UX:**

```text
S-05 Mis inscripciones
  -> fila de disciplina con estado "AP pendiente"
      -> CTA "Declarar AP"
          -> S-06 Declarar / Modificar AP
              -> Guardar AP
                  -> vuelve a S-05
```

**Comportamiento esperado:**

- si no existe AP previo, `S-06` opera como alta
- si ya existe AP y el período sigue abierto, `S-06` opera como modificación
- al guardar, `S-05` refleja el nuevo valor y actualiza el estado visual
- cuando el organizador cierra el período de anuncios, el CTA desaparece y la disciplina muestra `AP cerrado`

### Unidades y disciplina

La pantalla `S-06` debe adaptarse al tipo de disciplina:

- dinámicas (`DNF`, `DYN`, `DYNB`, `DBF`) -> input de distancia
- estáticas (`STA`) -> input de tiempo

La UX de referencia explicita que la estática requiere un comportamiento distinto al mock base de metros.

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.5.1 — Inscripción completa del atleta y declaración de AP

  Background:
    Given existe el torneo "BA Open 2026" publicado con inscripciones abiertas
    And el atleta "ana@email.com" accede al portal del atleta

  Scenario: atleta completa la inscripción con wizard de 3 pasos
    When navega a "Torneos"
    And abre el detalle del torneo "BA Open 2026"
    And presiona "Inscribirme en este torneo"
    And completa Personales, Competencia y Requisitos
    Then el sistema registra la inscripción
    And la inscripción queda visible en "Mis inscripciones"
    And el estado queda "pendiente de verificación"

  Scenario: no se puede enviar inscripción sin ambos adjuntos obligatorios
    Given el atleta está en el paso 3 "Requisitos"
    When intenta enviar la inscripción sin certificado médico
    Then la UI bloquea el envío
    And informa que el certificado médico es obligatorio

  Scenario: atleta declara AP desde pantalla dedicada
    Given el atleta ya está inscripto en DNF
    And el período de anuncios sigue abierto
    When desde "Mis inscripciones" presiona "Declarar AP"
    And guarda AP=70 metros
    Then vuelve a "Mis inscripciones"
    And la disciplina DNF muestra el AP guardado

  Scenario: atleta modifica AP antes del cierre
    Given el atleta ya declaró AP=70 para DNF
    And el período de anuncios sigue abierto
    When vuelve a "Declarar AP"
    And cambia el valor a 72 metros
    Then la disciplina DNF muestra AP=72

  Scenario: AP queda solo lectura después del cierre
    Given el atleta ya declaró AP para DNF
    And el organizador cerró el período de anuncios
    When el atleta abre "Mis inscripciones"
    Then la disciplina muestra chip "AP cerrado"
    And no existe CTA "Declarar AP"
```

---

## Impacto arquitectonico

- [x] Sí — corrige una desviación de UX e impacta navegación, composición de pantallas y contratos de backend.

### Capas afectadas

- `frontend/src/pages/atleta/` — pantallas `S-02` a `S-06`
- `frontend/src/components/atleta/` — shell, tab bar, stepper, upload areas, filas de inscripción
- `registro/api/` — soporte para inscripción completa con datos y requisitos
- `competencia/api/` — alta/modificación de AP dentro del período habilitado
- `identidad/` — perfil del atleta visible en portal si faltan datos civiles básicos

### Nota de modelado

La decisión de permitir modificar AP mientras el período siga abierto proviene de la UX aprobada y de `flujos-por-rol.md`. Si el dominio actual solo soporta alta única, deberá ajustarse backend o agregarse operación explícita de actualización compatible con el cierre de anuncios.

---

## Referencias

- `docs/design/ux/flujos-por-rol.md §3 Rol: Atleta`
- `docs/design/ux/wireframes-atleta.md §S-03..S-06`
- `docs/design/ux/prototipos/prototipo-atleta.html`
- `.work/revision-sp5/04-hallazgos-ux-portal-atleta.md`

---

*Redefinido: 2026-04-25 — INC-5.5 reiniciado desde UX aprobada*
