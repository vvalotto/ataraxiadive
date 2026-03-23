# US-1.4.1 — Black-out con Distancia

| Campo | Valor |
|-------|-------|
| **ID** | US-1.4.1 |
| **Incremento** | 1.4 |
| **BC** | Competencia |
| **Actor** | Juez |
| **RFs** | RF-EJ-07 |
| **Invariantes** | INV-P-07, INV-P-11 + nuevo: distancia_blackout obligatoria |

---

## Historia de Usuario

Como juez, quiero registrar un black-out con la distancia alcanzada por el atleta,
para que el resultado quede documentado correctamente según las reglas de la competencia.

---

## Precondición

Performance en estado `ResultadoRegistrado`.

## Postcondición

`TarjetaAsignada` persiste con `tipo = Roja`, `motivo = "black-out"` y
`distancia_blackout > 0`. Performance en estado `Ejecutada`.

## Invariantes

- INV-P-07: `AsignarTarjeta` solo si `ResultadoRegistrado` previo
- INV-P-11: `motivo` obligatorio para tarjeta Roja
- **RF-EJ-07**: `distancia_blackout` obligatoria y > 0 cuando `motivo == "black-out"`
- Tarjeta roja sin black-out: sin cambio de comportamiento

---

## Notas de implementación

- No se introduce un nuevo comando — es una extensión de `AsignarTarjeta` (US-1.2.4)
- `distancia_blackout` es un campo opcional en `TarjetaAsignada`; solo obligatorio si `motivo == "black-out"`
- La validación vive en el aggregate `Performance`, no en el handler
