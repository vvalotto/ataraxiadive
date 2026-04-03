# Plan de Implementacion — US-ADJ-3.5

## Resumen

Actualizar `disciplina_descriptor_port.py` para que importe `Disciplina` y
`DisciplinaDescriptor` desde `shared.domain.value_objects`, eliminando la
dependencia innecesaria sobre re-exports del BC `competencia`.

## Objetivo observable

- `disciplina_descriptor_port.py` deja de importar desde
  `competencia.domain.value_objects`
- el contrato del puerto permanece identico
- no aparecen nuevos cambios funcionales ni dependencias extra

## Alcance

- `src/competencia/domain/ports/disciplina_descriptor_port.py`
- validacion focalizada sobre `competencia`
- artefactos de tracking, calidad y reporte de la US

No incluye:

- cambios de comportamiento
- nuevos activos BDD
- cambios en adapters o handlers

## Implementacion prevista

1. reemplazar imports hacia `shared.domain.value_objects`
2. verificar si hay otros ports con el mismo patron y confirmar que no
   requieren ajuste en esta US
3. correr validacion focalizada y gates de calidad

## Validacion prevista

- `grep "competencia.domain.value_objects" src/competencia/domain/ports`
- `pytest tests/unit/competencia/application/test_configurar_intervalo_ot_handler.py tests/unit/competencia/application/test_obtener_competencias_por_torneo.py -q`
- `py_compile src/competencia/domain/ports/disciplina_descriptor_port.py`
- `CodeGuard src/competencia/domain/ports/disciplina_descriptor_port.py`
- `git diff --check`

## Riesgos a controlar

1. ninguno funcional; el unico riesgo real es dejar algun import viejo sin detectar
2. sobredimensionar una US cosmética con cambios que no pertenecen al alcance

## Artefactos esperados al cierre

- port apuntando a la fuente canonica en `shared.domain`
- reporte final y evidencia de calidad
