# Escenarios — Fase F-02: Creación del Torneo

## Criterio de Entrada

- [ ] F-01 completada: usuarios autenticables · portal público accesible
- [ ] Backend y frontend levantados

## Datos a ingresar

| Campo | Valor |
|-------|-------|
| Nombre | Apnea Indoor Buenos Aires 2025 |
| Sede nombre | Club Náutico Buenos Aires |
| Sede ciudad | Buenos Aires |
| Sede país | Argentina |
| Fecha inicio | 2025-06-14 |
| Fecha fin | 2025-06-15 |
| Entidad organizadora | Freediving Argentina |
| Tipo entidad | ASOCIACION |
| Disciplinas | DBF · DNF · DYN · SPE · STA |
| Categorías | JUNIOR · SENIOR · MASTER |

## Escenarios

| ID | Actor | Dispositivo | Acción | Resultado esperado | Resultado real | Estado | Hallazgo |
|----|-------|-------------|--------|--------------------|----------------|--------|----------|
| F02-S01 | Organizador | Desktop | Crear torneo con todos los datos del dataset | Torneo creado · `torneo_id` visible o accesible | — | ⬜ PENDIENTE | — |
| F02-S02 | Organizador | Desktop | Configurar disciplinas: DBF, DNF, DYN, SPE, STA | 5 disciplinas asociadas | — | ⬜ PENDIENTE | — |
| F02-S03 | Organizador | Desktop | Configurar categorías: JUNIOR, SENIOR, MASTER | Categorías guardadas | — | ⬜ PENDIENTE | — |
| F02-S04 | Visitante | Cualquier | Refrescar `/portalapnea` | Torneo aparece en lista (estado CREADO) | — | ⬜ PENDIENTE | — |
| F02-S05 | Organizador | Desktop | Ver lista de torneos en portal organizador | Torneo aparece ordenado por fecha | — | ⬜ PENDIENTE | — |

## Registro de torneo_id

**Anotar aquí el `torneo_id` generado — requerido para Seed-B:**

```
torneo_id: ________________________________
```

## Criterio de Salida

- [ ] Torneo creado con 5 disciplinas y 3 categorías
- [ ] `torneo_id` registrado
- [ ] Torneo visible en portal organizador
- [ ] Estado: `CREADO`
