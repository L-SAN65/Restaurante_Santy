Feature: Gestión de Ficha Técnica de platillos
  # RF-13 — Gestión de Inventarios y Menú

  Como Administrador
  Quiero definir la Ficha Técnica de cada platillo
  Para que el sistema deduzca automáticamente el inventario

  Scenario: Creación de ficha técnica asocia insumos y cantidades
    Given un platillo "Arroz con pollo"
    And tres insumos registrados
    When el Administrador crea una Ficha Técnica asociando insumos y cantidades
    And guarda la ficha
    Then los insumos y cantidades quedan asociados al producto
    And la ficha está disponible para el cálculo de stock y consumo

---

Feature: Habilitación y deshabilitación automática por stock
  # RF-14 — Gestión de Inventarios y Menú

  Como sistema
  Quiero cambiar el estado del platillo según el stock disponible
  Para evitar ofrecer productos sin insumos

  Background:
    Given un platillo "Activo" con Ficha Técnica registrada

  Scenario: Deshabilitación automática por stock insuficiente
    When se registra una salida de inventario que reduce un insumo por debajo del mínimo
    Then el platillo cambia automáticamente a estado "Deshabilitado por Stock"
    And la disponibilidad se refleja en el catálogo en tiempo real

  Scenario: Reactivación automática al restituir stock
    Given un platillo "Deshabilitado por Stock"
    When se registra un ingreso que restituye todos los insumos al nivel requerido
    Then el platillo vuelve automáticamente a estado "Activo"
    And la disponibilidad se refleja en el catálogo en tiempo real

---

Feature: Registro de entrada de inventario y costo promedio
  # RF-23 — Gestión de Inventarios

  Como Jefe de Compras
  Quiero registrar recepciones de lotes con costo y caducidad
  Para incrementar el stock y recalcular el costo promedio ponderado

  Scenario: Recepción recalcula costo promedio ponderado
    Given un insumo con stock anterior de 10 kg a 2,00 USD/kg
    When se registra una recepción de 10 kg a 3,00 USD/kg
    Then el stock total es 20 kg
    And el costo promedio ponderado es 2,50 USD/kg
    And el lote y caducidad quedan registrados
    And se genera trazabilidad del movimiento

---

Feature: Solicitud de corrección de recepción confirmada
  # RF-24 — Gestión de Inventarios

  Como Jefe de Compras
  Quiero corregir recepciones confirmadas mediante solicitud de aprobación
  Para mantener la integridad de los registros

  Scenario: Edición directa de recepción confirmada bloqueada
    Given una recepción "Enviada" y auditada
    When el Jefe de Compras intenta cambiar cantidad o costo
    Then el sistema rechaza la edición directa
    And ofrece crear una solicitud de corrección en estado "Pendiente de Aprobación"

  Scenario: Aprobación de solicitud de corrección queda auditable
    Given una solicitud de corrección en estado "Pendiente de Aprobación"
    When el Administrador aprueba la corrección
    Then la solicitud pasa a estado "Aprobada"
    And la aprobación queda registrada en auditoría
