Feature: Selección de reserva por fecha, horario, comensales y capacidad
  # RF-27, RF-29 — Portal Web de Reservas

  Como Cliente
  Quiero seleccionar mesa según comensales y horario
  Para reservar una mesa disponible

  Background:
    Given mesas disponibles en el croquis
    And un horario futuro dentro del rango 10:00 a 00:00

  Scenario: Reserva válida con 12 horas de anticipación
    Given una solicitud con 12 horas o más de anticipación
    And 4 comensales
    And un bloque de 2 horas
    When el Cliente selecciona una mesa de capacidad suficiente
    And confirma la reserva
    Then la mesa queda en estado "Reservada"
    And la reserva dura exactamente 2 horas bajo UTC-5
    And las mesas seleccionadas son excluyas

  Scenario: Reserva rechazada con menos de 12 horas de anticipación
    Given una solicitud con 11 horas de anticipación
    When el Cliente intenta confirmar la reserva
    Then el sistema rechaza la solicitud
    And no se reserva ninguna mesa

---

Feature: Bloqueo temporal estricto para concurrencia
  # RF-28, RNF-05 — Portal Web de Reservas

  Como sistema
  Quiero bloquear mesas durante 2 minutos tras una selección
  Para evitar dobles reservas concurrentes

  Scenario: Concurrencia evita doble reserva
    Given una mesa disponible para un bloque específico
    When dos Clientes solicitan la misma mesa en el mismo instante
    Then solo una solicitud obtiene el bloqueo de 2 minutos
    And la otra solicitud es rechazada
    And no existe doble reserva de la misma mesa y bloque horario
    And el bloqueo persiste aunque el navegador se cierre

---

Feature: Consulta de reservas activas
  # RF-32 — Portal Web de Reservas

  Como Cliente
  Quiero ver mis reservas activas en el portal
  Para confirmar mi agenda

  Scenario: Consulta de reservas activas del cliente
    Given un cliente autenticado con tres reservas: dos activas y una cancelada
    When el Cliente abre "Mis Reservas"
    Then se muestran únicamente las reservas activas del cliente autenticado
    And cada reserva incluye fecha, horario, mesas y estado
    And no se expone información de reservas de otros clientes

---

Feature: Cancelación autónoma de reservas
  # RF-33 — Portal Web de Reservas

  Como Cliente
  Quiero cancelar mi reserva con anticipación suficiente
  Para liberar mesas y evitar inconvenientes

  Scenario: Cancelación autónoma con cuatro horas o más de anticipación
    Given una reserva activa con 5 horas de anticipación
    When el Cliente cancela la reserva desde el portal
    Then la reserva queda en estado "Cancelada"
    And las mesas asociadas pasan inmediatamente a estado "Disponible"

  Scenario: Cancelación autónoma bloqueada con menos de cuatro horas
    Given una reserva activa con 3 horas de anticipación
    When el Cliente abre "Mis Reservas" y selecciona la reserva
    Then la opción de cancelación autónoma no está disponible
    And se muestra un aviso de contacto directo con el restaurante
