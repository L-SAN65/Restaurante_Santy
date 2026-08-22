# ARQUITECTURA — Santy POS

> Sistema de Gestión de Restaurante y Reservas (POS + KDS + Reservas + Inventario + Fidelización)
> Decisión registrada: **Django Full-Stack + Tailwind CSS** como frontend unificado.

---

## 1. Decisiones de arquitectura (ADR)

### ADR-001 — Django Full-Stack (un solo framework para backend y frontend)

**Contexto:** Proyecto personal unipersonal, desarrollado con asistencia de IA. El stack técnico fue definido por el cliente: Django + Supabase + Vercel.

**Decisión:** Usar Django para backend **y** frontend mediante su motor de templates, con **Tailwind CSS** como sistema de estilos (diseño Stitch exacto). No se adopta un SPA (React/Next.js).

**Consecuencias:**
- Un solo lenguaje (Python) en todo el código → menos cambio de contexto en prompts de IA y mantenimiento.
- Django Admin cubre la gestión CRUD operativa (inventario, usuarios, reportes).
- El realtime se resuelve con **Supabase Realtime** (push al navegador con RLS) + polling **HTMX**. No hay servidores WebSocket propios: son incompatibles con el runtime serverless de Vercel.
- El frontend es renderizado server-side (HTML + Tailwind), no requiere Node en runtime (solo en build para Tailwind).

### ADR-002 — Supabase como PostgreSQL + servicios auxiliares

- **Base de datos:** PostgreSQL gestionado (ACID, respaldos automáticos RNF-12).
- **RLS:** capa extra de seguridad por fila (complementa validación server-side RNF-02).
- **Realtime:** publica los cambios (estados de mesa, semáforo KDS) que el navegador consume directamente vía suscripción con `anon key` + RLS (sin pasar por Django ni por WebSockets propios).
- **Auth:** se usa el sistema de autenticación de Django (rol por modelo), NO Supabase Auth; esto evita duplicar la lógica de suspensión/bloqueo de 15 min / 5 fallos (RF-02/RF-03).
- **Storage:** los reportes (PDF/Excel) se generan en memoria (`BytesIO`/`FileResponse`) y el navegador los descarga como `attachment`; **no hay almacenamiento persistente en servidor** (el filesystem serverless es efímero y no se necesita). No se usa Supabase Storage.

### ADR-003 — Vercel como plataforma de despliegue

- Django se despliega con soporte **nativo de Vercel** (zero-config: detecta `manage.py` y toma el entrypoint de `WSGI_APPLICATION`). Sin `builds`/`routes` legacy ni `/api`.
- `build.py` es el Build Command: `npm ci` → Tailwind build → `collectstatic` → `migrate` (solo en `VERCEL_ENV=production`).
- Los estáticos se sirven por la **CDN de Vercel**; **WhiteNoise** queda como respaldo de `collectstatic`.
- El runtime es **HTTP-only** (serverless): sin WebSockets; el realtime recae en Supabase Realtime (ADR-002).
- Versión de Python fijada en `.python-version` (3.12, requerida por Django 6.1).

### ADR-004 — Arquitectura modular por dominio (apps Django)

Cada `app` es un bounded context del dominio, con acceso controlado entre ellas:

| App | Dominio | Reglas críticas |
|---|---|---|
| `core` | Usuarios, roles, configuración de negocio | Suspensión 15 min, bloqueo 5 fallos, roles (RF-01..03, RF-34) |
| `reservations` | Mesas, reservas, bloqueo de 2 min | Mínimo 12 h, bloques de 2 h, no-show 15 min, cancelación ≥ 4 h (RF-27..33) |
| `kitchen` | Comandas, KDS, mermas | Semáforo <10/10-20/>20 min, merma con auditoría (RF-05, RF-06, RF-20..22) |
| `billing` | Facturas, caja, cobros parciales | IVA 15%, cierre ciego ±2 USD, anulación solo Admin (RF-07..11, RF-25, RF-26) |
| `inventory` | Insumos, fichas técnicas, recepciones | Costo promedio, habilitación por stock, correcciones aprobadas (RF-13, RF-14, RF-23, RF-24) |
| `loyalty` | Puntos de fidelización | 1 pt/USD entero, canje 10 pts = $1, caducidad 3 meses (RF-15..17) |
| `audit` | Bitácora inmutable y PIN | Log de operaciones críticas, PIN de 60 s un solo uso (RF-18, RF-19, RF-35) |

> Los modelos de `reservations` referencian `kitchen.Dish` y `billing.Invoice` referencia `kitchen.Order`. Las dependencias cruzadas se mantienen al mínimo y por FK (no lógica compartida).

---

## 2. Seguridad y permisos (RNF-01, RNF-02)

- **Contraseñas:** hasheadas por Django (PBKDF2/salt), nunca texto plano.
- **Autorización en servidor:** decorador `login_required` + chequeo de rol en cada vista. La UI no es la única barrera.
- **Cierre de sesión CSRF-protegido**.
- **Bitácora inmutable:** `AuditLog` con campos `readonly` en Admin; los roles operativos no pueden editar/borrar.
- **Rate-limit de login** (RF-02/RF-03) implementado en `core.models.User.record_failed_login()`.

---

## 3. Reglas de negocio invariables (BDD)

| Invariante | Implementación |
|---|---|
| Zona horaria UTC-5 sin DST | `TIME_ZONE = "America/Panama"` en settings |
| Moneda USD, 2 decimales | Campos `DecimalField(10, 2)` + `decimal_to_currency` en templates |
| IVA 15% | Servicio en `billing` (`Invoice` calcula subtotal × 0.15 redondeado) |
| Horario operativo 10:00–00:00 | `BusinessConfig.operating_start/end` |
| Capacidades 2/4/6/12 | `choices` en `reservations.Table` |
| Bloqueo de 2 min en reserva | `TableBlock.expires_at` + `with_for_update()` al confirmar |
| Tolerancia cierre ±2,00 USD | `CashRegister.close_blind()` |
| PIN 60 s un solo uso | `audit.PinToken.valid_until/consumed_at` |

Los valores de negocio (IVA, tolerancias, minutos) son editables por el Administrador desde `BusinessConfig` (Admin Django), sin re-desplegar.

---

## 4. Realtime (KDS y estados de mesa)

El runtime de Vercel es HTTP-only, así que **no se usa Django Channels** (eliminado en el refactor de despliegue). Dos mecanismos cubren el realtime:

### 4a. Supabase Realtime (push, canal preferente)
```
Cambio en Order/Table (Django/Supabase)
   -> Supabase Realtime (Postgres LISTEN/NOTIFY + WAL)
   -> Navegador suscrito con anon_key + RLS
   -> JS actualiza KDS / floor plan / caja sin recargar
```
- El navegador se suscribe con la `SUPABASE_URL` + `SUPABASE_ANON_KEY` (env de Vercel) a las tablas `kitchen_order` / `reservations_table`.
- No hay servidor WebSocket propio ni Redis: nada que escalar en serverless.

### 4b. Polling HTMX (fallback simple, sin dependencias nuevas)
- Vistas KDS / floor plan devuelven un **partial** y el template usa `hx-trigger="every 5s"`.
- Suficiente para 1 restaurante; combinarlas como degradación si Realtime falla.

---

## 5. Estructura de carpetas

```
Restaurante_Santy/
├── santy/                # Config: settings, urls, wsgi (WSGI-only, sin Channels)
├── core/                 # Usuarios, roles, BusinessConfig, login/dashboards
├── reservations/         # Mesas, reservas, TableBlock (concurrencia)
├── kitchen/              # Comandas, KDS, mermas, platillos
├── billing/              # Cajas, facturas, IVA, cierres
├── inventory/            # Insumos, fichas técnicas, recepciones, correcciones
├── loyalty/              # Movimientos de puntos
├── audit/                # AuditLog inmutable + PinToken
├── templates/            # base.html (diseño Stitch) + partials
│   └── core|audit|...    # Pantallas por módulo (Screen IDs de DESIGN.md)
├── static/css/           # input.css (fuente Tailwind) → output.css (compilado)
├── docs/BDD/             # Features Gherkin + DESIGN.md (Stitch)
├── .env.example          # Plantilla para DATABASE_URL de Supabase
├── .python-version       # Versión de Python 3.12 (requisito de Django 6.1)
├── build.py              # Build Command de Vercel (Tailwind + collectstatic + migrate)
├── vercel.json           # Despliegue Vercel (zero-config, sin legacy builds)
└── requirements.txt      # Dependencias Python
```

---

## 6. Pantallas del DISEÑO.md → templates

| Screen ID | Ruta esperada | Estado |
|---|---|---|
| `menu_public` | `templates/reservations/menu.html` | ✅ público sin login (QR/menú digital) — landing `/` → menu |
| `client_login` | `templates/reservations/login.html` | ✅ solo Role.CLIENT (formulario separado del personal) |
| `client_register` | `templates/reservations/register.html` | ✅ registro cliente (Role.CLIENT) con `?next=` |
| `reservation_portal_step1` | `templates/reservations/step1_details.html` | ✅ Luxe paso 1: fecha/hora/comensales (12 h, 10:00–00:00) |
| `reservation_portal_step2` | `templates/reservations/step2_tables.html` | ✅ paso 2: selección visual de mesas con validación capacidad/bloque 2 min |
| `reservation_portal_step3` | `templates/reservations/step3_confirm.html` | ✅ paso 3: confirmación y creación + `success.html` (ref. LX-XXXX) |
| `reservation_portal_my` | `templates/reservations/my_reservations.html` | ✅ mis reservas + cancelación ≥4 h |
| `reservation_portal` legacy | `templates/reservations/portal.html` | ✅ compatibilidad 1-paso (tests) |
| `staff_login` | `templates/core/staff_login.html` | ✅ solo personal (ADMIN/CASHIER/WAITER/CHEF/WAREHOUSE) — rechaza CLIENT |
| `login` legacy | `templates/core/login.html` | ⚠️ conservado, ya no se usa (staff usa `staff_login.html`) |
| `admin_dashboard` | `templates/core/admin_dashboard.html` | ✅ con accesos a roles/inventario/reportes |
| `user_management` | `templates/core/user_management.html` | ✅ ADMIN: gestión de roles (RF-01) + desbloqueo (RF-02/03) |
| `waiter_floor_plan` | `templates/core/waiter_dashboard.html` + `templates/reservations/floor_plan.html` | ✅ |
| `waiter_order_creation` | `templates/kitchen/order_create.html` | ✅ RF-20 |
| `waiter_account_segmentation` | `templates/kitchen/account_segmentation.html` | ✅ RF-22 |
| `waiter_checkin` | `templates/reservations/checkin.html` + `/reservas/sala/checkin/` | ✅ RF-30 |
| `kds_main` | `templates/core/chef_dashboard.html` + `templates/kitchen/kds.html` | ✅ |
| `kds_shrinkage` | `templates/kitchen/shrinkage.html` | ✅ RF-06 |
| `cashier_billing` | `templates/core/cashier_dashboard.html` + `templates/billing/invoice_*.html` | ✅ |
| `cashier_cash_closing` | `templates/billing/cash_register_*.html` | ✅ RF-10/11/25/26 |
| `inventory_dashboard` | `templates/core/warehouse_dashboard.html` + `templates/inventory/dashboard.html` | ✅ |
| `audit_trail` | `templates/audit/trail.html` | ✅ |

---

## 7. Uso en desarrollo

```bash
# 1. Entorno e instalación
python -m venv .venv
.\.venv\Scripts\activate # Windows
pip install -r requirements.txt
npm install

# 2. Configurar base de datos
copy .env.example .env   # completar DATABASE_URL de Supabase (o dejar vacío → SQLite)

# 3. Construir CSS (Tailwind)
npm run build            # o npm run dev para watch

# 4. Migrar y sembrar
python manage.py migrate
python manage.py seed    # create usuarios y BusinessConfig

# 5. Ejecutar
python manage.py runserver
```

**Usuarios de prueba (seed):** `admin@santy.com / admin`, `cajero@santy.com / cajero`, `mesero@santy.com / mesero`, `chef@santy.com / chef`, `bodega@santy.com / bodega`.

---

## 8. Pendientes (siguiente fase)

- Suscripción **Supabase Realtime** en el navegador (KDS / estados de mesa) con RLS + partials **HTMX** como fallback.
- Tests de aceptación a partir de `docs/BDD/*.feature`.
- Pulido visual del flujo Luxe (animaciones Stitch DESIGN.md) y estados vacíos.