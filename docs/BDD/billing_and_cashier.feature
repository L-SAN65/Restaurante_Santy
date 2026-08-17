Feature: Emisión de factura con IVA
  # RF-07 — Facturación y Caja

  Como Cajero
  Quiero emitir facturas con cálculo correcto de IVA
  Para cobrar al cliente y liberar la mesa

  Scenario: Factura emitida con IVA del 15%
    Given una comanda cerrada
    And un cliente con cédula registrada
    And un subtotal de 100,00 USD
    When el Cajero registra un pago exacto de 115,00 USD
    Then el IVA calculado es 15,00 USD
    And el total es 115,00 USD
    And la factura pasa a estado "Emitida"
    And la cédula del cliente queda registrada
    And la mesa cambia a estado "Disponible"

---

Feature: Anulación de factura autorizada
  # RF-08 — Facturación y Caja

  Como Administrador
  Quiero anular facturas emitidas
  Para corregir errores sin eliminar el comprobante

  Scenario: Anulación restringida al Administrador
    Given una factura en estado "Emitida"
    When un Cajero intenta anular la factura
    Then el sistema deniega la operación al Cajero
    When un Administrador anula la factura
    Then el estado cambia a "Anulada"
    And la anulación queda registrada en auditoría
    And el comprobante no se elimina físicamente

---

Feature: Cobro parcial y saldo pendiente
  # RF-09 — Facturación y Caja

  Como Cajero
  Quiero registrar pagos parciales de cuentas segmentadas
  Para permitir el pago fraccionado y rastrear saldos pendientes

  Scenario: Cobro parcial libera mesa y conserva saldo
    Given una cuenta segmentada de 120,00 USD
    And el cliente con cédula registrada
    When el Cajero registra un pago parcial de 70,00 USD
    Then se emite la factura parcial
    And la mesa cambia a estado "Disponible"
    And el saldo pendiente de 50,00 USD se asigna a la cédula del cliente como "Pendiente de Resolución Administrativa"

---

Feature: Cierre ciego con tolerancia de descuadre
  # RF-10 — Facturación y Caja

  Como Cajero
  Quiero cerrar la caja sin ver el saldo esperado
  Para evitar manipulación de montos

  Scenario: Cierre ciego dentro de tolerancia
    Given una caja "Abierta" con saldo esperado no visible al Cajero
    When el Cajero realiza el cierre ciego declarando 498,50 USD
    Then la diferencia absoluta es 1,50 USD
    And la diferencia es menor o igual a 2,00 USD
    And la caja queda en estado "Cuadrada"
    And el saldo esperado no se reveló al Cajero antes del cálculo

---

Feature: Justificación obligatoria de descuadre
  # RF-11 — Facturación y Caja

  Como Cajero
  Quiero que el cierre exija justificación cuando hay descuadre
  Para mantener el control de diferencias significativas

  Scenario: Cierre con descuadre exige justificación
    Given una caja "Abierta"
    When el Cajero realiza el cierre ciego declarando un monto con diferencia de 2,01 USD
    And intenta confirmar sin justificación
    Then el sistema no permite completar el cierre
    When el Cajero registra una justificación válida
    Then la caja queda en estado "Descuadre Pendiente"

---

Feature: Apertura de caja con fondo inicial
  # RF-25 — Facturación y Caja

  Como Cajero
  Quiero abrir la caja registrando un fondo inicial
  Para iniciar el turno de cobros

  Scenario: Apertura de caja con fondo inicial válido
    Given una caja en estado "Cerrada"
    When el Cajero registra un fondo inicial de 100,00 USD
    Then la caja cambia a estado "Abierta"
    And el fondo se registra con marca temporal UTC-5
    And existe una única apertura activa para el turno/caja

  Scenario: Apertura de caja con cero es rechazada
    Given una caja en estado "Cerrada"
    When el Cajero intenta abrir con 0,00 USD
    Then el sistema rechaza la apertura
    And la caja permanece en estado "Cerrada"
    And no se habilitan funciones de cobro
    And el mensaje indica la condición sin exponer información sensible
