Feature: Generación de reportes de ventas y mermas
  # RF-12, RNF-09 — Reportes y Auditoría

  Como Administrador
  Quiero consultar ventas brutas y mermas por rango de fechas
  Para exportar resultados en PDF y Excel

  Scenario: Reporte de ventas y mermas exportable
    Given existen registros históricos en un rango de fechas
    And el Administrador define el rango 01/08/2026 a 14/08/2026
    When el Administrador genera el consolidado de ventas y mermas
    Then se muestran ventas brutas y mermas correctas en UTC-5
    And se puede exportar a PDF
    And se puede exportar a Excel
    And ambos formatos conservan totales y moneda en USD

  Scenario: Exportación íntegra en PDF y Excel sin pérdida de datos
    Given un reporte con subtotales y totales conocidos
    When el Administrador exporta el mismo rango a PDF y Excel
    Then ambos archivos conservan columnas y filtros aplicados
    And los totales coinciden en USD
    And no hay pérdida de estructura entre formatos
