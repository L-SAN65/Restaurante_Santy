Feature: Semáforo de tiempos en KDS
  # RF-05 — Cocina (KDS)

  Como Jefe de Cocina
  Quiero que el KDS clasifique comandas por tiempo de preparación
  Para identificar órdenes críticas de forma visual

  Scenario: Comanda con menos de 10 minutos se muestra Verde
    Given una comanda "En Preparación" con 9:59 minutos acumulados
    When el Jefe de Cocina observa el KDS
    Then la comanda se muestra con color "Verde"

  Scenario: Comanda con 10 minutos exactos se muestra Amarillo
    Given una comanda "En Preparación" con 10:00 minutos acumulados
    When el Jefe de Cocina observa el KDS
    Then la comanda se muestra con color "Amarillo"

  Scenario: Comanda con más de 20 minutos se muestra Rojo
    Given una comanda "En Preparación" con 20:01 minutos acumulados
    When el Jefe de Cocina observa el KDS
    Then la comanda se muestra con color "Rojo"

  Scenario: El semáforo se actualiza automáticamente con el tiempo
    Given una comanda "En Preparación" con 9:30 minutos acumulados
    When transcurren 30 segundos
    Then la clasificación se actualiza según el tiempo transcurrido

---

Feature: Registro auditado de mermas y reposición
  # RF-06 — Cocina (KDS)

  Como Chef
  Quiero cancelar platillos por merma con auditoría y notificar al Mesero
  Para reponer el producto a costo cero

  Scenario: Merma auditada con reposición a costo cero
    Given un platillo "En Preparación" con cargo vigente
    When el Chef registra una cancelación por merma con motivo "producto quemado"
    Then el ítem cambia a estado "Cancelada"
    And el cargo original se conserva
    And se crea una auditoría UTC-5 identificando usuario, ítem y motivo
    And se genera una alerta al Mesero para reposición a 0,00 USD
