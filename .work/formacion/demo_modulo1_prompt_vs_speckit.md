# Demostración en vivo — Módulo 1
## El mismo problema, dos interacciones distintas

*Guion de clase · Duración estimada: 20–25 minutos*

---

## Contexto de la demostración

El objetivo no es mostrar que la IA produce código "malo" cuando el prompt es libre. La IA produce código perfectamente razonable. El objetivo es mostrar que **razonable no es lo mismo que correcto** en un dominio con invariantes de negocio, y que esa diferencia no es visible hasta que se los especifica explícitamente.

El dominio elegido es intencionalmente familiar: aplicar un cupón de descuento a un carrito de compra. Cualquier equipo de desarrollo ha implementado algo parecido. Esa familiaridad hace que la primera respuesta de la IA parezca suficiente —y es exactamente ahí donde está la trampa.

---

## Acto 1 — El prompt libre

**Lo que se escribe en el chat:**

```
Escribí en Python una función que aplique un cupón de descuento a un carrito 
de compra. El cupón puede ser de porcentaje o de monto fijo.
```

**Respuesta representativa del modelo** *(se ejecuta en vivo, el código varía pero el patrón es estable)*:

```python
from dataclasses import dataclass
from enum import Enum
from typing import List

class TipoCupon(Enum):
    PORCENTAJE = "porcentaje"
    MONTO_FIJO = "monto_fijo"

@dataclass
class Cupon:
    codigo: str
    tipo: TipoCupon
    valor: float
    activo: bool

@dataclass
class ItemCarrito:
    nombre: str
    precio: float
    cantidad: int

def aplicar_cupon(items: List[ItemCarrito], cupon: Cupon) -> float:
    if not cupon.activo:
        raise ValueError("El cupón no está activo")
    
    subtotal = sum(item.precio * item.cantidad for item in items)
    
    if cupon.tipo == TipoCupon.PORCENTAJE:
        descuento = subtotal * (cupon.valor / 100)
    else:
        descuento = cupon.valor
    
    return max(subtotal - descuento, 0)
```

**Pausa para el aula:** *¿Alguien encuentra algún problema con este código?*

Esperar respuestas. La mayoría dirá que se ve bien. Algunos señalarán que falta fecha de expiración. El código es limpio, tipado, razonable. Para la mayoría de los equipos, esto pasaría un code review sin objeciones.

---

## Acto 2 — El spec-kit

**Lo que se escribe en el chat** *(mostrar el documento completo en pantalla antes de enviarlo)*:

```
Contexto de dominio
-------------------
Sistema de e-commerce. Un carrito pertenece a un usuario y contiene ítems 
con precio unitario y cantidad. Un cupón tiene código único, tipo 
(porcentaje o monto fijo), valor, estado (activo/usado/expirado), 
categoría de producto opcional (null = aplica a todo), y un flag 
es_primer_compra.

Historia: Aplicar cupón de descuento al carrito

Precondiciones
--------------
- El carrito existe y tiene al menos un ítem
- El cupón existe en el sistema y su estado es "activo"
- El cupón no ha sido aplicado previamente a este carrito (idempotencia)
- Si el cupón tiene is_primer_compra=True, el usuario no debe tener 
  pedidos confirmados anteriores

Postcondiciones
---------------
- El total del carrito refleja el descuento aplicado
- El cupón queda registrado como "en uso" en este carrito (no "usado" 
  todavía — eso ocurre al confirmar el pedido)
- Se genera el evento CuponAplicado con: codigo_cupon, carrito_id, 
  monto_descuento, timestamp

Invariantes
-----------
- INV-1: El total final nunca puede ser menor a 0.01 (mínimo facturable)
- INV-2: Si el cupón tiene categoría asignada, el descuento aplica 
  exclusivamente sobre los ítems de esa categoría; los demás ítems 
  conservan su precio original
- INV-3: Un cupón de monto fijo mayor al subtotal elegible descuenta 
  hasta el mínimo facturable, no genera crédito
- INV-4: La función es idempotente: aplicar el mismo cupón dos veces 
  al mismo carrito produce el mismo resultado que aplicarlo una vez

Restricciones técnicas
----------------------
- Los montos se expresan en céntimos (enteros) para evitar errores de 
  punto flotante
- La función debe ser pura: no hace llamadas a base de datos ni efectos 
  secundarios. El evento se retorna como valor, no se persiste aquí.
```

**Respuesta representativa del modelo:**

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

class TipoCupon(Enum):
    PORCENTAJE = "porcentaje"
    MONTO_FIJO = "monto_fijo"

@dataclass(frozen=True)
class Cupon:
    codigo: str
    tipo: TipoCupon
    valor_centimos: int          # porcentaje * 100 o monto en céntimos
    categoria_id: Optional[str]  # None = aplica a todo
    es_primer_compra: bool

@dataclass(frozen=True)
class ItemCarrito:
    nombre: str
    precio_centimos: int
    cantidad: int
    categoria_id: str

@dataclass(frozen=True)
class CuponAplicado:
    """Evento de dominio — retornado como valor, no persistido aquí."""
    codigo_cupon: str
    carrito_id: str
    monto_descuento_centimos: int
    timestamp: datetime

MINIMO_FACTURABLE_CENTIMOS = 1

class CuponYaAplicadoError(Exception):
    pass

class CuponNoPrimerCompraError(Exception):
    pass

def aplicar_cupon(
    carrito_id: str,
    items: List[ItemCarrito],
    cupon: Cupon,
    cupon_ya_aplicado: bool,
    es_primer_pedido_usuario: bool,
) -> tuple[int, CuponAplicado]:
    """
    Aplica un cupón al carrito y retorna (total_centimos, evento).
    
    Precondiciones verificadas por el llamador:
    - cupon.estado == "activo" (verificado en capa de aplicación)
    
    Invariantes garantizados por esta función:
    - INV-1: total >= MINIMO_FACTURABLE_CENTIMOS
    - INV-2: descuento por categoría aplica solo a ítems elegibles
    - INV-3: cupón de monto fijo no genera crédito
    - INV-4: idempotencia — falla explícitamente si ya fue aplicado
    """
    # INV-4: idempotencia
    if cupon_ya_aplicado:
        raise CuponYaAplicadoError(
            f"El cupón {cupon.codigo!r} ya fue aplicado a este carrito"
        )

    # Precondición: primer compra
    if cupon.es_primer_compra and not es_primer_pedido_usuario:
        raise CuponNoPrimerCompraError(
            f"El cupón {cupon.codigo!r} es exclusivo para la primera compra"
        )

    subtotal_total = sum(i.precio_centimos * i.cantidad for i in items)

    # INV-2: subtotal elegible según categoría
    if cupon.categoria_id is not None:
        subtotal_elegible = sum(
            i.precio_centimos * i.cantidad
            for i in items
            if i.categoria_id == cupon.categoria_id
        )
    else:
        subtotal_elegible = subtotal_total

    # Cálculo del descuento
    if cupon.tipo == TipoCupon.PORCENTAJE:
        descuento = int(subtotal_elegible * cupon.valor_centimos / 10000)
    else:
        # INV-3: monto fijo no genera crédito
        descuento = min(cupon.valor_centimos, subtotal_elegible)

    # INV-1: total nunca menor al mínimo facturable
    total = max(subtotal_total - descuento, MINIMO_FACTURABLE_CENTIMOS)
    descuento_real = subtotal_total - total

    evento = CuponAplicado(
        codigo_cupon=cupon.codigo,
        carrito_id=carrito_id,
        monto_descuento_centimos=descuento_real,
        timestamp=datetime.utcnow(),
    )

    return total, evento
```

---

## Acto 3 — El análisis

Una vez que ambas respuestas están visibles en pantalla, se hace la comparación punto a punto. No como crítica al modelo —el modelo hizo exactamente lo que se le pidió en ambos casos— sino como evidencia de qué información determina la calidad del resultado.

**Lo que el prompt libre no podía producir porque nadie se lo dijo:**

| Invariante | Consecuencia de ignorarlo |
|-----------|--------------------------|
| Idempotencia (INV-4) | Un usuario puede aplicar el mismo cupón múltiples veces si hace doble clic o reintenta una llamada fallida |
| Cupón de primera compra | El cupón se aplica a cualquier usuario; el control de elegibilidad desaparece |
| Descuento por categoría (INV-2) | El descuento se aplica sobre el total del carrito, no solo sobre los productos de la categoría. Un cupón de electrónica descuenta también la ropa. |
| Mínimo facturable (INV-1) | Un cupón de €50 sobre un carrito de €30 podría devolver −€20, o cero, o generar un pedido de €0.00 |
| Céntimos en lugar de float | `0.1 + 0.2 == 0.30000000000000004`. En un sistema de facturación, ese error se acumula. |
| Evento de dominio | Sin el evento, no hay trazabilidad de qué cupón se aplicó, cuándo, y cuánto descuento generó. El cupón tampoco queda bloqueado para uso concurrente. |

**La pregunta que cierra el análisis:**

*¿Alguno de estos cinco problemas hubiera aparecido en un code review del primer código?*

Probablemente no. El código es limpio, compila, tiene tipos. Pero implementa una especificación incompleta con precisión perfecta.

---

## Qué muestra esta demostración

El problema no es la IA. La IA produjo exactamente lo que se le pidió en ambos casos.

El problema es que **en el primer caso nadie había pensado todavía qué quería exactamente**. El prompt libre genera la ilusión de haber especificado —porque produjo código— cuando en realidad solo se delegó el problema de especificación al modelo, que lo resolvió con los supuestos más probables.

En el segundo caso, el trabajo de pensar los invariantes ocurrió antes de interactuar con la IA. El modelo tradujo una especificación a código. En el primer caso, el modelo inventó la especificación y la tradujo a código al mismo tiempo. Esa diferencia no es visible en el código resultante. Solo se hace visible cuando el sistema llega a producción y un usuario aplica un cupón de primera compra por tercera vez.

La hipótesis central de IEDD es exactamente esa: **la calidad de la implementación está determinada por la calidad de la especificación, no por la calidad del modelo**. Con IA, esa relación se vuelve más urgente porque la velocidad de implementación ya no frena la propagación de una mala especificación.

---

## Notas para la ejecución

**Tiempo:** el Acto 1 toma 3–4 minutos (prompt + respuesta + pausa). El Acto 2 toma 5–7 minutos (mostrar el spec-kit antes de enviarlo, ejecutar, esperar). El Acto 3 toma 8–10 minutos (análisis + discusión).

**Variante si el tiempo es ajustado:** mostrar solo los Actos 1 y 3 con la respuesta del Acto 2 preparada de antemano. Perder el efecto en vivo vale la pena si el análisis gana profundidad.

**Qué hacer si el modelo libre produce algo más completo de lo esperado:** ocurre ocasionalmente. En ese caso, señalar qué invariantes siguen faltando. Si el modelo cubre todo, el punto sigue siendo válido: no fue predecible de antemano qué cubriría y qué no. La consistencia del resultado depende de haber especificado, no de la suerte del prompt.

**Dominio alternativo** si el e-commerce no resuena con el equipo: la misma estructura funciona con "registrar un turno médico" (invariantes: no superposición de horarios, máximo de turnos por profesional por día, cancelación con antelación mínima) o "transferir saldo entre cuentas" (invariantes: atomicidad, saldo no negativo, límite diario por usuario, evento de auditoría).

---

*Guion preparado por Víctor Valotto · Abril 2026*
