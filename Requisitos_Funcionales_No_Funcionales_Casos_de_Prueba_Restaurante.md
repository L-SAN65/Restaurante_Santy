# Requisitos Funcionales, Requisitos No Funcionales y Casos de Prueba

**Proyecto:** Sistema de Gestión de Restaurante y Reservas
**Documento de origen:** `Especificacion_Completa_Requisitos_y_Casos_Prueba_Restaurante.xlsx`

Este documento consolida los requisitos derivados de las historias de usuario y los casos de prueba asociados.

## Resumen

- **Requisitos funcionales:** 35
- **Requisitos no funcionales:** 12
- **Casos de prueba:** 45

---

## 1. Requisitos Funcionales

### RF-01 — Inicio de sesión y redirección por rol

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-01 |
| **HU origen** | HU-01 |
| **Tipo** | Funcional |
| **Módulo** | Autenticación y Seguridad |
| **Fuente / Stakeholder** | Superadministrador / Stakeholder de Seguridad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir que un usuario en estado Activo ingrese con correo electrónico y contraseña válidos y sea dirigido al panel correspondiente a su rol.

**Criterio de verificación**

> Verificar acceso exitoso para un usuario Activo y comprobar que el panel, permisos y menú corresponden al rol autenticado.

**Notas / Restricciones**

> Roles soportados en HU-01: Administrador, Cajero, Mesero, Chef y Encargado de Bodega. Zona horaria operativa UTC-5.

---

### RF-02 — Control de intentos fallidos y suspensión temporal

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-02 |
| **HU origen** | HU-01 |
| **Tipo** | Funcional |
| **Módulo** | Autenticación y Seguridad |
| **Fuente / Stakeholder** | Superadministrador / Stakeholder de Seguridad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá contabilizar los intentos fallidos consecutivos y suspender temporalmente la cuenta durante 15 minutos al alcanzar 3 fallos.

**Criterio de verificación**

> Registrar tres autenticaciones consecutivas con credenciales inválidas y comprobar que la cuenta quede suspendida y no permita el acceso durante el periodo definido.

**Notas / Restricciones**

> La suspensión aplica sobre la cuenta afectada y debe quedar registrada en auditoría.

---

### RF-03 — Bloqueo permanente por fallos acumulados

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-03 |
| **HU origen** | HU-01 |
| **Tipo** | Funcional |
| **Módulo** | Autenticación y Seguridad |
| **Fuente / Stakeholder** | Superadministrador / Stakeholder de Seguridad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá bloquear permanentemente la cuenta cuando, después de la suspensión temporal, se acumulen 2 intentos fallidos adicionales hasta completar 5 fallos.

**Criterio de verificación**

> Comprobar que el quinto intento fallido cambie el estado de la cuenta a Bloqueada y que ningún nuevo intento permita autenticación.

**Notas / Restricciones**

> Se conserva el contador de fallos conforme a RN-02.

---

### RF-04 — Liberación de mesa por inasistencia

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-04 |
| **HU origen** | HU-02 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Sala |
| **Fuente / Stakeholder** | Gerencia de Operaciones / Jefe de Sala |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Mesero registrar un no-show únicamente cuando hayan transcurrido más de 15 minutos desde la hora reservada y liberar la mesa.

**Criterio de verificación**

> Con una mesa Reservada, verificar que a los 16 minutos la acción sea permitida y que la mesa pase a Disponible; a los 14 minutos debe ser rechazada.

**Notas / Restricciones**

> Horario operativo: 10:00 a 00:00. La tolerancia máxima es de 15 minutos.

---

### RF-05 — Semáforo de tiempos en KDS

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-05 |
| **HU origen** | HU-03 |
| **Tipo** | Funcional |
| **Módulo** | Cocina (KDS) |
| **Fuente / Stakeholder** | Jefe de Cocina / Administrador |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá clasificar visualmente cada comanda En Preparación según su tiempo: Verde si es menor de 10 minutos, Amarillo entre 10 y 20 minutos y Rojo si supera 20 minutos.

**Criterio de verificación**

> Verificar las tres categorías usando comandas con tiempos representativos en los límites y fuera de los límites.

**Notas / Restricciones**

> La clasificación debe actualizarse automáticamente con base en la hora de inicio de preparación.

---

### RF-06 — Registro auditado de mermas y reposición

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-06 |
| **HU origen** | HU-03 |
| **Tipo** | Funcional |
| **Módulo** | Cocina (KDS) |
| **Fuente / Stakeholder** | Jefe de Cocina / Administrador |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Chef cancelar un platillo por merma registrando el motivo, conservar el cargo original, crear la auditoría y generar una alerta al Mesero para reposición a costo 0,00 USD.

**Criterio de verificación**

> Registrar una merma con motivo y comprobar estado Cancelada, auditoría UTC-5, cargo original conservado y alerta de reposición sin costo.

**Notas / Restricciones**

> La auditoría debe identificar usuario, fecha/hora, ítem y motivo.

---

### RF-07 — Emisión de factura con IVA

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-07 |
| **HU origen** | HU-04 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Departamento Contable / Administrador |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá calcular subtotal, aplicar 15% de IVA, redondear a dos decimales, emitir la factura con cédula del cliente y liberar la mesa.

**Criterio de verificación**

> Procesar un pago exacto y comprobar subtotal, IVA, total, estado Emitida, cédula registrada y mesa Disponible.

**Notas / Restricciones**

> Moneda USD; tasa de IVA 15%; importes a dos decimales; zona horaria UTC-5.

---

### RF-08 — Anulación de factura autorizada

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-08 |
| **HU origen** | HU-04 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Administrador / Departamento Contable |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir únicamente al Administrador anular una factura Emitida y registrar la corrección de forma auditable.

**Criterio de verificación**

> Intentar anular con un usuario Cajero y con un Administrador; comprobar que solo el Administrador pueda cambiar el estado a Anulada.

**Notas / Restricciones**

> La anulación no elimina físicamente el comprobante.

---

### RF-09 — Cobro parcial y saldo pendiente

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-09 |
| **HU origen** | HU-04 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Cajero / Departamento Contable |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá soportar cobros parciales de una cuenta segmentada, emitir la factura parcial, liberar la mesa y asignar el saldo restante a la cédula del cliente como Pendiente de Resolución Administrativa.

**Criterio de verificación**

> Registrar un pago parcial y verificar monto facturado, saldo pendiente, estado del saldo y mesa Disponible.

**Notas / Restricciones**

> El saldo pendiente debe permanecer trazable hasta su resolución administrativa.

---

### RF-10 — Cierre ciego con tolerancia de descuadre

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-10 |
| **HU origen** | HU-05 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Auditoría Interna / Contabilidad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá ejecutar el cierre ciego sin mostrar al Cajero el saldo esperado y clasificar la caja como Cuadrada cuando la diferencia absoluta sea menor o igual a 2,00 USD.

**Criterio de verificación**

> Realizar cierre ciego con una diferencia de 2,00 USD o menor y comprobar estado Cuadrada.

**Notas / Restricciones**

> El monto físico se captura antes de revelar o calcular el resultado contable al Cajero.

---

### RF-11 — Justificación obligatoria de descuadre

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-11 |
| **HU origen** | HU-05 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Auditoría Interna / Contabilidad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá clasificar la caja como Descuadre Pendiente y exigir una justificación escrita cuando la diferencia absoluta sea de 2,01 USD o mayor.

**Criterio de verificación**

> Realizar cierre con diferencia superior a 2,00 USD y comprobar obligatoriedad de la justificación y estado final.

**Notas / Restricciones**

> No debe permitirse completar el cierre sin justificación válida.

---

### RF-12 — Generación de reportes de ventas y mermas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-12 |
| **HU origen** | HU-06 |
| **Tipo** | Funcional |
| **Módulo** | Reportes y Auditoría |
| **Fuente / Stakeholder** | Gerencia General / Dirección Financiera |
| **Prioridad** | Media |

**Descripción**

> El sistema deberá permitir al Administrador consultar por rango de fechas las ventas brutas y mermas y exportar los resultados en PDF y Excel.

**Criterio de verificación**

> Definir un rango válido, generar el consolidado y comprobar exactitud de datos, zona UTC-5 y disponibilidad de ambos formatos de exportación.

**Notas / Restricciones**

> Moneda del reporte: USD.

---

### RF-13 — Gestión de Ficha Técnica de platillos

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-13 |
| **HU origen** | HU-07 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Inventarios y Menú |
| **Fuente / Stakeholder** | Administrador / Chef Ejecutivo |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Administrador definir la Ficha Técnica de cada platillo, asociando insumos y cantidades requeridas.

**Criterio de verificación**

> Crear y actualizar una Ficha Técnica y comprobar que los insumos y cantidades queden asociados al producto.

**Notas / Restricciones**

> La Ficha Técnica es la fuente para la deducción automática de inventario.

---

### RF-14 — Habilitación y deshabilitación automática por stock

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-14 |
| **HU origen** | HU-07 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Inventarios y Menú |
| **Fuente / Stakeholder** | Administrador / Chef Ejecutivo |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá cambiar automáticamente el estado del platillo a Deshabilitado por Stock cuando algún insumo requerido sea insuficiente y volver a Activo cuando el inventario sea restituido.

**Criterio de verificación**

> Reducir un insumo por debajo del mínimo requerido y verificar deshabilitación; registrar inventario suficiente y comprobar reactivación.

**Notas / Restricciones**

> La actualización de disponibilidad debe reflejarse en el catálogo en tiempo real.

---

### RF-15 — Acumulación de puntos de fidelización

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-15 |
| **HU origen** | HU-08 |
| **Tipo** | Funcional |
| **Módulo** | Fidelización de Clientes |
| **Fuente / Stakeholder** | Marketing / Gerencia Comercial |
| **Prioridad** | Media |

**Descripción**

> Después de una factura Emitida con cédula registrada, el sistema deberá acreditar 1 punto por cada USD entero consumido.

**Criterio de verificación**

> Cobrar una factura con monto conocido y verificar que los puntos acreditados correspondan únicamente a la parte entera del consumo.

**Notas / Restricciones**

> Ejemplo: 12,99 USD generan 12 puntos.

---

### RF-16 — Canje de puntos por descuento

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-16 |
| **HU origen** | HU-08 |
| **Tipo** | Funcional |
| **Módulo** | Fidelización de Clientes |
| **Fuente / Stakeholder** | Marketing / Gerencia Comercial |
| **Prioridad** | Media |

**Descripción**

> El sistema deberá permitir canjear puntos vigentes aplicando 1,00 USD de descuento al subtotal por cada 10 puntos redimidos.

**Criterio de verificación**

> Canjear una cantidad válida de puntos y comprobar descuento y nuevo saldo de puntos.

**Notas / Restricciones**

> El canje debe validar saldo suficiente y puntos vigentes.

---

### RF-17 — Caducidad automática de puntos

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-17 |
| **HU origen** | HU-08 |
| **Tipo** | Funcional |
| **Módulo** | Fidelización de Clientes |
| **Fuente / Stakeholder** | Marketing / Gerencia Comercial |
| **Prioridad** | Media |

**Descripción**

> El sistema deberá descontar automáticamente los puntos no utilizados al cumplirse 3 meses exactos desde su acreditación.

**Criterio de verificación**

> Simular o esperar la fecha de vencimiento de una acreditación y verificar eliminación del saldo caducado.

**Notas / Restricciones**

> La fecha de vencimiento debe conservarse como parte de la trazabilidad del movimiento.

---

### RF-18 — Generación de PIN de autorización remota

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-18 |
| **HU origen** | HU-09 |
| **Tipo** | Funcional |
| **Módulo** | Autenticación y Seguridad |
| **Fuente / Stakeholder** | Seguridad Operativa / Administrador |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Administrador generar un PIN temporal para autorizar acciones sensibles.

**Criterio de verificación**

> Generar un PIN y comprobar que quede asociado a una acción, un tiempo de emisión y una ventana de validez de 60 segundos.

**Notas / Restricciones**

> El PIN debe ser de un solo uso y auditable.

---

### RF-19 — Validación y expiración de PIN

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-19 |
| **HU origen** | HU-09 |
| **Tipo** | Funcional |
| **Módulo** | Autenticación y Seguridad |
| **Fuente / Stakeholder** | Seguridad Operativa / Administrador |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá validar un PIN dentro de los primeros 60 segundos y rechazarlo automáticamente desde el segundo 61.

**Criterio de verificación**

> Ingresar un PIN antes y después del umbral de 60 segundos y comprobar autorización o rechazo de la acción sensible.

**Notas / Restricciones**

> Al expirar, el PIN debe quedar invalidado inmediatamente.

---

### RF-20 — Registro y envío de comanda a KDS

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-20 |
| **HU origen** | HU-10 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Sala y Cocina |
| **Fuente / Stakeholder** | Jefe de Sala / Operaciones |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Mesero asociar productos a una mesa disponible, enviar la comanda y cambiar la mesa a Ocupada y la comanda a En Espera.

**Criterio de verificación**

> Registrar una comanda válida, enviarla y verificar las transiciones de estado y la deducción de insumos.

**Notas / Restricciones**

> Capacidades soportadas: 2, 4, 6 y 12 personas; horario 10:00 a 00:00.

---

### RF-21 — Cálculo de subtotal e IVA en consumo

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-21 |
| **HU origen** | HU-10 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Sala y Cocina |
| **Fuente / Stakeholder** | Jefe de Sala / Operaciones |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá totalizar la vista previa de consumo calculando subtotal y 15% de IVA.

**Criterio de verificación**

> Agregar varios productos y comprobar subtotal, IVA y total con precisión de dos decimales.

**Notas / Restricciones**

> El cálculo debe ser consistente con el utilizado en facturación.

---

### RF-22 — Segmentación de cuenta

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-22 |
| **HU origen** | HU-10 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Sala y Cocina |
| **Fuente / Stakeholder** | Jefe de Sala / Operaciones |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá dividir una cuenta en grupos independientes generando fracciones cobrables con cálculo individual del 15% de IVA.

**Criterio de verificación**

> Separar una cuenta en dos o más grupos y verificar que cada fracción tenga sus propios ítems, subtotal, IVA y total.

**Notas / Restricciones**

> Los ítems no deben duplicarse ni perderse durante la segmentación.

---

### RF-23 — Registro de entrada de inventario y costo promedio

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-23 |
| **HU origen** | HU-11 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Inventarios |
| **Fuente / Stakeholder** | Jefe de Compras / Bodega |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá registrar cantidades, costos unitarios y caducidad de lotes recibidos, incrementar stock y recalcular el Costo Promedio Ponderado en USD.

**Criterio de verificación**

> Registrar una recepción y comprobar existencia, lote, caducidad y nuevo costo promedio ponderado.

**Notas / Restricciones**

> La recepción confirmada debe generar trazabilidad del movimiento.

---

### RF-24 — Solicitud de corrección de recepción confirmada

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-24 |
| **HU origen** | HU-11 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Inventarios |
| **Fuente / Stakeholder** | Jefe de Compras / Bodega |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá impedir la edición directa de una recepción confirmada y obligar a crear una solicitud de corrección pendiente de aprobación del Administrador.

**Criterio de verificación**

> Intentar editar un registro confirmado y comprobar bloqueo; crear solicitud y comprobar estado Pendiente hasta aprobación.

**Notas / Restricciones**

> La aprobación o rechazo debe quedar auditada.

---

### RF-25 — Apertura de caja con fondo inicial

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-25 |
| **HU origen** | HU-12 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Contabilidad / Cajas |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá abrir la caja cuando el fondo inicial sea mayor a 0,00 USD y registrar la fecha y hora en UTC-5.

**Criterio de verificación**

> Con caja Cerrada, ingresar un fondo válido y comprobar estado Abierta y marca temporal.

**Notas / Restricciones**

> Solo debe existir una apertura activa por turno/caja.

---

### RF-26 — Rechazo de apertura con fondo cero

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-26 |
| **HU origen** | HU-12 |
| **Tipo** | Funcional |
| **Módulo** | Facturación y Caja |
| **Fuente / Stakeholder** | Contabilidad / Cajas |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá rechazar la apertura de caja con fondo inicial igual a 0,00 USD y mantener bloqueadas las funciones de cobro.

**Criterio de verificación**

> Intentar abrir caja con 0,00 USD y verificar rechazo, caja Cerrada y cobros bloqueados.

**Notas / Restricciones**

> El mensaje debe indicar la condición que impide la apertura sin exponer información sensible.

---

### RF-27 — Selección de reserva por fecha, horario, comensales y capacidad

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-27 |
| **HU origen** | HU-13 |
| **Tipo** | Funcional |
| **Módulo** | Portal Web de Reservas |
| **Fuente / Stakeholder** | Marketing / Experiencia del Cliente |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Cliente seleccionar fecha, bloque de 2 horas, número de comensales y mesas cuya capacidad cubra la demanda.

**Criterio de verificación**

> Consultar el croquis y seleccionar una combinación de mesas con capacidad suficiente para la cantidad indicada.

**Notas / Restricciones**

> La reserva requiere mínimo 12 horas de anticipación y exclusividad de las mesas seleccionadas.

---

### RF-28 — Bloqueo temporal estricto para concurrencia

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-28 |
| **HU origen** | HU-13 |
| **Tipo** | Funcional |
| **Módulo** | Portal Web de Reservas |
| **Fuente / Stakeholder** | Marketing / Experiencia del Cliente |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá aplicar un bloqueo de 2 minutos sobre las mesas seleccionadas para evitar que dos solicitudes concurrentes confirmen la misma disponibilidad.

**Criterio de verificación**

> Ejecutar dos solicitudes simultáneas sobre la misma mesa y comprobar que solo una conserve el bloqueo y pueda continuar.

**Notas / Restricciones**

> El bloqueo debe persistir aunque el navegador se cierre y no debe permitir doble reserva.

---

### RF-29 — Confirmación de reserva de 2 horas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-29 |
| **HU origen** | HU-13 |
| **Tipo** | Funcional |
| **Módulo** | Portal Web de Reservas |
| **Fuente / Stakeholder** | Marketing / Experiencia del Cliente |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá confirmar una reserva válida, marcar las mesas como Reservada y asignar un bloque de duración exacta de 2 horas bajo UTC-5.

**Criterio de verificación**

> Confirmar una reserva dentro de las condiciones y verificar hora inicio, hora fin, estado Reservada y UTC-5.

**Notas / Restricciones**

> Solicitudes con menos de 12 horas de anticipación deben ser rechazadas.

---

### RF-30 — Check-In y excepción de unión de mesas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-30 |
| **HU origen** | HU-14 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Sala |
| **Fuente / Stakeholder** | Jefe de Sala / Operaciones |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá permitir al Mesero validar la llegada mediante cédula, actualizar el aforo y unir hasta 4 mesas continuas cuando el número real de comensales exceda la reserva.

**Criterio de verificación**

> Registrar una llegada con aforo superior y verificar actualización de personas y unión dentro del máximo permitido.

**Notas / Restricciones**

> Las mesas involucradas deben quedar Ocupadas al completar el check-in.

---

### RF-31 — No-show desde Check-In

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-31 |
| **HU origen** | HU-14 |
| **Tipo** | Funcional |
| **Módulo** | Gestión de Sala |
| **Fuente / Stakeholder** | Jefe de Sala / Operaciones |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá registrar como no-show una reserva que exceda 15 minutos sin llegada, cancelarla por inasistencia y liberar la mesa.

**Criterio de verificación**

> Esperar más de 15 minutos y registrar la inasistencia; comprobar estado de reserva Cancelada por no-show y mesa Disponible.

**Notas / Restricciones**

> Debe compartir la misma regla de tolerancia de HU-02.

---

### RF-32 — Consulta de reservas activas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-32 |
| **HU origen** | HU-15 |
| **Tipo** | Funcional |
| **Módulo** | Portal Web de Reservas |
| **Fuente / Stakeholder** | Experiencia del Cliente / Producto |
| **Prioridad** | Media |

**Descripción**

> El sistema deberá mostrar al Cliente sus reservas activas con fecha, horario, mesas y estado.

**Criterio de verificación**

> Consultar el portal con reservas activas y verificar que solo se muestren registros vigentes del cliente autenticado.

**Notas / Restricciones**

> No debe exponerse información de reservas pertenecientes a otros clientes.

---

### RF-33 — Cancelación autónoma de reservas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-33 |
| **HU origen** | HU-15 |
| **Tipo** | Funcional |
| **Módulo** | Portal Web de Reservas |
| **Fuente / Stakeholder** | Experiencia del Cliente / Producto |
| **Prioridad** | Media |

**Descripción**

> El sistema deberá permitir cancelar una reserva desde el portal cuando falten 4 horas o más y liberar inmediatamente las mesas asociadas.

**Criterio de verificación**

> Cancelar una reserva con anticipación suficiente y verificar estado Cancelada y mesas Disponibles; intentar cancelar con menos de 4 horas y comprobar bloqueo de la opción.

**Notas / Restricciones**

> Menos de 4 horas requiere gestión directa con el restaurante.

---

### RF-34 — Autorización de funcionalidades por rol

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-34 |
| **HU origen** | HU-01 |
| **Tipo** | Funcional |
| **Módulo** | Autenticación y Seguridad |
| **Fuente / Stakeholder** | Superadministrador / Stakeholder de Seguridad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá restringir cada funcionalidad según el rol autenticado y negar acciones no autorizadas.

**Criterio de verificación**

> Iniciar sesión con diferentes roles e intentar acceder a módulos permitidos y no permitidos.

**Notas / Restricciones**

> La autorización debe validarse en servidor y no depender solo de la interfaz.

---

### RF-35 — Registro de auditoría de operaciones críticas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RF-35 |
| **HU origen** | HU-01, HU-03, HU-04, HU-05, HU-09, HU-11 |
| **Tipo** | Funcional |
| **Módulo** | Transversal / Auditoría |
| **Fuente / Stakeholder** | Administración / Auditoría Interna |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El sistema deberá registrar en una bitácora las operaciones críticas de autenticación, anulaciones, mermas, cierres, autorizaciones PIN y correcciones de inventario.

**Criterio de verificación**

> Ejecutar una operación crítica y comprobar existencia de un registro con usuario, fecha/hora UTC-5, acción, resultado y referencia al objeto afectado.

**Notas / Restricciones**

> La bitácora debe ser inmutable para perfiles operativos.

---

## 2. Requisitos No Funcionales

### RNF-01 — Seguridad de credenciales

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-01 |
| **HU origen** | HU-01 |
| **Tipo** | No funcional |
| **Módulo** | Seguridad |
| **Fuente / Stakeholder** | Superadministrador |
| **Prioridad** | Alta / Esencial |

**Descripción**

> Las contraseñas no deberán almacenarse en texto plano y el acceso deberá requerir autenticación antes de exponer funcionalidades protegidas.

**Criterio de verificación**

> Revisar almacenamiento de credenciales y ejecutar pruebas de acceso no autenticado.

**Notas / Restricciones**

> Se recomienda hash fuerte con salt de contraseñas y control de sesiones.

---

### RNF-02 — Autorización del lado servidor

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-02 |
| **HU origen** | HU-01, HU-04, HU-05, HU-09, HU-11 |
| **Tipo** | No funcional |
| **Módulo** | Seguridad |
| **Fuente / Stakeholder** | Superadministrador / Auditoría |
| **Prioridad** | Alta / Esencial |

**Descripción**

> Las reglas de permisos deberán validarse en servidor para impedir que un usuario modifique o invoque directamente operaciones no permitidas.

**Criterio de verificación**

> Intentar invocar endpoints/operaciones restringidas con un rol sin permiso y comprobar respuesta de denegación.

**Notas / Restricciones**

> Aplica a Cajero, Mesero, Chef, Bodega y Administrador.

---

### RNF-03 — Consistencia temporal UTC-5

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-03 |
| **HU origen** | HU-01, HU-03, HU-04, HU-06, HU-09, HU-12, HU-13 |
| **Tipo** | No funcional |
| **Módulo** | Transversal |
| **Fuente / Stakeholder** | Auditoría / Contabilidad |
| **Prioridad** | Alta / Esencial |

**Descripción**

> Las fechas y horas de negocio deberán almacenarse y visualizarse de forma consistente con la zona horaria operativa UTC-5.

**Criterio de verificación**

> Comparar marcas temporales de auditoría, reservas, caja y facturación con una referencia UTC-5.

**Notas / Restricciones**

> Debe evitarse ambigüedad por horario de verano.

---

### RNF-04 — Rendimiento de operaciones críticas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-04 |
| **HU origen** | HU-01, HU-09, HU-13, HU-14 |
| **Tipo** | No funcional |
| **Módulo** | Rendimiento |
| **Fuente / Stakeholder** | Administración |
| **Prioridad** | Alta |

**Descripción**

> Las operaciones de inicio de sesión, validación de PIN y confirmación/check-in de reserva deberán responder en un tiempo objetivo de hasta 3 segundos bajo carga normal.

**Criterio de verificación**

> Medir 30 ejecuciones representativas y comprobar que el percentil 95 no supere 3 segundos.

**Notas / Restricciones**

> Objetivo propuesto de ingeniería; debe validarse con infraestructura definitiva.

---

### RNF-05 — Concurrencia en reservas

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-05 |
| **HU origen** | HU-13 |
| **Tipo** | No funcional |
| **Módulo** | Rendimiento / Integridad |
| **Fuente / Stakeholder** | Marketing / Operaciones |
| **Prioridad** | Alta / Esencial |

**Descripción**

> El módulo de reservas deberá garantizar consistencia transaccional ante solicitudes concurrentes sin permitir doble confirmación de una misma mesa y bloque horario.

**Criterio de verificación**

> Ejecutar múltiples solicitudes concurrentes y verificar que solo una transacción confirme cada disponibilidad.

**Notas / Restricciones**

> Debe existir protección transaccional en base de datos.

---

### RNF-06 — Disponibilidad del sistema

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-06 |
| **HU origen** | Transversal |
| **Tipo** | No funcional |
| **Módulo** | Disponibilidad |
| **Fuente / Stakeholder** | Administración |
| **Prioridad** | Alta |

**Descripción**

> El sistema deberá mantener una disponibilidad objetivo mensual mínima de 99,5%, excluyendo mantenimientos programados.

**Criterio de verificación**

> Revisar monitoreo mensual y reportes de disponibilidad.

**Notas / Restricciones**

> El objetivo es propuesto y debe acordarse con el responsable de operación.

---

### RNF-07 — Integridad transaccional

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-07 |
| **HU origen** | HU-04, HU-07, HU-08, HU-10, HU-11, HU-13 |
| **Tipo** | No funcional |
| **Módulo** | Integridad de Datos |
| **Fuente / Stakeholder** | Arquitectura / DBA |
| **Prioridad** | Alta / Esencial |

**Descripción**

> Las operaciones críticas deberán confirmarse de forma atómica para evitar saldos, stocks, reservas o estados parcialmente actualizados.

**Criterio de verificación**

> Provocar una falla durante una transacción y verificar rollback de los cambios dependientes.

**Notas / Restricciones**

> Especialmente aplicable a reservas, cobros y deducción de inventario.

---

### RNF-08 — Trazabilidad y auditoría

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-08 |
| **HU origen** | HU-03, HU-04, HU-05, HU-09, HU-11, HU-13, HU-14 |
| **Tipo** | No funcional |
| **Módulo** | Auditoría |
| **Fuente / Stakeholder** | Administración / Auditoría |
| **Prioridad** | Alta / Esencial |

**Descripción**

> Los eventos críticos deberán conservar usuario, fecha/hora, acción, resultado y referencia del registro afectado.

**Criterio de verificación**

> Ejecutar operaciones auditables y comprobar integridad y completitud de la bitácora.

**Notas / Restricciones**

> Los registros de auditoría no deben ser modificables por roles operativos.

---

### RNF-09 — Exportación interoperable

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-09 |
| **HU origen** | HU-06 |
| **Tipo** | No funcional |
| **Módulo** | Reportes |
| **Fuente / Stakeholder** | Gerencia General / Dirección Financiera |
| **Prioridad** | Media |

**Descripción**

> Los reportes deberán exportarse en PDF y Excel (.xlsx) sin pérdida de columnas, totales ni filtros aplicados.

**Criterio de verificación**

> Exportar el mismo rango a ambos formatos y comparar totales y estructura.

**Notas / Restricciones**

> Moneda: USD.

---

### RNF-10 — Usabilidad y mensajes de validación

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-10 |
| **HU origen** | HU-01, HU-02, HU-04, HU-05, HU-09, HU-12, HU-13, HU-15 |
| **Tipo** | No funcional |
| **Módulo** | Interfaz |
| **Fuente / Stakeholder** | Usuarios Operativos / Cliente |
| **Prioridad** | Media |

**Descripción**

> La interfaz deberá presentar mensajes claros, consistentes y orientados a la acción, diferenciando errores de validación, autorización y disponibilidad.

**Criterio de verificación**

> Ejecutar escenarios inválidos y verificar que los mensajes indiquen qué debe corregirse sin exponer información sensible.

**Notas / Restricciones**

> Se recomienda mantener terminología de estados consistente con el modelo de negocio.

---

### RNF-11 — Compatibilidad del portal web

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-11 |
| **HU origen** | HU-13, HU-15 |
| **Tipo** | No funcional |
| **Módulo** | Portal Web |
| **Fuente / Stakeholder** | Cliente / Producto |
| **Prioridad** | Media |

**Descripción**

> El portal de reservas deberá funcionar en las dos versiones estables más recientes de Chrome, Edge y Firefox en resolución de escritorio y móvil.

**Criterio de verificación**

> Ejecutar el conjunto crítico de reserva, consulta y cancelación en los navegadores soportados.

**Notas / Restricciones**

> La matriz de compatibilidad debe mantenerse en pruebas de regresión.

---

### RNF-12 — Copias de seguridad y recuperación

| Campo | Detalle |
|---|---|
| **Número de requisito** | RNF-12 |
| **HU origen** | Transversal |
| **Tipo** | No funcional |
| **Módulo** | Continuidad Operativa |
| **Fuente / Stakeholder** | Administración / DBA |
| **Prioridad** | Alta |

**Descripción**

> La base de datos deberá contar con copias de seguridad automáticas y un procedimiento probado de restauración para minimizar pérdida de información.

**Criterio de verificación**

> Revisar ejecución de respaldos y realizar una restauración de prueba en ambiente controlado.

**Notas / Restricciones**

> Periodicidad propuesta: al menos diaria, con retención definida por política institucional.

---

## 3. Casos de Prueba

### CP-01 — Login exitoso con redirección correcta por rol

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-01 |
| **Requisito relacionado** | RF-01, RF-34 |
| **HU relacionada** | HU-01 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Existe un usuario Activo con rol Administrador y otro con rol Mesero.

**Datos de entrada**

> Escenario A: credenciales válidas del Administrador. Escenario B: credenciales válidas del Mesero.

**Pasos de ejecución**

- 1. Abrir inicio de sesión.
- 2. Ingresar credenciales del Escenario A.
- 3. Seleccionar Ingresar.
- 4. Verificar panel y permisos.
- 5. Cerrar sesión y repetir con Escenario B.

**Resultado esperado**

> Escenario A dirige al panel Administrador. Escenario B dirige al panel Mesero y limita las funciones no autorizadas.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-02 — Suspensión después de tres intentos fallidos

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-02 |
| **Requisito relacionado** | RF-02 |
| **HU relacionada** | HU-01 |
| **Tipo de prueba** | Seguridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> Cuenta Activa y sin bloqueos previos.

**Datos de entrada**

> Contraseña incorrecta en tres intentos consecutivos.

**Pasos de ejecución**

- 1. Abrir inicio de sesión.
- 2. Ingresar correo válido y contraseña incorrecta.
- 3. Repetir dos veces más.
- 4. Intentar ingresar nuevamente.

**Resultado esperado**

> Después del tercer fallo la cuenta queda suspendida 15 minutos y no permite autenticación.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-03 — Bloqueo permanente al quinto fallo acumulado

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-03 |
| **Requisito relacionado** | RF-03 |
| **HU relacionada** | HU-01 |
| **Tipo de prueba** | Seguridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> Cuenta suspendida por haber alcanzado tres fallos consecutivos.

**Datos de entrada**

> Dos nuevas contraseñas incorrectas después de la suspensión.

**Pasos de ejecución**

- 1. Intentar acceder con la cuenta tras finalizar o gestionar la suspensión.
- 2. Ejecutar dos fallos adicionales.
- 3. Intentar autenticación con la contraseña correcta.

**Resultado esperado**

> Al completar cinco fallos acumulados la cuenta queda Bloqueada y no permite acceso.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-04 — No-show a los 16 minutos libera la mesa

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-04 |
| **Requisito relacionado** | RF-04, RF-31 |
| **HU relacionada** | HU-02, HU-14 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Reserva activa a las 18:00 y mesa en estado Reservada.

**Datos de entrada**

> Hora actual 18:16; registrar inasistencia.

**Pasos de ejecución**

- 1. Consultar reserva.
- 2. Intentar no-show.
- 3. Confirmar acción.
- 4. Consultar estado de mesa y reserva.

**Resultado esperado**

> La acción es permitida; reserva pasa a cancelada por no-show y mesa a Disponible.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-05 — No-show antes de 15 minutos es rechazado

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-05 |
| **Requisito relacionado** | RF-04 |
| **HU relacionada** | HU-02 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Reserva activa a las 18:00.

**Datos de entrada**

> Hora actual 18:14.

**Pasos de ejecución**

- 1. Consultar reserva.
- 2. Intentar registrar inasistencia.
- 3. Observar respuesta.

**Resultado esperado**

> El sistema deniega la acción y mantiene la mesa Reservada.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-06 — Semáforo KDS por tiempo de preparación

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-06 |
| **Requisito relacionado** | RF-05 |
| **HU relacionada** | HU-03 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Tres comandas en estado En Preparación.

**Datos de entrada**

> Tiempos de 9:59, 10:00 y 20:01 minutos.

**Pasos de ejecución**

- 1. Abrir KDS.
- 2. Consultar las tres comandas.
- 3. Verificar clasificación visual.

**Resultado esperado**

> 9:59 se muestra Verde; 10:00 Amarillo; 20:01 Rojo.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-07 — Merma auditada con reposición a costo cero

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-07 |
| **Requisito relacionado** | RF-06 |
| **HU relacionada** | HU-03 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Existe un platillo En Preparación con cargo vigente.

**Datos de entrada**

> Motivo de merma: producto quemado.

**Pasos de ejecución**

- 1. Seleccionar ítem.
- 2. Registrar cancelación por merma y motivo.
- 3. Confirmar.
- 4. Revisar auditoría y alerta al Mesero.

**Resultado esperado**

> Ítem Cancelada, cargo original conservado, auditoría creada y alerta de reposición a $0,00.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-08 — Factura emitida con IVA del 15%

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-08 |
| **Requisito relacionado** | RF-07 |
| **HU relacionada** | HU-04 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Comanda cerrada y cliente con cédula registrada.

**Datos de entrada**

> Subtotal: 100,00 USD; pago exacto 115,00 USD.

**Pasos de ejecución**

- 1. Abrir cobro.
- 2. Verificar subtotal e IVA.
- 3. Registrar pago.
- 4. Emitir factura.
- 5. Consultar mesa.

**Resultado esperado**

> IVA 15,00; total 115,00; factura Emitida; mesa Disponible y cédula asociada.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-09 — Anulación restringida al Administrador

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-09 |
| **Requisito relacionado** | RF-08 |
| **HU relacionada** | HU-04 |
| **Tipo de prueba** | Seguridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> Factura Emitida.

**Datos de entrada**

> Intento 1 con Cajero. Intento 2 con Administrador.

**Pasos de ejecución**

- 1. Ingresar como Cajero e intentar anular.
- 2. Ingresar como Administrador e intentar anular.

**Resultado esperado**

> Cajero recibe denegación. Administrador puede cambiar el estado a Anulada y queda registro de auditoría.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-10 — Cobro parcial libera mesa y conserva saldo

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-10 |
| **Requisito relacionado** | RF-09 |
| **HU relacionada** | HU-04 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Cuenta segmentada de 120,00 USD.

**Datos de entrada**

> Pago parcial: 70,00 USD; cédula del cliente registrada.

**Pasos de ejecución**

- 1. Seleccionar segmento.
- 2. Registrar pago parcial.
- 3. Emitir comprobante.
- 4. Consultar mesa y saldo.

**Resultado esperado**

> Se emite factura parcial, mesa Disponible y saldo 50,00 asociado como Pendiente de Resolución Administrativa.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-11 — Cierre ciego dentro de tolerancia

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-11 |
| **Requisito relacionado** | RF-10 |
| **HU relacionada** | HU-05 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Caja Abierta y saldo esperado de 500,00 USD no visible al Cajero.

**Datos de entrada**

> Efectivo declarado 498,50 USD.

**Pasos de ejecución**

- 1. Iniciar cierre ciego.
- 2. Registrar 498,50.
- 3. Confirmar cierre.
- 4. Consultar estado.

**Resultado esperado**

> Diferencia 1,50 <= 2,00; caja queda Cuadrada sin mostrar previamente el saldo esperado.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-12 — Cierre con descuadre exige justificación

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-12 |
| **Requisito relacionado** | RF-11 |
| **HU relacionada** | HU-05 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Caja Abierta.

**Datos de entrada**

> Efectivo declarado produce diferencia de 2,01 USD.

**Pasos de ejecución**

- 1. Iniciar cierre ciego.
- 2. Registrar monto físico.
- 3. Intentar confirmar sin justificación.
- 4. Registrar justificación.
- 5. Confirmar.

**Resultado esperado**

> Sin justificación el cierre no concluye. Con justificación válida la caja queda Descuadre Pendiente.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-13 — Reporte de ventas y mermas exportable

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-13 |
| **Requisito relacionado** | RF-12, RNF-09 |
| **HU relacionada** | HU-06 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Existen registros históricos en un rango de fechas.

**Datos de entrada**

> Rango: 01/08/2026 a 14/08/2026.

**Pasos de ejecución**

- 1. Abrir reportes.
- 2. Seleccionar rango.
- 3. Generar consolidado.
- 4. Exportar PDF.
- 5. Exportar Excel.
- 6. Comparar totales.

**Resultado esperado**

> Se muestran ventas brutas y mermas correctas en UTC-5; ambos archivos se generan sin pérdida de datos.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-14 — Creación de ficha técnica

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-14 |
| **Requisito relacionado** | RF-13 |
| **HU relacionada** | HU-07 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Existe un platillo y tres insumos registrados.

**Datos de entrada**

> Platillo: Arroz con pollo; insumos con cantidades definidas.

**Pasos de ejecución**

- 1. Abrir catálogo.
- 2. Crear ficha técnica.
- 3. Asociar insumos y cantidades.
- 4. Guardar.
- 5. Consultar ficha.

**Resultado esperado**

> La ficha queda guardada y lista para cálculo de stock y consumo.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-15 — Deshabilitación automática por stock insuficiente

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-15 |
| **Requisito relacionado** | RF-14 |
| **HU relacionada** | HU-07 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Platillo Activo y ficha técnica registrada.

**Datos de entrada**

> Reducir un insumo requerido por debajo de su cantidad mínima.

**Pasos de ejecución**

- 1. Registrar salida de inventario.
- 2. Actualizar existencias.
- 3. Consultar catálogo.

**Resultado esperado**

> El platillo cambia automáticamente a Deshabilitado por Stock.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-16 — Reactivación automática al restituir stock

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-16 |
| **Requisito relacionado** | RF-14 |
| **HU relacionada** | HU-07 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Platillo Deshabilitado por Stock.

**Datos de entrada**

> Ingreso que devuelve todos los insumos al nivel requerido.

**Pasos de ejecución**

- 1. Registrar ingreso.
- 2. Confirmar existencias.
- 3. Consultar catálogo.

**Resultado esperado**

> El platillo vuelve automáticamente a Activo.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-17 — Acreditación de puntos por consumo entero

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-17 |
| **Requisito relacionado** | RF-15 |
| **HU relacionada** | HU-08 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Cliente registrado con cédula y saldo de puntos inicial conocido.

**Datos de entrada**

> Factura Emitida por 12,99 USD.

**Pasos de ejecución**

- 1. Finalizar cobro.
- 2. Consultar historial de puntos.
- 3. Verificar acreditación.

**Resultado esperado**

> Se acreditan 12 puntos.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-18 — Canje de puntos con descuento

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-18 |
| **Requisito relacionado** | RF-16 |
| **HU relacionada** | HU-08 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Cliente con al menos 50 puntos vigentes.

**Datos de entrada**

> Canje de 50 puntos en una nueva factura.

**Pasos de ejecución**

- 1. Iniciar nueva factura.
- 2. Solicitar canje de 50 puntos.
- 3. Confirmar operación.
- 4. Revisar subtotal y saldo.

**Resultado esperado**

> Se aplica 5,00 USD de descuento al subtotal y se descuentan 50 puntos.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-19 — Caducidad de puntos a los tres meses

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-19 |
| **Requisito relacionado** | RF-17 |
| **HU relacionada** | HU-08 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Existen puntos acreditados con fecha de vencimiento alcanzada.

**Datos de entrada**

> Acreditación con antigüedad exacta de 3 meses.

**Pasos de ejecución**

- 1. Ejecutar proceso de vencimiento.
- 2. Consultar saldo.
- 3. Revisar historial.

**Resultado esperado**

> Los puntos caducados dejan de estar disponibles y el movimiento queda trazado.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-20 — Generación de PIN temporal

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-20 |
| **Requisito relacionado** | RF-18 |
| **HU relacionada** | HU-09 |
| **Tipo de prueba** | Seguridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> Administrador autenticado.

**Datos de entrada**

> Solicitud de autorización para una operación sensible.

**Pasos de ejecución**

- 1. Abrir generación de PIN.
- 2. Crear PIN.
- 3. Consultar metadatos.

**Resultado esperado**

> PIN generado, asociado a acción y marca temporal, con vigencia de 60 segundos.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-21 — PIN válido dentro de 60 segundos

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-21 |
| **Requisito relacionado** | RF-19 |
| **HU relacionada** | HU-09 |
| **Tipo de prueba** | Seguridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> PIN recién generado.

**Datos de entrada**

> Ingreso del PIN en el segundo 30.

**Pasos de ejecución**

- 1. Solicitar PIN.
- 2. Introducirlo antes del segundo 60.
- 3. Confirmar acción.

**Resultado esperado**

> El sistema valida el PIN y autoriza la operación sensible.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-22 — PIN rechazado en el segundo 61

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-22 |
| **Requisito relacionado** | RF-19 |
| **HU relacionada** | HU-09 |
| **Tipo de prueba** | Seguridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> PIN recién generado.

**Datos de entrada**

> Ingreso del mismo PIN en el segundo 61.

**Pasos de ejecución**

- 1. Generar PIN.
- 2. Esperar 61 segundos.
- 3. Introducir PIN.
- 4. Confirmar acción.

**Resultado esperado**

> El sistema rechaza el PIN por caducidad y no ejecuta la operación.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-23 — Envío de comanda cambia estados y descuenta insumos

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-23 |
| **Requisito relacionado** | RF-20 |
| **HU relacionada** | HU-10 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Mesa Disponible de capacidad 4 y productos activos.

**Datos de entrada**

> Dos productos de la ficha técnica.

**Pasos de ejecución**

- 1. Seleccionar mesa.
- 2. Agregar productos.
- 3. Enviar comanda.
- 4. Consultar mesa, comanda e inventario.

**Resultado esperado**

> Mesa Ocupada, comanda En Espera y stock disminuido según Ficha Técnica.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-24 — Cálculo de subtotal e IVA en vista previa

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-24 |
| **Requisito relacionado** | RF-21 |
| **HU relacionada** | HU-10 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Productos con precios conocidos.

**Datos de entrada**

> Dos productos por 20,00 y 30,00 USD.

**Pasos de ejecución**

- 1. Agregar productos.
- 2. Abrir vista previa.
- 3. Verificar subtotal, IVA y total.

**Resultado esperado**

> Subtotal 50,00; IVA 7,50; total 57,50 USD.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-25 — Segmentación de cuenta calcula IVA por fracción

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-25 |
| **Requisito relacionado** | RF-22 |
| **HU relacionada** | HU-10 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Cuenta con cuatro ítems.

**Datos de entrada**

> Dividir 2 ítems al Grupo A y 2 al Grupo B.

**Pasos de ejecución**

- 1. Abrir segmentación.
- 2. Crear dos grupos.
- 3. Asignar ítems.
- 4. Calcular totales.

**Resultado esperado**

> Cada grupo tiene sus ítems sin duplicaciones y calcula su propio 15% de IVA.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-26 — Recepción recalcula costo promedio ponderado

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-26 |
| **Requisito relacionado** | RF-23 |
| **HU relacionada** | HU-11 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Insumo con stock y costo promedio existentes.

**Datos de entrada**

> Stock anterior: 10 kg a 2,00; recepción: 10 kg a 3,00.

**Pasos de ejecución**

- 1. Registrar recepción.
- 2. Confirmar lote y caducidad.
- 3. Consultar stock y costo promedio.

**Resultado esperado**

> Stock total 20 kg y costo promedio ponderado 2,50 USD/kg.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-27 — Edición directa de recepción confirmada bloqueada

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-27 |
| **Requisito relacionado** | RF-24 |
| **HU relacionada** | HU-11 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Recepción confirmada y auditada.

**Datos de entrada**

> Intento de cambiar cantidad o costo.

**Pasos de ejecución**

- 1. Abrir recepción confirmada.
- 2. Intentar editar.
- 3. Revisar opciones disponibles.

**Resultado esperado**

> La edición directa es rechazada y el sistema ofrece crear una solicitud de corrección.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-28 — Apertura de caja con fondo inicial válido

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-28 |
| **Requisito relacionado** | RF-25 |
| **HU relacionada** | HU-12 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Caja en estado Cerrada.

**Datos de entrada**

> Fondo inicial 100,00 USD.

**Pasos de ejecución**

- 1. Abrir módulo de caja.
- 2. Registrar fondo.
- 3. Confirmar apertura.
- 4. Consultar estado y hora.

**Resultado esperado**

> Caja Abierta, fondo registrado y marca temporal UTC-5 almacenada.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-29 — Apertura de caja con cero es rechazada

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-29 |
| **Requisito relacionado** | RF-26 |
| **HU relacionada** | HU-12 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Caja en estado Cerrada.

**Datos de entrada**

> Fondo inicial 0,00 USD.

**Pasos de ejecución**

- 1. Abrir módulo de caja.
- 2. Ingresar 0,00.
- 3. Intentar confirmar.

**Resultado esperado**

> La apertura es rechazada; caja permanece Cerrada y no se habilitan cobros.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-30 — Reserva válida con 12 horas de anticipación

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-30 |
| **Requisito relacionado** | RF-27, RF-29 |
| **HU relacionada** | HU-13 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Mesas disponibles y horario futuro.

**Datos de entrada**

> Reserva con 12 horas o más de anticipación, 4 comensales, bloque de 2 horas.

**Pasos de ejecución**

- 1. Abrir portal.
- 2. Seleccionar fecha y bloque.
- 3. Indicar 4 comensales.
- 4. Seleccionar mesa de capacidad suficiente.
- 5. Confirmar.

**Resultado esperado**

> La mesa queda Reservada durante el bloque de 2 horas bajo UTC-5.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-31 — Reserva rechazada con menos de 12 horas

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-31 |
| **Requisito relacionado** | RF-27, RF-29 |
| **HU relacionada** | HU-13 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Horario de reserva disponible pero con poca anticipación.

**Datos de entrada**

> Reserva para dentro de 11 horas.

**Pasos de ejecución**

- 1. Abrir portal.
- 2. Seleccionar fecha/bloque.
- 3. Intentar confirmar.

**Resultado esperado**

> El sistema rechaza la solicitud por no cumplir la anticipación mínima.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-32 — Concurrencia evita doble reserva

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-32 |
| **Requisito relacionado** | RF-28 |
| **HU relacionada** | HU-13 |
| **Tipo de prueba** | Integridad / Funcional |
| **Prioridad** | Alta |

**Precondición**

> Una misma mesa está disponible para un bloque específico.

**Datos de entrada**

> Dos clientes solicitan la misma mesa en el mismo instante.

**Pasos de ejecución**

- 1. Iniciar dos solicitudes concurrentes.
- 2. Seleccionar misma mesa y horario.
- 3. Confirmar ambas.

**Resultado esperado**

> Solo una solicitud obtiene el bloqueo/confirmación; la otra es rechazada sin doble reserva.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-33 — Check-In con más comensales une mesas

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-33 |
| **Requisito relacionado** | RF-30 |
| **HU relacionada** | HU-14 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Reserva activa para 4 personas y mesas contiguas disponibles.

**Datos de entrada**

> Llegada real: 6 personas; cédula válida.

**Pasos de ejecución**

- 1. Consultar reserva.
- 2. Ingresar cédula.
- 3. Actualizar aforo.
- 4. Seleccionar mesas contiguas necesarias.
- 5. Confirmar check-in.

**Resultado esperado**

> Aforo actualizado, mesas unidas dentro del máximo de 4 y mesas Ocupadas.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-34 — Check-In sin exceder tolerancia no permite no-show

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-34 |
| **Requisito relacionado** | RF-31 |
| **HU relacionada** | HU-14 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Alta |

**Precondición**

> Reserva activa y llegada dentro de 15 minutos.

**Datos de entrada**

> Hora actual 10 minutos después de la reserva.

**Pasos de ejecución**

- 1. Consultar reserva.
- 2. Intentar marcar no-show.

**Resultado esperado**

> El sistema no permite cancelar por inasistencia y conserva la reserva activa.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-35 — Consulta de reservas activas del cliente

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-35 |
| **Requisito relacionado** | RF-32 |
| **HU relacionada** | HU-15 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Cliente autenticado con tres reservas, dos activas y una cancelada.

**Datos de entrada**

> Consulta de reservas.

**Pasos de ejecución**

- 1. Ingresar al portal.
- 2. Abrir Mis Reservas.
- 3. Revisar resultados.

**Resultado esperado**

> Se muestran únicamente las reservas activas del cliente autenticado con sus datos principales.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-36 — Cancelación autónoma con cuatro horas o más

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-36 |
| **Requisito relacionado** | RF-33 |
| **HU relacionada** | HU-15 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Reserva activa para una hora futura y con 5 horas de anticipación.

**Datos de entrada**

> Solicitud de cancelación.

**Pasos de ejecución**

- 1. Abrir Mis Reservas.
- 2. Seleccionar reserva.
- 3. Cancelar.
- 4. Consultar estado de reserva y mesas.

**Resultado esperado**

> La reserva queda Cancelada y sus mesas pasan inmediatamente a Disponible.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-37 — Cancelación autónoma bloqueada con menos de cuatro horas

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-37 |
| **Requisito relacionado** | RF-33 |
| **HU relacionada** | HU-15 |
| **Tipo de prueba** | Funcional |
| **Prioridad** | Media |

**Precondición**

> Reserva activa con 3 horas de anticipación.

**Datos de entrada**

> Solicitud de cancelación.

**Pasos de ejecución**

- 1. Abrir Mis Reservas.
- 2. Seleccionar reserva.
- 3. Revisar opciones.

**Resultado esperado**

> La opción de cancelación autónoma no está disponible y se muestra aviso de contacto directo con el restaurante.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-38 — Bitácora de operación crítica completa

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-38 |
| **Requisito relacionado** | RF-35, RNF-08 |
| **HU relacionada** | HU-03, HU-04, HU-05, HU-09, HU-11 |
| **Tipo de prueba** | Auditoría |
| **Prioridad** | Alta |

**Precondición**

> Usuario autorizado y operación crítica disponible.

**Datos de entrada**

> Ejecutar una anulación, merma, cierre o autorización PIN.

**Pasos de ejecución**

- 1. Ejecutar operación crítica.
- 2. Consultar auditoría.
- 3. Verificar usuario, fecha/hora, acción, resultado y referencia.

**Resultado esperado**

> La bitácora contiene todos los campos requeridos y no permite edición desde un rol operativo.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-39 — Acceso no autorizado a una función restringida

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-39 |
| **Requisito relacionado** | RF-34, RNF-02 |
| **HU relacionada** | HU-01, HU-04, HU-09, HU-11 |
| **Tipo de prueba** | Seguridad |
| **Prioridad** | Alta |

**Precondición**

> Usuario autenticado con rol sin permiso para una operación.

**Datos de entrada**

> Ejemplo: Cajero intenta anular factura.

**Pasos de ejecución**

- 1. Iniciar sesión con el rol restringido.
- 2. Navegar o invocar la operación.
- 3. Ejecutar solicitud.

**Resultado esperado**

> El sistema deniega la operación tanto en la interfaz como en el servidor y registra el intento según política de auditoría.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-40 — Consistencia temporal de auditoría y reservas

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-40 |
| **Requisito relacionado** | RNF-03 |
| **HU relacionada** | HU-03, HU-09, HU-13 |
| **Tipo de prueba** | No funcional |
| **Prioridad** | Alta |

**Precondición**

> Acceso a registros de auditoría y reservas.

**Datos de entrada**

> Evento generado con fecha/hora conocida.

**Pasos de ejecución**

- 1. Ejecutar una reserva o generar un PIN.
- 2. Consultar fecha/hora almacenada.
- 3. Comparar con UTC-5 de referencia.

**Resultado esperado**

> Los timestamps de negocio son consistentes con UTC-5.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-41 — Concurrencia transaccional en reserva bajo carga

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-41 |
| **Requisito relacionado** | RNF-05, RNF-07 |
| **HU relacionada** | HU-13 |
| **Tipo de prueba** | No funcional / Rendimiento |
| **Prioridad** | Alta |

**Precondición**

> Ambiente de prueba con concurrencia controlada.

**Datos de entrada**

> 50 solicitudes concurrentes sobre varias mesas y horarios; 10 sobre la misma mesa.

**Pasos de ejecución**

- 1. Lanzar carga concurrente.
- 2. Registrar resultados.
- 3. Verificar reservas confirmadas.
- 4. Revisar consistencia de estados.

**Resultado esperado**

> No existe doble reserva de una misma mesa/bloque y las transacciones fallidas no dejan datos parciales.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-42 — Rendimiento de operaciones críticas

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-42 |
| **Requisito relacionado** | RNF-04 |
| **HU relacionada** | HU-01, HU-09, HU-13, HU-14 |
| **Tipo de prueba** | No funcional / Rendimiento |
| **Prioridad** | Alta |

**Precondición**

> Ambiente estable y monitorizado.

**Datos de entrada**

> 30 ejecuciones por operación crítica.

**Pasos de ejecución**

- 1. Ejecutar login, validación PIN, confirmación de reserva y check-in.
- 2. Medir tiempos.
- 3. Calcular percentil 95.

**Resultado esperado**

> El P95 de cada operación es menor o igual a 3 segundos bajo carga normal.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-43 — Exportación íntegra en PDF y Excel

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-43 |
| **Requisito relacionado** | RNF-09 |
| **HU relacionada** | HU-06 |
| **Tipo de prueba** | No funcional |
| **Prioridad** | Media |

**Precondición**

> Reporte con subtotales y totales conocidos.

**Datos de entrada**

> Mismo rango y filtros para ambos formatos.

**Pasos de ejecución**

- 1. Generar reporte.
- 2. Exportar PDF.
- 3. Exportar Excel.
- 4. Comparar estructura y totales.

**Resultado esperado**

> Ambos archivos conservan columnas, filtros y totales; los valores en USD coinciden.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-44 — Compatibilidad del portal en navegadores soportados

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-44 |
| **Requisito relacionado** | RNF-11 |
| **HU relacionada** | HU-13, HU-15 |
| **Tipo de prueba** | Compatibilidad |
| **Prioridad** | Media |

**Precondición**

> Chrome, Edge y Firefox en versiones estables soportadas.

**Datos de entrada**

> Escenarios críticos de reserva, consulta y cancelación.

**Pasos de ejecución**

- 1. Repetir flujo en cada navegador.
- 2. Probar resolución móvil y escritorio.
- 3. Registrar incidencias.

**Resultado esperado**

> Los flujos críticos funcionan sin errores funcionales en todos los navegadores y resoluciones soportadas.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---

### CP-45 — Restauración de copia de seguridad

| Campo | Detalle |
|---|---|
| **ID caso de prueba** | CP-45 |
| **Requisito relacionado** | RNF-12 |
| **HU relacionada** | Transversal |
| **Tipo de prueba** | Continuidad / No funcional |
| **Prioridad** | Alta |

**Precondición**

> Existe una copia válida y ambiente controlado de restauración.

**Datos de entrada**

> Backup diario más reciente.

**Pasos de ejecución**

- 1. Restaurar copia en ambiente aislado.
- 2. Validar tablas y registros críticos.
- 3. Ejecutar consulta y proceso de negocio de prueba.

**Resultado esperado**

> La restauración es completa y los datos críticos son recuperables conforme al objetivo definido.

**Resultado obtenido**

> —

**Estado:** Pendiente

**Observaciones**

> —

---
