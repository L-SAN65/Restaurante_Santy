Feature: Acumulación de puntos de fidelización
  # RF-15 — Fidelización de Clientes

  Como sistema
  Quiero acreditar puntos por consumos registrados
  Para fidelizar al cliente según su gasto

  Scenario: Acreditación de puntos por consumo entero
    Given un cliente registrado con cédula
    And un saldo de puntos inicial conocido
    When se emite una factura por 12,99 USD con cédula registrada
    Then se acreditan 12 puntos al cliente
    And los puntos corresponden únicamente a la parte entera del consumo

  Scenario: No se acreditan puntos cuando la factura no tiene cédula
    Given una factura emitida sin cédula registrada
    When se finaliza el cobro
    Then no se acreditan puntos de fidelización

---

Feature: Canje de puntos por descuento
  # RF-16 — Fidelización de Clientes

  Como cliente fidelizado
  Quiero canjear puntos por descuento en la cuenta
  Para reducir el importe a pagar

  Scenario: Canje de puntos con descuento
    Given un cliente con al menos 50 puntos vigentes
    And una nueva factura en progreso
    When el cliente canjea 50 puntos
    Then se aplica un descuento de 5,00 USD al subtotal
    And se descuentan 50 puntos del saldo

  Scenario: Canje rechazado por saldo insuficiente
    Given un cliente con 5 puntos vigentes
    When el cliente intenta canjear 50 puntos
    Then el sistema deniega el canje
    And se muestra un mensaje de saldo insuficiente

---

Feature: Caducidad automática de puntos
  # RF-17 — Fidelización de Clientes

  Como sistema
  Quiero descontar puntos no utilizados al cumplirse 3 meses
  Para mantener el programa de fidelización vigente

  Scenario: Caducidad de puntos a los tres meses
    Given puntos acreditados con fecha de vencimiento alcanzada
    When se ejecuta el proceso de vencimiento
    Then los puntos caducados dejan de estar disponibles
    And el movimiento de caducidad queda registrado en el historial
    And la fecha de vencimiento se conserva como trazabilidad
