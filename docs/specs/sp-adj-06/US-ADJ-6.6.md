# US-ADJ-6.6: Corrección documental — FAZ → FAAS en documentación y código

**Estado**: `Pendiente`
**Iteración / Sprint**: SP-ADJ-06
**Agregado principal afectado**: N/A (corrección de lenguaje ubicuo)
**Bounded Context**: Transversal

---

## Descripción (lenguaje de negocio)

Como **equipo de desarrollo**,
quiero corregir el acrónimo "FAZ" a "FAAS" en todos los archivos del proyecto
para que la terminología del sistema use el nombre oficial correcto de la federación
argentina de apnea.

---

## Contexto del dominio

### Lenguaje ubicuo relevante

La federación argentina que organiza competencias de apnea es la **FAAS**:
**Federación Argentina de Actividades Subacuáticas**.

El proyecto usa incorrectamente "FAZ" en varios documentos y archivos de código.
Este error fue detectado y registrado como deuda en `memory/project_faz_faas_pendiente.md`
(pendiente desde SP-ADJ-05 diferido).

### Origen del error

El nombre "FAZ" fue introducido tempranamente en la documentación de dominio y se propagó
a través de varios artefactos sin corrección sistemática. No afecta al comportamiento
del sistema (es un error de nomenclatura en texto libre, no en enums ni en código de negocio).

---

## Especificación del comportamiento

### Operación

Esta US es una corrección documental de lenguaje ubicuo. No hay cambios de comportamiento.
La operación consiste en reemplazar todas las ocurrencias de "FAZ" por "FAAS" en los
archivos identificados.

### Precondición

`grep -r "FAZ" docs/ src/ tests/ --include="*.md" --include="*.py" --include="*.ts"` retorna al menos 9 ocurrencias.

### Postcondición

`grep -r "\bFAZ\b" docs/ src/ tests/` retorna 0 ocurrencias (búsqueda con word boundary
para no afectar palabras que contengan "FAZ" como parte de otra cadena, si las hubiere).

### Invariante

> El nombre oficial de la federación argentina de apnea es **FAAS** —
> Federación Argentina de Actividades Subacuáticas.
> Ningún documento ni comentario del proyecto debe usar "FAZ".

---

## Criterios de aceptación

```gherkin
Feature: Lenguaje ubicuo correcto — FAAS en lugar de FAZ

  Scenario: No quedan ocurrencias de "FAZ" en el proyecto
    Given el repositorio completo
    When se busca la cadena "FAZ" con word boundary en todos los archivos .md, .py, .ts
    Then no se encuentran ocurrencias

  Scenario: "FAAS" aparece correctamente en los contextos relevantes
    Given los documentos de dominio y las especificaciones
    When se busca "FAAS"
    Then aparece en los contextos donde antes decía "FAZ"
    And el significado del texto es correcto y coherente
```

---

## Impacto arquitectónico

**¿Esta US requiere una decisión arquitectónica?**
- [x] No — es corrección de texto en documentación y comentarios

**Archivos a verificar con grep (lista no exhaustiva):**
- `docs/dominio/`
- `docs/specs/`
- `docs/design/`
- `docs/adr/`
- `src/` (comentarios de código)
- `tests/` (docstrings, comments)

---

## Notas de implementación

1. Ejecutar primero: `grep -rn "\bFAZ\b" docs/ src/ tests/ --include="*.md" --include="*.py"`
   para obtener la lista exacta de archivos y líneas.
2. Reemplazar con búsqueda exacta de palabra completa para evitar falsos positivos.
3. Verificar el resultado con `grep -r "\bFAZ\b" docs/ src/ tests/` — debe retornar vacío.
4. No reemplazar en nombres de variables Python ni en strings de enums si los hubiere
   (aunque es improbable dado que es un nombre de federación, no un código técnico).

---

*Spec creada: 2026-04-16 — deuda heredada de SP-ADJ-05 diferido (memory/project_faz_faas_pendiente.md)*
