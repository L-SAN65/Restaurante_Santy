Feature: Inicio de sesión y redirección por rol
  # RF-01, RF-34 — Autenticación y Seguridad

  Como usuario con rol asignado
  Quiero ingresar con correo y contraseña
  Para acceder al panel correspondiente a mi rol

  Scenario: Login exitoso con redirección correcta por rol
    Given un usuario "Activo" con rol "Administrador" existe
    And un usuario "Activo" con rol "Mesero" existe
    When el usuario "Administrador" ingresa con credenciales válidas
    Then el sistema lo dirige al panel "Administrador"
    When el usuario "Mesero" ingresa con credenciales válidas
    Then el sistema lo dirige al panel "Mesero"
    And el sistema limita las funciones no autorizadas al "Mesero"

  Scenario: Login con usuario inactivo es rechazado
    Given un usuario con estado "Inactivo" existe
    When el usuario intenta ingresar con credenciales válidas
    Then el sistema rechaza el acceso
    And no dirige al panel correspondiente

---

Feature: Control de intentos fallidos y suspensión temporal
  # RF-02 — Autenticación y Seguridad

  Como usuario
  Quiero que mi cuenta se suspenda tras fallos consecutivos
  Para proteger mi acceso ante intentos no autorizados

  Scenario: Suspensión después de tres intentos fallidos
    Given una cuenta en estado "Activo" y sin bloqueos previos
    When el usuario falla la autenticación tres veces consecutivas
    Then la cuenta pasa a estado "Suspendida"
    And no permite autenticación durante 15 minutos
    And la suspensión queda registrada en auditoría

  Scenario: Dos intentos fallidos no suspenden la cuenta
    Given una cuenta en estado "Activo" y sin bloqueos previos
    When el usuario falla la autenticación dos veces consecutivas
    Then la cuenta permanece en estado "Activo"

---

Feature: Bloqueo permanente por fallos acumulados
  # RF-03 — Autenticación y Seguridad

  Como usuario
  Quiero que mi cuenta se bloquee permanentemente tras 5 fallos acumulados
  Para evitar accesos no autorizados tras suspensión temporal

  Scenario: Bloqueo permanente al quinto fallo acumulado
    Given una cuenta en estado "Suspendida" tras 3 fallos consecutivos
    When el usuario falla la autenticación dos veces adicionales
    And se cumplen 5 fallos acumulados
    Then la cuenta pasa a estado "Bloqueada"
    And ningún intento posterior permite autenticación

  Scenario: Acceso correcto durante suspensión no reactiva la cuenta
    Given una cuenta en estado "Suspendida"
    When el usuario ingresa credenciales correctas
    Then el sistema rechaza el acceso por suspensión
    And la cuenta no cambia de estado

---

Feature: Generación de PIN de autorización remota
  # RF-18 — Autenticación y Seguridad

  Como Administrador
  Quiero generar un PIN temporal
  Para autorizar acciones sensibles de forma remota

  Scenario: Generación de PIN temporal
    Given un Administrador autenticado
    When el Administrador genera un PIN para una acción sensible
    Then el PIN queda asociado a la acción
    And se registra la marca temporal de emisión
    And el PIN tiene una ventana de validez de 60 segundos
    And el PIN es de un solo uso

---

Feature: Validación y expiración de PIN
  # RF-19 — Autenticación y Seguridad

  Como usuario autorizado
  Quiero que el PIN caduque tras 60 segundos
  Para garantizar que las autorizaciones sensibles expiran

  Scenario: PIN válido dentro de 60 segundos autoriza la operación
    Given un PIN recién generado
    When el usuario ingresa el PIN en el segundo 30
    Then el sistema valida el PIN
    And autoriza la operación sensible

  Scenario: PIN rechazado en el segundo 61 por caducidad
    Given un PIN recién generado
    When el usuario ingresa el PIN en el segundo 61
    Then el sistema rechaza el PIN por caducidad
    And no ejecuta la operación sensible
    And el PIN queda invalidado inmediatamente

---

Feature: Autorización de funcionalidades por rol
  # RF-34, RNF-02 — Autenticación y Seguridad

  Como usuario autenticado
  Quiero que mi rol defina qué puedo hacer
  Para que no acceda a funcionalidades no autorizadas

  Scenario: Acceso no autorizado a una función restringida es denegado
    Given un usuario con rol "Cajero" autenticado
    When el Cajero intenta anular una factura
    Then el sistema deniega la operación en la interfaz
    And el sistema deniega la operación en el servidor
    And el intento queda registrado en auditoría

  Scenario: Acceso autorizado a funcionalidad permitida por rol
    Given un usuario con rol "Administrador" autenticado
    When el Administrador anula una factura "Emitida"
    Then el sistema cambia el estado a "Anulada"
    And la anulación queda registrada en auditoría

---

Feature: Registro de auditoría de operaciones críticas
  # RF-35, RNF-08 — Transversal / Auditoría

  Como sistema
  Quiero registrar operaciones críticas de forma completa
  Para garantizar trazabilidad e inmutabilidad de la bitácora

  Scenario: Bitácora de operación crítica completa
    Given un usuario autorizado
    When el usuario ejecuta una anulación de factura
    Then la bitácora registra el usuario, fecha/hora UTC-5, acción, resultado y referencia al objeto
    And la bitácora no permite edición desde un rol operativo
