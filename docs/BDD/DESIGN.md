# DESIGN.md — Sistema de Gestión de Restaurante y Reservas

> **Prompt maestro para Stitch (stitch.withgoogle.com)**
> Pega este contenido en la descripción de tu proyecto Stitch y genera cada pantalla
> siguiendo el orden de las secciones. Usa los *Screen IDs* como nombres de pantalla.

---

## 1. Visión general del proyecto

**Nombre del sistema:** Sistema de Gestión de Restaurante y Reservas ("Santy POS")
**Tipo:** Aplicación web responsive para gestión restaurantera (POS + KDS + Reservas + Inventario + Fidelización)
**Usuarios:** 5 roles — Administrador, Cajero, Mesero, Chef, Encargado de Bodega — más Cliente (portal web de reservas)

**Flujo principal:**
1. Login → redirección al dashboard según rol
2. Mesero: ver mapa de sala, tomar órdenes, enviar a cocina, cobrar, cerrar mesa
3. Chef: ver KDS con semáforo de tiempos, gestionar mermas
4. Cajero: abrir caja, facturar, cobrar parcial/full, cerrar caja ciega
5. Admin: reportes, inventario, usuarios, auditoría, ajustes
6. Cliente: portal web para reservar, consultar y cancelar

**Restricciones clave (del BDD):**
- Zona horaria UTC-5 en todas las pantallas
- Moneda USD con 2 decimales
- IVA del 15%
- Horario operativo: 10:00 a 00:00
- Capacidades de mesa: 2, 4, 6 y 12 personas
- Mínimo 12 horas de anticipación para reservas
- Bloqueo de 2 minutos para evitar dobles reservas
- Tolerancia de no-show: 15 minutos
- Tolerancia de cierre ciego: ±2,00 USD
- PIN de autorización: 60 segundos, un solo uso
- Puntos de fidelización: 1 punto por cada USD entero; caduca a los 3 meses; canje 10 pts = 1 USD

---

## 2. Sistema de diseño

### Paleta de colores

| Uso | Color | Hex |
|---|---|---|
| Primario (acción) | Verde | `#22C55E` |
| Secundario (advertencia) | Amarillo | `#FACC15` |
| Error/alerta | Rojo | `#EF4444` |
| Información/éxito suave | Azul | `#3B82F6` |
| Neutro fondo | Gris muy claro | `#F8FAFC` |
| Neutro superficie | Blanco | `#FFFFFF` |
| Neutro texto primario | Gris oscuro | `#1E293B` |
| Neutro texto secundario | Gris medio | `#94A3B8` |
| Reservada | Azul suave | `#60A5FA` |
| Ocupada | Naranja | `#F59E0B` |
| Disponible | Verde claro | `#BBF7D0` |
| Estado inactivo | Gris claro | `#E2E8F0` |
| Scrim overlay | Negro translúcido | `rgba(0, 0, 0, 0.4)` |

### Semáforo KDS (tiempos de preparación)

| Rango de tiempo | Color | Hex |
|---|---|---|
| < 10 minutos | Verde | `#22C55E` |
| 10–20 minutos | Amarillo | `#FACC15` |
| > 20 minutos | Rojo | `#EF4444` |

### Estados de mesa

| Estado | Color | Hex |
|---|---|---|
| Disponible | Verde claro | `#BBF7D0` |
| Reservada | Azul suave | `#60A5FA` |
| Ocupada | Naranja | `#F59E0B` |
| Bloqueada (2 min) | Rojo translúcido | `rgba(239, 68, 68, 0.3)` |

### Tipografía

- **Fuente principal:** Inter (o system-ui)
- **Jerarquía:** Display 48-64px / H1 32-36px / H2 24-28px / H3 20px / Body 16px / Small 14px / Caption 12px
- **Números:** Monospace para montos (ej. `font-family: tabular-nums`)
- **Tracking:** Negativo para display (-0.02em), 0 para body

### Componentes base

- **Botones:** Altura 40px, padding horizontal 16px, border-radius 8px
- **Inputs:** Altura 40px, border 1px, focus ring verde
- **Tables:** Header gris claro, hover gris muy claro
- **Badets:** Border-radius completo, padding 4px 12px
- **Cards:** Shadow sutil, border-radius 12px
- **Modales:** Scrim overlay, entrada con fade + scale

---

## 3. Roles y permisos

| Rol | Acceso a módulos |
|---|---|
| Administrador | Todo: Dashboard, KDS, Facturación, Caja, Inventario, Reportes, Usuarios, Auditoría |
| Cajero | Facturación, Caja, Consulta de órdenes |
| Mesero | Sala, Órdenes, Facturación (cobro), Check-in |
| Chef | KDS, Mermas |
| Encargado de Bodega | Inventario, Recepciones |
| Cliente | Portal web de reservas (separado) |

---

## 4. Pantallas — Prompt maestro para Stitch

### SCREEN: login

**Nombre:** Login
**Prompt para Stitch:**
> Diseña una pantalla de login limpia para un sistema POS de restaurante. Centra el formulario verticalmente en una página con fondo degradado cálido (#22C55E → #166534). El formulario tiene: un logo circular "Santy" arriba, título "Bienvenido", dos inputs (Email y Contraseña con icono de ojo para toggle), botón "Ingresar" verde ancho (#22C55E, hover #16A34A), y debajo un texto "¿Olvidó su contraseña?". Usa Inter font, inputs con border-radius 8px, transición suave. Mostrar feedback de error rojo (#EF4444) si las credenciales son inválidas.

---

### SCREEN: admin_dashboard

**Nombre:** Panel de Administrador
**Prompt para Stitch:**
> Diseña un dashboard para el rol Administrador de un sistema POS de restaurante. Layout de 3 columnas con sidebar fijo izquierdo (iconos: Dashboard, Sala, Cocina, Facturación, Caja, Inventario, Reportes, Usuarios, Auditoría, Cerrar sesión). Main content: 4 tarjetas métrica en grid (Ventas del día $4,280.00, Pedidos activos 12, Stock bajo 3, Mesas ocupadas 8) con íconos y tendencias. Debajo una tabla de órdenes recientes con columnas: Mesa, Ítems, Estado (badge colorido: Verde=Listo, Amarillo=En espera, Naranja=Preparando), Total. Footer con indicador de zona horaria UTC-5.

---

### SCREEN: waiter_floor_plan

**Nombre:** Gestión de Sala — Mapa de mesas
**Prompt para Stitch:**
> Diseña la pantalla principal del Mesero: un "floor plan" interactivo de un restaurante. Sidebar izquierdo con título "Sala" y botones "Nueva Comanda" y "Mis Mesas". Main area: un croquis SVG con mesas redondas etiquetadas por número y capacidad (4, 6, 12 personas). Cada mesa es un círculo con color de estado: verde claro (Disponible), azul (Reservada), naranja (Ocupada), rojo translúcido (Bloqueada). Al hacer hover, muestra tooltip con: número, capacidad, estado, comensales esperados. En la parte inferior un timeline de reservas del día. Botón flotante verde "Tomar Orden" en bottom-right.

---

### SCREEN: waiter_order_creation

**Nombre:** Crear orden desde mesa
**Prompt para Stitch:**
> Diseña la pantalla de creación de órden: un split-view con menú de productos a la izquierda y orden en curso a la derecha. Menú: grid de cards de platillos con foto, nombre, precio, badge de disponibilidad (Verde=Activo, gris=Deshabilitado por Stock). Botones + para agregar ítems al carrito. Área de orden: lista de ítems con nombre, cantidad (stepper), precio unitario, subtotal, botón eliminar. Al footer: subtotal, IVA (15%), total en negrita. Botón "Enviar a Cocina" verde ancho y "Dividir cuenta" secundario. Al enviar, animación de "deslizar" la orden hacia el KDS.

---

### SCREEN: waiter_account_segmentation

**Nombre:** Segmentar cuenta
**Prompt para Stitch:**
> Diseña la pantalla de segmentación de cuenta ("dividir cuenta"). Parte superior: selector de mesa y lista de ítems pendientes. Layout principal: botones "Crear Grupo A" y "Crear Grupo B" verdes. Área de ítems: cada ítem es draggable (cursorGrab) y se puede arrastrar a grupo A o B. Grupos aparecen como cards con nombre editable, lista de ítems (badge con nombre + precio), subtotal, IVA 15% y total calculados por grupo. Footer: "Cobrar" verde si todos los ítems están asignados, "Cancelar" gris. No se pueden duplicar ítems entre grupos. Mensaje de error si un ítem queda sin asignar.

---

### SCREEN: waiter_checkin

**Nombre:** Check-in y unión de mesas
**Prompt para Stitch:**
> Diseña la pantalla de check-in para el Mesero. Layout de 2 columnas: izquierda un formulario (input de cédula de cliente con validación en tiempo real, input de comensales con stepper), derecha un croquis minimo de mesas contiguas con checkboxes para seleccionar mesas a unir (máximo 4). Botón "Confirmar Check-in" verde. Al confirmar: animación de mesas cambiando a color naranja (Ocupada) y aforo actualizado. Si comensales > capacidad: muestra sugerencia automática de mesas adicionales contiguas. Mensaje de error si se exceden 4 mesas.

---

### SCREEN: kds_main

**Nombre:** Kitchen Display System
**Prompt para Stitch:**
> Diseña la pantalla KDS (Kitchen Display System) para el Chef. Fondo negro (#111827) para contraste. Cards horizontales de comandas en columna vertical. Cada card tiene: número de mesa (badge naranja), lista de ítems con check circle (tachado si completado), tiempo acumulado (fuente grande, monospace, color según semáforo: #22C55E <10min, #FACC15 10-20min, #EF4444 >20min). El tiempo se actualiza en tiempo real. Al completar ítem: click en checkbox, ítem se tacha con animación. Botón rojo "Cancelar por Merma" con icono de advertencia. Footer: contador total de comandas, notificación de merma pendiente (badge rojo).

---

### SCREEN: kds_shrinkage

**Nombre:** Registro de merma y reposición
**Prompt para Stitch:**
> Dónde el Chef registra una merma: modal emergente desde el KDS (botón rojo "Cancelar por Merma"). Formulario con: textarea "Motivo de merma" (requerido, placeholder: "ej: producto quemado, vencido..."), checkbox "Notificar al Mesero para reposición". Al confirmar: ítem cambia a estado "Cancelada", banner verde "Merma registrada, auditoría UTC-5 creada", notificación al Mesero para reposición a $0.00 USD. La auditoría conserva usuario, fecha/hora, ítem y motivo. Botón "Cancelar" gris.

---

### SCREEN: cashier_billing

**Nombre:** Facturación y cobro
**Prompt para Stitch:**
> Diseña la pantalla de facturación para el Cajero. Layout de 3 columnas: izquierda lista de ítems de la comanda (nombre, cantidad, precio, subtotal), centro cálculo de totales (subtotal, IVA 15%, total con fuente grande monospace), derecha formulario de pago. Formulario: input de cédula (validación cédula), radio buttons "Pago completo" / "Pago parcial", input de monto recibido, botón "Confirmar pago" verde. Mensajes: si pago parcial, muestra saldo pendiente en rojo con texto "Pendiente de Resolución Administrativa". Al confirmar: factura en estado "Emitida", mesa pasa a "Disponible", print de ticket. Botón "Anular" rojo solo visible para Administrador.

---

### SCREEN: cashier_cash_closing

**Nombre:** Cierre y apertura de caja
**Prompt para Stitch:**
> Diseña la pantalla de manejo de caja. Tabs superiores: "Abrir Caja" y "Cerrar Caja".
>
> **Abrir Caja:** formulario con input "Fondo inicial (USD)" (validación > 0.00), botón "Abrir" verde. Si se ingresa 0.00: error rojo "El fondo inicial debe ser mayor a 0,00 USD", caja permanece "Cerrada", cobros bloqueados. Al abrir: estado "Abierta", marca temporal UTC-5, banner verde de confirmación.
>
> **Cierre Ciego:** input "Efectivo contado (USD)", NO muestra saldo esperado. Al calcular: si diferencia ≤ 2,00 → "Cuadrada" (badge verde). Si diferencia > 2,00 → "Descuadre Pendiente", obliga textarea "Justificación" (requerido), botón "Confirmar" deshabilitado hasta llenar. Estado final según justificación.

---

### SCREEN: inventory_dashboard

**Nombre:** Gestión de inventario
**Prompt para Stitch:**
> Diseña el dashboard de Inventario (accesible por Admin y Encargado de Bodega). Sidebar con sub-tabs: "Fichas Técnicas", "Stock Actual", "Recepciones", "Solicitudes de Corrección". Tab "Stock Actual": tabla con columnas (Producto, Stock actual, Stock mínimo [badge rojo si bajo mínimo], Costo promedio USD, Última entrada). Color de fila rojo si deshabilitado por stock. Botón "Nueva Recepción" verde. Notificación banner rojo si algún insumo está bajo mínimo.

---

### SCREEN: inventory_technical_sheet

**Nombre:** Ficha técnica de platillo
**Prompt para Stitch:**
> Diseña la pantalla de creación/edición de Ficha Técnica. Card con: dropdown "Seleccionar platillo" (autocomplete), tabla de insumos asociados (columnas: insumo, cantidad requerida, unidad, costo unitario, subtotal). Botón "+ Agregar insumo" que abre un modal con buscador de insumos y input de cantidad. Footer: "Guardar Ficha" verde (deshabilitado si no hay insumos). Al guardar: banner verde "Ficha técnica creada". La ficha se usa para cálculo automático de stock al enviar órdenes.

---

### SCREEN: inventory_receipt

**Nombre:** Recepción de inventario
**Prompt para Stitch:**
> Diseña la pantalla de registro de recepción de inventario. Formulario con: dropdown "Insumo", date picker "Lote y caducidad", number input "Cantidad" (kg, unidades), number input "Costo unitario (USD)", checkbox "Confirmado". Al confirmar: stock aumenta, costo promedio ponderado se recalcula (mostrar cálculo en tooltip), banner verde "Recepción registrada, trazabilidad creada". Si el insumo tiene platillos asociados que pasan de "Deshabilitado" a "Activo": animación de badge verde. Botón "Crear solicitud de corrección" visible solo para recepciones confirmadas.

---

### SCREEN: inventory_correction_request

**Nombre:** Solicitud de corrección de recepción
**Prompt para Stitch:**
> Modal o página para gestionar solicitudes de corrección. Lista de solicitudes con: ID, insumo, diferencia solicitada, estado (Pendiente de Aprobación = amarillo, Aprobada = verde, Rechazada = rojo), fecha. Botón "Aprobar" verde y "Rechazar" rojo solo para Administrador. Al aprobar: cambio de estado en tiempo real, auditoría registrada. Al rechazar: se mantiene la recepción original.

---

### SCREEN: reservation_portal_public

**Nombre:** Portal web de reservas (cliente)
**Prompt para Stitch:**
> Diseña el **portal web público** de reservas para clientes. Diseño limpio, moderno, mobile-first. Layout: hero section con fondo de restaurante acogedor, título grande "Reserva tu mesa en Santy", subtítulo "Horario: 10:00 - 00:00". Debajo un card de formulario de 3 pasos:
> 1. **Fecha y hora:** date picker + time selector (bloques de 2 horas). Mensaje de error si < 12 horas de anticipación: "Mínimo 12 horas de anticipación".
> 2. **Comensales y mesa:** selector de número de personas (2, 4, 6, 12), muestra croquis de mesas con capacidad suficiente resaltadas en verde. Botón "Seleccionar" que aplica bloqueo de 2 minutos.
> 3. **Confirmación:** resumen con fecha, hora, mesa asignada, cédula (input). Checkbox "Términos y condiciones". Botón "Confirmar Reserva" verde.
> Al confirmar: pantalla de éxito con código QR, marca temporal UTC-5, botones "Agregar a Google Calendar", "Ver mi reserva", "Cancelar".
> Footer: links "Mis Reservas", "Política de cancelación" (menos de 4 horas requiere contacto directo).

---

### SCREEN: reservation_portal_my_reservations

**Nombre:** Mis reservas (cliente)
**Prompt para Stitch:**
> Détalle en el portal web cliente: botón "Mis Reservas" muestra una lista de tarjetas. Solo reservas activas (estado "Reservada"). Cada tarjeta: fecha, horario (2 horas), mesa(s), estado (badge azul "Reservada" o verde "Completada"), botón "Cancelar" (solo visible si faltan ≥ 4 horas, de lo contrario texto "Contactar al restaurante"). Reservas pasadas o canceladas aparecen en sección separada "Historial" en gris. No se muestran reservas de otros clientes.

---

### SCREEN: reports_sales

**Nombre:** Reportes de ventas y mermas
**Prompt para Stitch:**
> Diseña la pantalla de reportes (Admin). Panel con: date range picker (default rango del día), botones "Ventas brutas" y "Mermas" (toggle). Tabla de resultados con filas por fecha: ventas, IVA, totales, mermas. Botones de exportación: "Exportar PDF" (icono 📄) y "Exportar Excel" (icono 📊) verdes. Al exportar: ambos formatos conservan columnas, filtros y totales en USD. Banner de info: "Todos los datos en UTC-5, moneda USD".

---

### SCREEN: audit_trail

**Nombre:** Bitácora de auditoría
**Prompt para Stitch:**
> Diseña la pantalla de auditoría (Admin). Tabla con columnas: Fecha/Hora (UTC-5), Usuario, Acción (login, anulación, merma, cierre, PIN, corrección inventario), Resultado (éxito/fallo), Objeto afectado (factura, mesa, insumo...). Filtros: rango de fechas, tipo de acción, usuario. Banner rojo "Bitácora inmutable — no se permite edición desde roles operativos". Exportar a PDF/Excel.

---

### SCREEN: pin_authorization

**Nombre:** PIN de autorización remota
**Prompt para Stitch:**
> Modal de autorización con PIN. Prompt: "Generar PIN de autorización". Muestra: código PIN en caja grande (6 dígitos, monospace), countdown timer de 60 segundos (badge rojo cuando < 10s), botón "Copiar". Estados: "Vigente" (verde) → "Expirado" (rojo) al segundo 61. Un solo uso: al consumir, el PIN se invalida inmediatamente y aparece en auditoría.

---

## 5. Flujos de usuario clave

### Flujo A: Mesero toma orden y cobra
1. Login → Dashboard Mesero → selecciona mesa del floor plan → "Crear Orden"
2. Agrega ítems → "Vista previa" (subtotal, IVA, total) → "Enviar a Cocina"
3. Mesa → "Ocupada", comanda → "En Espera" en KDS
4. Al terminar → "Cobrar" → Facturación (cédula, pago) → mesa → "Disponible"

### Flujo B: Cierre ciego de caja
1. Cajero abre "Cerrar Caja" → ingresa efectivo contado (no ve saldo esperado)
2. Sistema calcula diferencia → si ≤ 2,00 USD → "Cuadrada" (verde)
3. Si > 2,00 USD → exige justificación → "Descuadre Pendiente" (amarillo)

### Flujo C: Reserva web con concurrencia
1. Cliente abre portal → fecha, comensales → selecciona mesa
2. Sistema aplica bloqueo de 2 minutos
3. Otro cliente intenta misma mesa → recibe "no disponible"
4. Primero confirma → mesa "Reservada" 2 horas UTC-5

### Flujo D: Merma en cocina
1. Chef cancela ítem → ingresa motivo → item → "Cancelada"
2. Cargo original conservado, auditoría creada
3. Notificación al Mesero → reposición a $0.00

---

## 6. Requisitos no visuales (del BDD)

- **Real-time:** KDS autoupdate de semáforo, estados de mesa en vivo
- **Responsive:** Portal web funciona en Chrome, Edge, Firefox (desktop + mobile)
- **Animaciones:** Entrada/salida de modals (fade + scale), mesas cambiando de color (transición spring), ítems tachados al completar
- **Accesibilidad:** prefers-reduced-motion, contraste 4.5:1, foco visible en inputs
- **Performance:** Login, validación PIN, reserva, check-in < 3s P95
- **Seguridad:** Contraseñas hashed, permisos validados server-side, intentos fallidos limitados

---

## 7. Estructura de archivos Stitch recomendada

Genera estas pantallas en este orden, nombrándolas exactamente:

| Screen ID | Nombre |
|---|---|
| `login` | Login |
| `admin_dashboard` | Panel de Administrador |
| `waiter_floor_plan` | Gestión de Sala — Mapa de mesas |
| `waiter_order_creation` | Crear orden desde mesa |
| `waiter_account_segmentation` | Segmentar cuenta |
| `waiter_checkin` | Check-in y unión de mesas |
| `kds_main` | Kitchen Display System |
| `kds_shrinkage` | Registro de merma y reposición |
| `cashier_billing` | Facturación y cobro |
| `cashier_cash_closing` | Cierre y apertura de caja |
| `inventory_dashboard` | Gestión de inventario |
| `inventory_technical_sheet` | Ficha técnica de platillo |
| `inventory_receipt` | Recepción de inventario |
| `inventory_correction_request` | Solicitud de corrección |
| `reservation_portal_public` | Portal web de reservas |
| `reservation_portal_my_reservations` | Mis reservas (cliente) |
| `reports_sales` | Reportes de ventas y mermas |
| `audit_trail` | Bitácora de auditoría |
| `pin_authorization` | PIN de autorización remota |

**Stitch navigation:**
- Conecta `login` → `admin_dashboard`
- `admin_dashboard` → todas las pantallas según rol
- Desde `waiter_order_creation` → `kds_main` (enviar orden)
- Desde `reservation_portal_public` → `reservation_portal_my_reservations`
- Aplica el sistema de diseño (sección 2) a todo el proyecto.