# Sistema de Gestión de Restaurante y Reservas — Contexto e Invariantes

> **Cómo usar este documento (para humanos y asistentes):**
> Este archivo complementa los archivos `.feature` en esta carpeta. Define los
> invariantes que NO se rediscuten y la terminología de dominio que los escenarios
> citan por nombre.
> - El **Preámbulo** define restricciones de diseño inviolables. Cualquier propuesta
>   que las contradiga es inválida por defecto.
> - Las **Features** (en los archivos `.feature`) describen qué hace el sistema. Son
>   la base para tests de aceptación reales.
> - El **Apéndice** lista stack y contexto no verificable: es contexto, NO
>   comportamiento verificable del software.
>
> **Versión:** 0.1 · **Estado:** borrador · **Siguiente artefacto:** tests de aceptación

---

## Preámbulo — Invariantes del sistema (no se rediscuten)

1. **Zona horaria operativa UTC-5.** Todas las fechas y horas de negocio, auditoría,
   reservas, caja y facturación se almacenan y visualizan en UTC-5. No se admite
   ambigüedad por horario de verano.
2. **Moneda USD.** Todas las transacciones monetarias, subtotales, impuestos, montos
   de caja y reportes expresan sus valores en dólares estadounidenses con dos
   decimales.
3. **IVA del 15%.** El impuesto al valor agregado se aplica al subtotal de cada
   consumo con una tasa fija del 15%, redondeando el resultado a dos decimales.
4. **Credenciales sin texto plano.** Las contraseñas nunca se almacenan en texto
   plano; se emplea hash fuerte con salt y control de sesiones.
5. **Autorización en servidor.** Las reglas de permisos se validan en el servidor;
   la interfaz no es la única barrera de seguridad.
6. **Bitácora inmutable.** Los registros de auditoría no pueden ser modificados por
   roles operativos.
7. **Horario operativo 10:00 a 00:00.** El sistema opera en este rango diario; las
   reservas y operaciones deben respetarlo.
8. **Una apertura activa por caja/turno.** Solo puede existir una apertura de caja
   activa simultáneamente por caja y turno.

> **Nota legal embebida (no es comportamiento):** Las mesas tienen capacidades
> soportadas de 2, 4, 6 y 12 personas. La reserva exige un mínimo de 12 horas de
> anticipación. Estas reglas de negocio deben validarse con Gerencia de Operaciones.

---

## Terminología

- **Activo:** Estado de un usuario habilitado para autenticarse.
- **Suspendida:** Estado de cuenta bloqueado temporalmente por intentos fallidos
  consecutivos; dura 15 minutos.
- **Bloqueada:** Estado de cuenta bloqueado permanentemente por acumulación de 5
  fallos.
- **Disponible:** Mesa libre y lista para ser asignada.
- **Reservada:** Mesa bloqueada por una reserva confirmada.
- **Ocupada:** Mesa con clientes atendidos o en proceso de atención.
- **En Preparación:** Comanda en progreso en la cocina (KDS).
- **En Espera:** Comanda registrada en KDS pero no iniciada por la cocina.
- **Cancelada:** Comanda, reserva o factura anulada/anulada; el estado final no
  permite reversión a su estado anterior sin proceso contable.
- **Emitida:** Factura generada y registrada contablemente.
- **Anulada:** Factura anulada por el Administrador; el comprobante se conserva.
- **Cuadrada:** Caja cerrada con diferencia absoluta ≤ 2,00 USD.
- **Descuadre Pendiente:** Caja cerrada con diferencia > 2,00 USD y justificación
  registrada.
- **Enviada:** Corrección de recepción confirmada y auditada; no admite edición
  directa.
- **Pendiente de Aprobación:** Solicitud de corrección de recepción esperando
  autorización del Administrador.
- **Aprobada / Rechazada:** Estado final de una solicitud de corrección.
- **Vigentes:** Puntos de fidelización dentro del período de validez (3 meses).
- **Caducados:** Puntos que superan los 3 meses desde su acreditación.
- **Abierta:** Caja con fondo inicial registrado y operativa.
- **Cerrada:** Caja sin apertura activa.

---

## Apéndice A — Stack de referencia (contexto, no comportamiento)

| Capa | Tecnología sugerida |
|---|---|
| Autenticación | Hash fuerte con salt, sesiones controladas, PIN de un solo uso |
| Backend | API RESTful con validación de permisos en el servidor |
| Base de datos | Transaccional (ACID); bloqueo optimista/pesimista para reservas |
| Frontend web | Chrome, Edge, Firefox (dos versiones estables más recientes) |
| KDS | Interfaz en tiempo real con semáforo de tiempos |
| Reportes | Exportación a PDF y Excel (.xlsx) |
| Infraestructura | Backup diario automático; disponibilidad objetivo 99,5% mensual |

---

## Apéndice B — Puntos abiertos / a confirmar

- **P95 de rendimiento:** el objetivo de 3 segundos bajo carga normal es propuesto
  de ingeniería y debe validarse con infraestructura definitiva.
- **Disponibilidad 99,5%:** objetivo propuesto; debe acordarse con el responsable de
  operación.
- **Periodicidad de backups:** al menos diaria, con retención definida por política
  institucional por confirmar.
- **Matriz de compatibilidad de navegadores:** debe mantenerse en pruebas de
  regresión; versiones soportadas se revisan trimestralmente.