# Estrategia de Tests - US-5.5.1

## Alcance

US-5.5.1 toca cuatro frentes:

- payload JWT de identidad;
- consulta de inscripciones del atleta;
- comando/API de registrar AP;
- shell y pantallas del portal atleta en frontend.

## Estrategia aplicada

### Backend

- test focalizado de JWT:
  - verificar que el payload incluya `nombre` y `apellido`.

- test focalizado de `RegistrarAPHandler`:
  - mantener camino feliz;
  - permitir modificar AP mientras la performance siga en `AnunciadaAP`;
  - rechazar modificacion cuando la performance ya avanzo.

### Frontend

- `npm run build` como gate principal:
  - tipado de rutas nuevas;
  - integracion de stores y clientes API;
  - consistencia de imports y componentes del portal atleta.

- `npm run lint`:
  - enforcement de reglas React/TS del repo;
  - correccion de inicializacion de estado para evitar `set-state-in-effect`.

- `codeguard`:
  - gate deseable sobre BCs tocados;
  - en esta corrida quedo pendiente/no concluido por falta de salida utilizable del comando.

## Waivers

- No hay suite automatizada React/DOM para montar el portal atleta.
- No se agrego prueba automatizada de uploads porque el backend no persiste archivos en esta iteracion.
- No se agrego prueba end-to-end del endpoint `GET /registro/atletas/{id}/inscripciones` en esta regularizacion.

## Riesgo residual

La mayor parte del riesgo remanente queda en integracion UI/manual:

- navegacion real entre pantallas en browser;
- compatibilidad de la inferencia `AP cerrado` basada en `torneo.estado`;
- ausencia de persistencia real de adjuntos del wizard.
