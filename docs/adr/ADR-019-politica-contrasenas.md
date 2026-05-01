# ADR-019: Política de contraseñas y UX de fortaleza

| Campo | Valor |
|-------|-------|
| **Estado** | Aceptada |
| **Fecha** | 2026-04-24 |
| **Autores** | Victor Valotto |
| **Relacionado con** | US-5.4.1, US-5.4.2, US-5.4.3 · `identidad/domain/exceptions.py` |

---

## Contexto

Durante el smoke test de INC-5.4 se identificó que la política de contraseñas
original (mínimo 8 caracteres) era insuficiente para una plataforma que maneja
datos de atletas y resultados de competencias oficiales. Se tomaron tres decisiones
de diseño en conjunto: la política mínima, el campo de confirmación en el registro,
y el indicador visual de fortaleza.

---

## Decisiones

### 1. Política de contraseñas

**Regla:** mínimo 10 caracteres + al menos 1 mayúscula + al menos 1 número.

**Aplicada en:** `RegistrarUsuarioHandler`, `CambiarPasswordHandler`, `ResetPasswordHandler`.
**Excepción:** `PasswordDemasiadoCorto` — mensaje: _"La contraseña debe tener al menos
10 caracteres, una mayúscula y un número"_.

### 2. Campo de confirmación de contraseña

**Regla:** el formulario de auto-registro (`RegistroPage`) requiere confirmar la
contraseña antes de enviar. La validación es exclusivamente frontend — el backend
no recibe el campo de confirmación.

**Aplicada en:** `RegistroPage.tsx`.

### 3. Indicador de fortaleza

Barra visual con 3 niveles, calculada en tiempo real mientras el usuario tipea:

| Nivel | Color | Criterio |
|-------|-------|----------|
| **Débil** | Rojo | No cumple alguno de los 3 criterios mínimos |
| **Buena** | Amarillo | Cumple los 3 criterios (10+, mayúscula, número) |
| **Fuerte** | Verde | 14+ caracteres + cumple los 3 criterios |

**Aplicada en:** `RegistroPage`, `CambiarPasswordPage`, `ResetPasswordPage`.
**Componente:** `frontend/src/components/PasswordStrengthBar.tsx`.

---

## Justificación

**Sobre la política:**

- **Longitud sobre complejidad:** NIST SP 800-63B (2017) desaconseja las reglas de
  complejidad excesiva (mayúsculas + símbolos + números obligatorios) porque llevan
  a patrones predecibles (`Password1!`). La recomendación es priorizar longitud.
- **10 caracteres:** aumenta el espacio de búsqueda exponencialmente respecto a 8.
  Para un ataque de fuerza bruta sobre un hash bcrypt, pasar de 8 a 10 caracteres
  multiplica el tiempo de cómputo por un factor del orden de 10⁴ en el caso de
  caracteres alfanuméricos.
- **1 mayúscula + 1 número:** regla mínima de complejidad razonable que los usuarios
  ya conocen, sin llegar a la fricción de exigir símbolos especiales.
- **Sin símbolos especiales obligatorios:** los gestores de contraseñas generan
  contraseñas fuertes de todos modos; exigir símbolos solo penaliza a usuarios sin
  gestor sin mejorar significativamente la seguridad frente a ataques de diccionario
  sobre hashes bcrypt.

**Sobre el indicador:**

- Informa al usuario en tiempo real sin bloquear — puede registrarse con "Buena"
  pero ve que podría mejorarla.
- El umbral de "Fuerte" en 14 caracteres es arbitrario pero razonable: es la
  longitud a partir de la cual la mayoría de los gestores de contraseñas considera
  una contraseña robusta contra ataques offline.

---

## Consecuencias

**Positivas:**
- Contraseñas más seguras sin friccionar excesivamente el registro.
- El indicador educa al usuario sin obligarlo — mejora la postura de seguridad
  del conjunto de la plataforma a largo plazo.
- Una única fuente de verdad para la política: `PasswordDemasiadoCorto` en el dominio.

**Negativas:**
- Contraseñas existentes con 8-9 caracteres (o sin mayúscula/número) siguen siendo
  válidas — la política se aplica solo a contraseñas nuevas, no a las almacenadas.
  Esto es intencional: no se fuerza a los usuarios existentes a cambiar su contraseña.
- Los tests existentes que usen contraseñas de 8 caracteres (ej: `"apnea123"`)
  fallarán si incluyen el flujo de registro o cambio de contraseña — deben actualizarse
  a contraseñas que cumplan la nueva política (ej: `"Apnea1234!"`).

## Límites del diseño

- La política valida caracteres ASCII. Contraseñas con caracteres Unicode (emojis,
  acentos) cuentan en longitud pero no satisfacen los criterios de mayúscula/número
  si son exclusivamente Unicode.
- El indicador de fortaleza es orientativo, no prescriptivo. No impide enviar el
  formulario con una contraseña "Débil" si el usuario la corrige para cumplir la
  política mínima.
