Feature: Seguridad de credenciales
  # RNF-01 — Seguridad

  Como sistema
  Quiero almacenar contraseñas con hash y salt
  Para proteger las credenciales de los usuarios

  Scenario: Las contraseñas no se almacenan en texto plano
    Given el sistema almacena credenciales de usuarios
    When se revisa el almacenamiento de credenciales
    Then no se encuentran contraseñas en texto plano
    And se emplea hash fuerte con salt

  Scenario: Acceso no autenticado es denegado
    When un usuario no autenticado intenta acceder a funcionalidades protegidas
    Then el sistema requiere autenticación
    And no expone funcionalidades protegidas

---

Feature: Autorización del lado servidor
  # RNF-02 — Seguridad

  Como sistema
  Quiero validar permisos en el servidor
  Para impedir operaciones no autorizadas

  Scenario: Invocación de operación restringida con rol sin permiso
    Given un usuario con rol "Cajero" autenticado
    When el Cajero intenta invocar directamente una operación restringida
    Then el servidor deniega la operación
    And la negación no depende de la interfaz

---

Feature: Consistencia temporal UTC-5
  # RNF-03 — Transversal

  Como sistema
  Quiero que todas las marcas temporales sigan UTC-5
  Para mantener coherencia en auditoría, reservas, caja y facturación

  Scenario: Consistencia temporal de auditoría y reservas
    Given un evento generado con fecha/hora conocida
    When se consulta la marca temporal almacenada
    Then los timestamps de negocio son consistentes con UTC-5
    And no hay ambigüedad por horario de verano

---

Feature: Rendimiento de operaciones críticas
  # RNF-04 — Rendimiento

  Como Administrador
  Quiero que operaciones críticas respondan rápido
  Para garantizar buena experiencia bajo carga normal

  Scenario: Operaciones críticas responden en P95 menor o igual a 3 segundos
    Given el ambiente estable y monitorizado
    When se ejecutan 30 ejecuciones de cada operación crítica: login, validación de PIN, confirmación de reserva y check-in
    Then el percentil 95 de cada operación es menor o igual a 3 segundos bajo carga normal

---

Feature: Concurrencia transaccional en reservas
  # RNF-05, RNF-07 — Rendimiento / Integridad

  Como sistema
  Quiero garantizar consistencia transaccional en reservas concurrentes
  Para evitar dobles confirmaciones y datos parciales

  Scenario: Concurrencia transaccional en reserva bajo carga
    Given un ambiente de prueba con concurrencia controlada
    When se lanzan 50 solicitudes concurrentes sobre varias mesas y horarios
    And 10 solicitudes sobre la misma mesa
    Then no existe doble reserva de una misma mesa y bloque horario
    And las transacciones fallidas no dejan datos parciales
    And los cambios dependientes se realizan en rollback

---

Feature: Disponibilidad del sistema
  # RNF-06 — Disponibilidad

  Como Administración
  Quiero una disponibilidad mensual mínima del 99,5%
  Para garantizar continuidad operativa

  Scenario: Monitoreo de disponibilidad mensual
    When se revisa el monitoreo mensual de disponibilidad
    Then la disponibilidad mensual es al menos 99,5%
    And los mantenimientos programados se excluyen del cálculo

---

Feature: Trazabilidad y auditoría inmutable
  # RNF-08 — Auditoría

  Como sistema
  Quiero que los eventos críticos conserven todos sus campos
  Para garantizar trazabilidad completa

  Scenario: Eventos críticos conservan usuario, fecha/hora, acción, resultado y referencia
    When se ejecuta una operación crítica
    Then la bitácora contiene usuario, fecha/hora UTC-5, acción, resultado y referencia al registro afectado
    And los registros de auditoría no son modificables por roles operativos

---

Feature: Compatibilidad del portal web
  # RNF-11 — Portal Web

  Como Cliente
  Quiero que el portal funcione en navegadores modernos
  Para reservar sin problemas técnicos

  Scenario: Flujos críticos funcionan en navegadores soportados
    Given Chrome, Edge y Firefox en versiones estables soportadas
    When se repiten los flujos críticos de reserva, consulta y cancelación
    And se prueban resoluciones móviles y de escritorio
    Then los flujos críticos funcionan sin errores funcionales en todos los navegadores y resoluciones soportadas

---

Feature: Copias de seguridad y recuperación
  # RNF-12 — Continuidad Operativa

  Como DBA
  Quiero backups automáticos y un procedimiento probado de restauración
  Para minimizar la pérdida de información

  Scenario: Restauración de copia de seguridad
    Given una copia válida y un ambiente controlado de restauración
    When se restaura el backup diario más reciente en el ambiente aislado
    And se validan las tablas y registros críticos
    And se ejecuta una consulta y un proceso de negocio de prueba
    Then la restauración es completa
    And los datos críticos son recuperables conforme al objetivo definido

---

Feature: Usabilidad y mensajes de validación
  # RNF-10 — Interfaz

  Como usuario operativo
  Quiero mensajes claros y consistentes
  Para corregir errores sin exposición de información sensible

  Scenario: Mensajes de error diferencian validación, autorización y disponibilidad
    Given un formulario con datos inválidos
    When el usuario ejecuta una operación inválida
    Then el sistema muestra un mensaje claro, consistente y orientado a la acción
    And el mensaje indica qué debe corregirse
    And no expone información sensible
