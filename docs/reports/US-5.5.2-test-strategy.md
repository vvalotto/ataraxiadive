# US-5.5.2 - Test Strategy

**Fecha:** 2026-04-26

---

## Objetivo

Validar que la vista operativa del organizador muestre solo inscriptos activos y que el estado AP visible por disciplina sea consistente con el flujo del atleta.

---

## Capas cubiertas

### Integracion backend

- `tests/integration/registro/test_inscriptos_detalle_endpoint.py`
  - devuelve solo inscripciones activas;
  - devuelve AP por disciplina si existe;
  - rechaza acceso con rol `ATLETA`.

### Calidad frontend

- `npm run lint`
- `npm run build`

Estas validaciones cubren:

- coherencia de tipos del nuevo DTO;
- uso correcto del endpoint nuevo;
- integridad de JSX/TS en el panel organizador.

---

## No cubierto

- Browser automation del flujo del organizador.
- `codeguard` especifico de esta US.

---

## Riesgo residual

El principal riesgo residual es visual: el shell general del organizador sigue parcialmente desalineado respecto del prototipo global, aunque la vista de inscriptos ya cumple la semantica funcional de la spec.
