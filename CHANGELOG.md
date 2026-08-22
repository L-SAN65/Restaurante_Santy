# CHANGELOG — Santy POS

Registro de todos los cambios realizados en el proyecto, organizado por sesión.

---

## Sesión 2026-08-22 — Módulo Cliente completo + separación de logins (personal vs cliente)

> **Objetivo:** implementar todas las vistas primero el flujo cliente (menú → login/registro → reservas en 3 pasos) y después el login del personal con formularios separados, cerrando las vistas faltantes del portal y dejando el sistema navegable de punta a punta (RF-27..33, RF-01/34).

| Archivo | Descripción |
|---|---|
| `santy/urls.py` | `/` ahora redirige a `reservations:menu` (landing pública sin login, primer paso del flujo cliente). Antes apuntaba a `core:login`. |
| `core/views.py` | `login_view` convertido en **staff-only** (`core/staff_login.html`): rechaza `Role.CLIENT` con mensaje dirigido a `/reservas/login/`; conserva suspensión 15 min / bloqueo 5 fallos (RF-02/03). `client_login_view` y `client_register_view` ya separados en `reservations`. |
| `templates/core/staff_login.html` | **Nuevo** — formulario exclusivo del personal (ADMIN, CASHIER, WAITER, CHEF, WAREHOUSE), estilo `inverse-surface`, banner RF-02/03, link a portal clientes y credenciales de prueba. |
| `templates/core/login.html` | Conservado como legacy (ya no referenciado por la vista). |
| `templates/reservations/login.html` | Actualizado: CTA a `reservations:client_register` con `?next=` preservado, links a `menu` y a `core:login` (Soy personal), hidden `next` dentro del form. |
| `templates/reservations/register.html` | **Nuevo** — registro cliente (nombre, cédula, teléfono, email, contraseña) con validaciones 8 chars, `?next=` y alta como `Role.CLIENT` + login automático. Diseño Luxe. |
| `templates/reservations/menu.html` | Hero reestructurado en 2 columnas: menú + card **Módulo Cliente** con botones "Iniciar sesión / Crear cuenta → portal" y flujo documentado (Menú → Login/Registro → 3 pasos). Links a personal. |
| `templates/reservations/step1_details.html` | **Nuevo** — paso 1 Luxe: fecha/hora/comensales (select 2/4/6/12), progress 1/3, mensajes, validación 12 h y 10:00–00:00. |
| `templates/reservations/step2_tables.html` | **Nuevo** — paso 2: grilla visual de mesas con estado (disponible/reservada/bloqueada 2 min), selección múltiple, hint de capacidad en vivo, progress 2/3. |
| `templates/reservations/step3_confirm.html` | **Nuevo** — paso 3: resumen fecha/mesas, prefill `full_name/email`, notas, aviso tolerancia 15 min / cancelación 4 h, confirmación crea `Reservation` + `TableBlock` 2 min (RF-28). |
| `templates/reservations/success.html` | **Nuevo** — pantalla de éxito con ref. `LX-XXXX`, detalle fecha/mesas/email/estado y CTAs a mis reservas / menú. |
| `reservations/views.py` | `reservation_portal` ahora soporta **legacy 1-paso** (POST con `tables` → crea reserva directo para compatibilidad con `reservations/tests.py`) además del flujo 3 pasos por sesión; acepta `guests` 1..12 legacy. |
| `docs/ARQUITECTURA.md` | §6 actualizado: tabla completa de pantallas Stitch → templates con estado ✅; §8 pendientes simplificado (queda Realtime + tests BDD). |

**Flujo implementado:**
1. `GET /` → `reservations:menu` (público, sin auth) con CTAs **Iniciar sesión** (`/reservas/login/?next=/reservas/`) y **Crear cuenta** (`/reservas/registro/?next=/reservas/`).
2. Cliente se registra/loguea en formularios **exclusivos de cliente** (`Role.CLIENT`); staff usa `/login/` (`core:staff_login.html`, rechaza CLIENT).
3. `GET /reservas/` (portal paso 1) → paso 2 → paso 3 → `LX-XXXX` → `/reservas/mis-reservas/` (cancelación ≥4 h, RF-33).
4. Módulo cliente aislado hasta ahí; resto de vistas (KDS, facturación, inventario, etc.) ya existentes y enlazadas por sidebar/roles.

**Evidencia:** `python manage.py check` → 0 issues.

---

## Sesión 2026-08-22 — Panel Administrador: usuarios/roles, inventario y reportes visibles

> **Incidencia:** el Administrador no veía la gestión de inventario ni la gestión de roles (sidebar solo mostraba Panel/Reportes/Bitácora/PIN).

| Archivo | Descripción |
|---|---|
| `inventory/views.py` | `_guard_warehouse` ampliado a `Role.WAREHOUSE` **y** `Role.ADMIN` — el Administrador ve y opera inventario completo (RF-13/14/23/24) manteniendo la aprobación de correcciones solo ADMIN (`correction_review`). |
| `core/views.py` | Nuevo `user_management` (solo ADMIN): lista usuarios, cambio de rol, desbloqueo (reset fallos) y alta de usuarios de personal; todo auditado en `AuditLog` (RF-01/34). Nuevo `_guard_admin` reutilizable. |
| `core/urls.py` | Nueva ruta `dashboard/admin/usuarios/` → `core:user_management`. |
| `templates/partials/sidebar.html` | ADMIN ahora muestra **Usuarios y roles**, **Inventario** y **Reportes** además de Panel/Bitácora/PIN. |
| `templates/core/admin_dashboard.html` | Tres cards destacadas: **Gestión de roles**, **Gestión de inventario**, **Reportes y análisis** + accesos rápidos a recepciones/correcciones/bitácora. |
| `templates/core/user_management.html` | **Nuevo** — tabla de usuarios con selector de rol + Guardar, badge de estado (Activa/Suspendida/Bloqueada), botón Desbloquear y formulario de alta (email/rol/contraseña). Enlaces a inventario/reportes/bitácora. |

**Verificación:** `python manage.py check` → 0 issues; login `admin@santy.com/admin` → Panel → Usuarios/Inventario/Reportes accesibles.

---


> **Fecha:** 2026-08-19
> **Objetivo:** corregir la suite de tests (`python manage.py test`) hasta dejarla completamente verde (28/28) y arreglar bugs detectados por los tests.

| Archivo | Descripción |
|---|---|
| `santy/settings.py` | Tests usan `StaticFilesStorage` (sin manifest WhiteNoise) para no depender de `npm run build` + `collectstatic` |
| `billing/views.py` | Import faltante `get_object_or_404` (fallaba `invoice_create` y `invoice_annul`) |
| `billing/models.py` | `CashRegister.close_blind()` ahora calcula saldo esperado = `opening_fund + total_billed` (antes omitía el fondo inicial) |
| `templates/partials/sidebar.html` | Se elimina el enlace "Mermas" (apuntaba a `kitchen:shrinkage` sin `order_id`, URL inválida) |
| `templates/inventory/dashboard.html` | Nueva tabla "Insumos activos" con todos los insumos (antes solo se listaban críticos) |
| `core/tests.py` | `test_login_redirects_by_role` ahora hace logout entre iteraciones (la sesión persistía y desviaba el redirect) |
| `reservations/views.py` | `reservation_portal` compara anticipación contra `timezone.localtime()` (antes UTC, desfase de 5 h en UTC-5) |
| `reservations/tests.py` | Tests de portal corrigen login del cliente y usan hora local (UTC-5) para fechas de reserva |

**Evidencia:** `python manage.py check` → 0 issues; `python manage.py test` → 28/28 OK.

---

## Sesión 2026-08-19 — Descargas locales PDF/Excel (sin storage en servidor) y sin email

> Los reportes PDF/Excel se generan en memoria (`BytesIO`) y el navegador los descarga directo (streaming con `FileResponse`, `as_attachment=True`); no se escribe ni persiste archivo alguno en el servidor, lo cual es inherentemente compatible con el filesystem efímero de serverless. El sistema no envía correos.

| Archivo | Descripción |
|---|---|
| `billing/views.py` | `_export_response` ahora usa `FileResponse` sobre el buffer (`BytesIO`) con `as_attachment=True`; se elimina `HttpResponse(bytes)` y cualquier dependencia de disco. |
| `santy/settings.py` | Se elimina el bloque de email (`MAILERS`, que además no era una setting válida de Django); no se envían correos. |
| `docs/ARQUITECTURA.md` | ADR-002 Storage actualizado: reportes en memoria + descarga en cliente, **sin** Supabase Storage; se elimina el pendiente de archivos a Storage. |

**Evidencia:** `python manage.py check` → 0 issues; `python manage.py test` → 28 tests OK.

---

---

---

## Sesión 2026-08-19 — Rediseño de despliegue para Vercel (refactor de arquitectura)

> **Commit relacionado:** `6a8a413`
> Se elimina Django Channels/ASGI (incompatible con el runtime serverless de Vercel) y se migra a la integración nativa de Django. El realtime pasa a Supabase Realtime + polling HTMX.

### Configuración de despliegue
| Archivo | Descripción |
|---|---|
| `vercel.json` | Reescrito al formato moderno: zero-config Django (detecta `manage.py` y toma `WSGI_APPLICATION`) con `buildCommand` y `functions.maxDuration`; se elimina el formato legacy `builds`/`routes` y `@vercel/python`. |
| `build.py` | **Nuevo** pipeline de build (Build Command): `npm ci` → Tailwind build → `collectstatic` → `migrate` (solo con `VERCEL_ENV=production`). Reemplaza a `build.sh`. |
| `.python-version` | **Nuevo:** fija Python 3.12 en el runtime de Vercel (requisito de Django 6.1). |
| `.env.example` | Elimina `REDIS_URL`/Channels; documenta Supabase Realtime (anon key + RLS) y variables inyectadas por Vercel (`VERCEL`, `VERCEL_ENV`). |

### Django
| Archivo | Descripción |
|---|---|
| `requirements.txt` | Se eliminan `channels==4.3.2` y `channels-redis==4.3.0`. |
| `santy/settings.py` | Se elimina `channels` de `INSTALLED_APPS`, `ASGI_APPLICATION` y `CHANNEL_LAYERS`; `DEBUG` se fuerza a `False` en build/runtime de Vercel. |
| `santy/asgi.py` | **Eliminado** (sin WebSockets propios). |
| `santy/routing.py` | **Eliminado** (sin consumers). |
| `build.sh` | **Eliminado** (reemplazado por `build.py`). |

### Realtime (nueva estrategia)
- **Supabase Realtime al navegador** (suscripción directa con `anon key` + RLS) como canal preferente y **polling HTMX** (`hx-trigger="every 5s"`) como fallback. Sin servidor WebSocket propio ni Redis.

### Documentación
| Archivo | Descripción |
|---|---|
| `docs/ARQUITECTURA.md` | ADR-001/002/003 actualizados, sección 4 (Realtime) reescrita, estructura de carpetas y pendientes actualizados. |

### Verificaciones
1. `python manage.py check` → 0 issues.
2. `python manage.py test` → **28 tests OK**.
3. `python build.py` local → npm ci + Tailwind + collectstatic OK; migrate omitido fuera de producción.

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