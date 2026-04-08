# ADR-014: Penalizaciones acumulables como tarjeta válida con RP penalizado

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-04-08 |
| **Autores** | Victor Valotto |
| **Relacionado** | ADR-004, ADR-005, ADR-006, US-4.1.2 |

---

## Contexto

El modelo vigente de `Performance` distingue tres resultados finales: `Blanca`,
`Amarilla` y `Roja`. Ese modelo no alcanza para representar un caso reglamentario
relevante: una performance válida con infracciones técnicas acumulables que reducen
la marca final sin descalificar al atleta.

La especificación `US-4.1.2` introduce ese caso como **Tarjeta Blanca con penalizaciones**.
Esto exige resolver tres puntos de diseño:

1. cómo representar una tarjeta válida pero distinta de `Blanca`;
2. cómo conservar simultáneamente la marca medida y la marca efectiva para ranking;
3. cómo modelar penalizaciones acumulables sin convertir el aggregate en una estructura ad hoc.

## Opciones consideradas

**Opción A — modelar las penalizaciones como una variante de Amarilla**

Reutiliza el concepto existente, pero mezcla semánticas distintas:
- `Amarilla` hoy representa revisión/incertidumbre;
- la nueva tarjeta representa resultado cerrado y válido.

**Opción B — mantener una sola tarjeta Blanca y guardar penalizaciones como detalle auxiliar**

Reduce cambios en el enum, pero oculta una diferencia de negocio importante y
obliga a inferir el estado real desde campos secundarios.

**Opción C — introducir `BlancaConPenalizaciones` como tarjeta válida explícita**

Hace visible el concepto del dominio, permite expresar el resultado final sin
ambigüedad y mantiene reglas de ranking simples: sigue siendo una performance válida.

## Decisión

Se adopta **Opción C**.

### Modelo resultante

- `TipoTarjeta` incorpora `BlancaConPenalizaciones`.
- Las penalizaciones se modelan como lista de value objects `PenalizacionTecnica`.
- `Performance` conserva:
  - `rp_medido`: marca física original;
  - `rp_penalizado`: marca efectiva luego de deducciones;
  - `rp`: propiedad compatible que retorna `rp_penalizado` si existe, o `rp_medido` en caso contrario.

### Reglas de negocio formalizadas

- `BlancaConPenalizaciones` es **resultado válido**.
- Requiere al menos una penalización.
- El RP final se calcula restando la suma de deducciones al RP medido.
- Si la suma supera el RP medido, el resultado final se clampa a `0`.
- Solo aplica a disciplinas dinámicas; esa validación vive en el handler de aplicación.

## Consecuencias

**Positivas**

- El lenguaje ubicuo queda explícito: una performance puede ser válida y penalizada.
- El ranking no necesita una rama nueva compleja: consume `rp` y considera la nueva tarjeta como válida.
- La auditoría del evento mejora: se preservan tanto `rp_medido` como las penalizaciones aplicadas.

**Negativas**

- `TarjetaAsignada` amplía su payload y aumenta el costo de compatibilidad.
- `Performance` incorpora más estado derivado.
- Tests y adaptadores de resultados deben asumir una cuarta tarjeta final válida.

## Notas de implementación

- `PenalizacionTecnica` se modela como value object inmutable con código y deducción.
- El payload de `TarjetaAsignada` agrega:
  - `penalizaciones`
  - `rp_medido`
  - `rp_penalizado`
- `RankingCompetencia` debe tratar `BlancaConPenalizaciones` como tarjeta válida.
