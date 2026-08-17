# CHANGELOG — Santy POS

Registro de todos los cambios realizados en la sesión de setup del proyecto.

> **Fecha:** 2026-08-17
> **Estado inicial del repo:** solo existían `docs/BDD/*`, `Requisitos_...md`, `.agents/`, `opencode.json` y `skills-lock.json` (commit `890970d`). No existía código de aplicación.

---

## 1. Infraestructura y toolchain

| Archivo | Descripción |
|---|---|
| `.venv/` | Virtualenv Python 3.13 con dependencias instaladas |
| `requirements.txt` | Dependencias Python de producción (Django 6.1, channels 4.3.2, psycopg 3.3.4, dj-database-url, whitenoise, django-environ, gunicorn, crispy) |
| `package.json` | Scripts npm: `dev` (Tailwind watch) y `build` (Tailwind minify) + devDeps tailwindcss y `@tailwindcss/forms` |
| `package-lock.json` | Lockfile de npm generado por `npm install` |
| `.gitignore` | Excluye `.venv/`, `node_modules/`, `db.sqlite3`, `.env`, `staticfiles/`, CSS compilado, etc. |
| `build.sh` | Build pipeline para Vercel: pip install → npm build → collectstatic → migrate |

---

## 2. Configuración Django

| Archivo | Descripción |
|---|---|
| `manage.py` | Entry point estándar de Django |
| `santy/settings.py` | Configuración completa: apps del proyecto, middleware (WhiteNoise), template dir `templates/`, `AUTH_USER_MODEL = core.User`, `TIME_ZONE = America/Panama` (UTC-5 sin DST), lenguaje `es`, decimales/separadores USD, `DATABASE_URL` vía `django-environ` con fallback a SQLite local, STORAGES WhiteNoise, Crispy Tailwind, CANALES InMemory (dev), variables de negocio |
| `santy/urls.py` | Rutas raíz: `/admin/`, `core`, `reservas/`, `facturacion/`, `cocina/`, `inventario/`, `fidelizacion/`, `auditoria/` |
| `santy/asgi.py` | ASGI con Django Channels (`ProtocolTypeRouter` HTTP + WebSocket) |
| `santy/wsgi.py` | WSGI estándar para despliegue Vercel |
| `santy/routing.py` | `websocket_urlpatterns` (pendiente de consumers) |
| `.env.example` | Plantilla de variables de entorno: `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL` (Supabase opcional) |
| `vercel.json` | Despliegue Vercel con buildpack `@vercel/python` sirviendo `santy/wsgi.py` |
| `opencode.json` | **Pre-existente** (config MCP de Stitch; no fue creado en esta sesión) |

---

## 3. Aplicaciones (apps) y modelos de dominio

### `core` — Núcleo y Autenticación
| Archivo | Contenido |
|---|---|
| `core/models.py` | `Role` (ADMIN, CASHIER, WAITER, CHEF, WAREHOUSE, CLIENT); `User(AbstractUser)` con email como username, `cedula`, control de `failed_login_count`/`suspended_until`/`is_permanently_locked` (RF-02/RF-03), `dashboard_url` por rol; `BusinessConfig` con invariantes de negocio (IVA, horario, bloqueos, tolerancias, PIN, fidelización) |
| `core/views.py` | `login_view` con auditoría de cada intento y redirección por rol; dashboards `admin/`, `cashier/`, `waiter/`, `chef/`, `warehouse` con validación de rol en servidor (RF-34); `CustomLogoutView` auditable |
| `core/urls.py` | Rutas `login/`, `logout/`, `dashboard/` y por rol |
| `core/admin.py` | `CustomUserAdmin` (ventana de control de acceso) y `BusinessConfigAdmin` |
| `core/management/commands/seed.py` | Comando `python manage.py seed`: crea `BusinessConfig` y usuarios de prueba por rol |

### `reservations` — Reservas y Sala
| Archivo | Contenido |
|---|---|
| `reservations/models.py` | `Table` (capacidad 2/4/6/12, posición para floor plan, estado derivado por propiedad `status`); `Reservation` (bloques de 2 h, cancelación ≥ 4 h, no-show con 15 min de gracia); `TableBlock` (bloqueo de 2 min persistente, RF-28) |
| `reservations/admin.py` | Admin de Table, Reservation (filter_horizontal mesas) y TableBlock |

### `kitchen` — Cocina (KDS)
| Archivo | Contenido |
|---|---|
| `kitchen/models.py` | `Order` (comanda En Espera → En Preparación → Listo, `elapsed_minutes` y `traffic_light` semáforo <10/10-20/>20 min, RF-05); `OrderItem` (subtotal con redondeo); `Shrinkage` (merma que conserva cargo + alerta reposición $0, RF-06); `Dish` (platillo con `availability`) |
| `kitchen/admin.py` | Admin de Order con inline de ítems, Shrinkage y Dish |

### `billing` — Facturación y Caja
| Archivo | Contenido |
|---|---|
| `billing/models.py` | `CashRegister` (apertura con fondo > 0, cierre ciego con tolerancia ±2 USD via `close_blind`, justificación obligatoria para descuadre, RF-10/11/25/26); `Invoice` con `subtotal`/`vat_amount`/`total`, `issue()` (Emitida), anulación solo Admin conservando comprobante `annul()`, cobro parcial con `remaining_balance` (RF-07/08/09) |
| `billing/admin.py` | Admin de CashRegister e Invoice |

### `inventory` — Inventario y Bodega
| Archivo | Contenido |
|---|---|
| `inventory/models.py` | `Ingredient` (stock actual, mínimo, costo promedio ponderado via `apply_receipt`, RF-23); `TechnicalSheet` + `TechnicalSheetItem` (ficha técnica para deducción automática y habilitación por stock, RF-13/14); `Receipt` (recepciones confiables con lote/caducidad, confirmación inmutable); `CorrectionRequest` (Pendiente/Aprobada/Rechazada, RF-24) |
| `inventory/admin.py` | Admin de Ingredient, TechnicalSheet con inline, Receipt, CorrectionRequest |

### `loyalty` — Fidelización
| Archivo | Contenido |
|---|---|
| `loyalty/models.py` | `LoyaltyMovement` con `accrue_for_invoice` (1 pt por USD entero, RF-15), `redeem` (canje 10 pts = $1 al subtotal con validación de saldo, RF-16) y `expire_overdue` (caducidad a los 3 meses exactos via helper `add_months`, RF-17) |
| `loyalty/admin.py` | Admin de movimientos de fidelización |

### `audit` — Auditoría
| Archivo | Contenido |
|---|---|
| `audit/models.py` | `AuditLog` (bitácora inmutable: usuario, fecha/hora, acción, resultado, objeto, RF-35/RNF-08; método `log()`); `PinToken` (PIN de 6 dígitos, 60 s, un solo uso, RF-18/19) |
| `audit/views.py` | Vista de bitácora (últimos 200 registros) |
| `audit/urls.py` | Ruta `auditoria/` → `audit:trail` |
| `audit/admin.py` | Admin de AuditLog solo lectura y PinToken |

---

## 4. Frontend (Django templates + Tailwind)

| Archivo | Descripción |
|---|---|
| `tailwind.config.js` | Sistema de diseño Stitch: colores exactos de DESIGN.md (`primary #22C55E`, warning, danger, info, estados de mesa, semáforo KDS), tipografía Inter, radio de componente 8px/card 12px, animaciones fade-scale y slide-up |
| `static/css/input.css` | Componentes base: `.btn*` (altura 40px, radius 8px), `.input`, `.label`, `.card`, `.badge`, `.scrim`, `.nav-link` + `prefers-reduced-motion` |
| `static/css/output.css` | CSS compilado por Tailwind (generado en build; ignorado en git) |
| `templates/base.html` | Layout raíz: fuente Inter, mensajes flash, footer con indicador UTC-5/USD/IVA |
| `templates/partials/sidebar.html` | Sidebar por rol (iconos + rutas) |
| `templates/core/login.html` | SCREEN `login`: fondo degradado verde, logo "S", toggle contraseña, mensajes de error |
| `templates/core/admin_dashboard.html` | SCREEN `admin_dashboard`: 4 tarjetas métrica + tabla de órdenes |
| `templates/core/waiter_dashboard.html` | SCREEN `waiter_floor_plan` (esqueleto con leyenda de estados) |
| `templates/core/chef_dashboard.html` | SCREEN `kds_main` (esqueleto fondo oscuro) |
| `templates/core/cashier_dashboard.html` | SCREEN `cashier_billing` (esqueleto) |
| `templates/core/warehouse_dashboard.html` | SCREEN `inventory_dashboard` (esqueleto) |
| `templates/audit/trail.html` | SCREEN `audit_trail`: tabla funcional de la bitácora + banner "inmutable" |

---

## 5. Documentación

| Archivo | Descripción |
|---|---|
| `docs/ARQUITECTURA.md` | Decisiones ADR-001..004, mapa de apps/dominios/reglas, seguridad, invariantes BDD → código, realtime, estructura, mapeo Screen IDs → templates, instrucciones de uso y pendientes |

---

## 6. Verificaciones ejecutadas (evidencia)

1. `python manage.py check` → 0 issues.
2. Migraciones aplicadas (core, audit, reservations, kitchen, billing, inventory, loyalty) sin cambios pendientes.
3. Seed: 5 usuarios por rol creados.
4. Login admin `admin@santy.com/admin` → 302 a `/dashboard/admin/`; `/dashboard/admin/` → 200.
5. Login fallido → no autentica y registra evento en `AuditLog`.
6. Bloqueo de mesa activo → estado `BLOCKED`.
7. No-show a los 16 min → estado `NO_SHOW`.
8. Factura $100 + IVA 15% → total $115; acreditación de 115 pts (1 pt/USD) con expiración +3 meses.
9. Cierre ciego: diferencia ≤ $2 → `SQUARED`; > $2 → `UNRECONCILED`.

---

## 7. Pendientes (no implementados en esta sesión)

- Consumers de Django Channels para KDS realtime (`kitchen/consumers.py`) + integración con Supabase Realtime.
- Vistas/forms de: toma de orden, segmentación de cuenta, check-in, merma, facturación/cobro, cierre de caja, recepciones, portal público de reservas.
- Mapeo completo de las ~20 pantallas Stitch restantes (ver §6 de `docs/ARQUITECTURA.md`).
- Tests de aceptación derivados de `docs/BDD/*.feature`.
- Conexión real a Supabase (`DATABASE_URL`) y configuración de Redis para Channels en producción.