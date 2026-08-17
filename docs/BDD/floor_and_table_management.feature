Feature: Gestión de mesa — no-show y liberación
  # RF-04, RF-31 — Gestión de Sala

  Como Mesero
  Quiero registrar no-shows después de la tolerancia
  Para liberar mesas reservadas que no se presentan

  Background:
    Given una reserva activa a las 18:00
    And una mesa en estado "Reservada"

  Scenario: No-show a los 16 minutos libera la mesa
    Given la hora actual es 18:16
    When el Mesero registra el no-show
    Then la acción es permitida
    And la reserva pasa a estado "Cancelada" por no-show
    And la mesa pasa a estado "Disponible"

  Scenario: No-show antes de 15 minutos es rechazado
    Given la hora actual es 18:14
    When el Mesero intenta registrar el no-show
    Then el sistema deniega la acción
    And la mesa permanece en estado "Reservada"

  Scenario: No-show desde Check-In sin exceder tolerancia no permite inasistencia
    Given la hora actual es 10 minutos después de la reserva
    When el Mesero intenta marcar no-show
    Then el sistema no permite cancelar por inasistencia
    And la reserva permanece activa

---

Feature: Registro y envío de comanda a KDS
  # RF-20 — Gestión de Sala y Cocina

  Como Mesero
  Quiero enviar comandas desde la mesa
  Para que la cocina prepare los pedidos

  Scenario: Envío de comanda cambia estados y descuenta insumos
    Given una mesa "Disponible" de capacidad 4
    And productos activos con ficha técnica registrada
    When el Mesero agrega dos productos a la mesa
    And envía la comanda
    Then la mesa cambia a estado "Ocupada"
    And la comanda cambia a estado "En Espera"
    And el stock de insumos disminuye según la Ficha Técnica

---

Feature: Cálculo de subtotal e IVA en consumo
  # RF-21 — Gestión de Sala y Cocina

  Como Mesero
  Quiero ver el total de la cuenta en tiempo real
  Para informar al cliente antes de facturar

  Scenario: Vista previa calcula subtotal, IVA y total con precisión
    Given dos productos de precios conocidos: 20,00 USD y 30,00 USD
    When el Mesero abre la vista previa de consumo
    Then el subtotal es 50,00 USD
    And el IVA es 7,50 USD
    And el total es 57,50 USD

---

Feature: Segmentación de cuenta
  # RF-22 — Gestión de Sala y Cocina

  Como Mesero
  Quiero dividir la cuenta en grupos independientes
  Para que cada comensal pague su parte

  Scenario: Segmentación de cuenta calcula IVA por fracción
    Given una cuenta con cuatro ítems
    When el Mesero divide 2 ítems al Grupo A y 2 al Grupo B
    Then cada grupo tiene sus ítems sin duplicaciones
    And cada grupo calcula su propio 15% de IVA

---

Feature: Check-In y unión de mesas
  # RF-30 — Gestión de Sala

  Como Mesero
  Quiero validar la llegada del cliente y unir mesas
  Para acomodar grupos que superan la reserva

  Scenario: Check-In con más comensales une mesas
    Given una reserva activa para 4 personas
    And mesas contiguas disponibles
    When el Mesero registra la llegada de 6 personas con cédula válida
    Then el aforo se actualiza a 6
    And se unen mesas dentro del máximo de 4
    And las mesas involucradas cambian a estado "Ocupada"
