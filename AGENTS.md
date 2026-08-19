# AGENTS.md — Estándar del proyecto Santy POS

> Este archivo define las convenciones, comandos y reglas que todo agente (o persona) debe seguir al trabajar en este repositorio. Se actualiza junto con el código.

---

## 1. Qué es este proyecto

**Santy POS** es un sistema de gestión de restaurante y reservas (POS + KDS + Reservas + Inventario + Fidelización), construido como **Django Full-Stack** con **Tailwind CSS** (diseño Stitch en `docs/stitch/design-system/DESIGN.md`). Despliegue en **Vercel** con **Supabase** (PostgreSQL) como base de datos de producción.

**Regla de oro:** esta es una base de código **en español** (etiquetas, mensajes, templates) porque los usuarios finales son hispanohablantes. Los identificadores de código (nombres de variables, funciones, clases) pueden ir en inglés, pero **toda cadena visible al usuario va en español**.

---

## 2. Arquitectura y contexto

| App | Dominio | Invariantes BDD |
|---|---|---|
| `core` | Usuarios, roles, `BusinessConfig`, login | Suspensión 15 min / bloqueo 5 fallos (RF-02/03), redirección por rol (RF-01/34) |
| `reservations` | Mesas, reservas, `TableBlock` | Mín. 12 h antelación, bloques 2 h, no-show 15 min, cancelación ≥ 4 h (RF-27..33) |
| `kitchen` | Comandas, KDS, mermas, platillos | Semáforo <10 / 10-20 / >20 min, merma auditada c/ reposición $0 (RF-05/06/20/21) |
| `billing` | Cajas, facturas, IVA | IVA 15%, cierre ciego ±$2.00, anulación solo ADMIN (RF-07..11/25/26) |
| `inventory` | Insumos, fichas técnicas, recepciones | Costo promedio ponderado, habilitación por stock, correcciones aprobadas (RF-13/14/23/24) |
| `loyalty` | Puntos de fidelización | 1 pt/USD entero, canje 10 pts = $1, caducidad 3 meses (RF-15..17) |
| `audit` | Bitácora inmutable, PIN | Log de operaciones críticas, PIN 60 s un solo uso (RF-18/19/35) |

Referencias:
- `docs/ARQUITECTURA.md` — decisiones ADR, mapa de pantallas → templates, pendientes.
- `docs/BDD/*.feature` — especificaciones Gherkin (fuente de verdad del comportamiento).
- `docs/stitch/design-system/DESIGN.md` — sistema de diseño (colores, tipografía, shapes).
- Realtime (KDS/estados de mesa): **Supabase Realtime** directo al navegador (anon key + RLS) con polling **HTMX** como fallback. Sin WebSockets propios (serverless de Vercel es HTTP-only).

---

## 3. Invariantes globales (no romper bajo ninguna circunstancia)

- **Zona horaria** `America/Panama` (UTC-5, sin DST). Nunca `USE_TZ = False`.
- **Moneda** USD con 2 decimales (`DecimalField(10,2)`), separador decimal `.` y miles `,`.
- **IVA 15%** editable en `BusinessConfig.vat_rate`; siempre calcular y redondear a 2 decimales.
- Todos los valores de negocio se leen de `BusinessConfig` (`get_business_config()`), nunca hardcodeados.
- **Auditoría**: toda operación crítica debe registrar `AuditLog.log(...)`. La bitácora es inmutable.
- **Autorización en servidor**: cada vista valida el rol del usuario; la UI no es la única barrera.
- **Seguridad**: nunca loguear ni exponer contraseñas/PIN en texto plano; CSRF activo en todo POST.

---

## 4. Comandos del proyecto

```bash
# Instalación
python -m venv .venv
.\.venv\Scripts\activate        # Windows
pip install -r requirements.txt
npm install

# Configuración
copy .env.example .env           # completar DATABASE_URL (Supabase) o dejar vacío -> SQLite

# CSS (Tailwind)
npm run build                    # compilación minificada
npm run dev                      # watch (desarrollo)

# Django
python manage.py check           # verificación de integridad (SIEMPRE antes de terminar)
python manage.py migrate
python manage.py seed            # usuarios de prueba + BusinessConfig
python manage.py runserver
python manage.py test            # ejecutar TODA la suite de tests

# Usuarios seed: admin@santy.com/admin · cajero@santy.com/cajero · mesero@santy.com/mesero ·
#                chef@santy.com/chef · bodega@santy.com/bodega

# Despliegue (Vercel) — réplica local del Build Command
python build.py            # npm ci + tailwind + collectstatic (+ migrate solo en producción)
```

---

## 5. Convenciones de código

### Python / Django
- Vistas basadas en **funciones** salvo que exista motivo para CBV (el resto del código es FBV).
- Guard de rol en cada vista con patrón:
  ```python
  def _guard_cashier(request):
      if request.user.role != Role.CASHIER:
          messages.error(request, "No tiene permisos para acceder a este módulo.")
          return redirect(request.user.dashboard_url)
      return None
  ```
- Lógica de dominio en **modelos (métodos/propiedades)**, no en vistas (p. ej. `Invoice.issue()`, `CashRegister.close_blind()`, `Table.status`).
- Auditoría via `AuditLog.log(user, ActionType.X, Result.Y, object_type=..., object_id=..., detail=...)`.
- Usar `@login_required` + guard de rol en toda vista protegida.
- Importaciones **locales** dentro de la función (style ya usado en el proyecto) para evitar ciclos entre apps.

### Frontend (Django templates + Tailwind)
- Todos los templates están en `templates/<app>/...` y extienden `templates/base.html`.
- Componentes base de `static/css/input.css`: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.input`, `.label`, `.card`, `.badge`, `.scrim`, `.nav-link`.
- Colores/tokens de `tailwind.config.js` (primary verde `#22C55E`, surface, mesa.*, kds.*).
- Respetar `prefers-reduced-motion` (ya hay media query global en `input.css`).
- Clases `sr-only` para texto accesible y `aria-*` en controles interactivos.

### Git / commits
- Mensajes de commit en español, convención Conventional Commits: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.
- **Nunca commitear** `.env`, `db.sqlite3`, `node_modules/`, `.venv/`, `staticfiles/`, `static/css/output.css` (ya en `.gitignore`).

---

## 6. Regla de documentación de cambios (OBLIGATORIA)

Dos archivos son la tarjeta de cada sesión de trabajo:

### `CHANGELOG.md`
Todo cambio funcional o estructural se registra como entrada en la sección del día (fecha, commit relacionado, y tabla/lista de archivos modificados con descripción). Mantener el estilo existente del archivo.

### `AGENTS.md`
Este archivo. Se actualiza cuando cambian convenciones, comandos, estructura o invariantes. La regla de documentación vive aquí.

**Al terminar una sesión**:
1. Correr `python manage.py check` y `python manage.py test` (todo verde).
2. Actualizar `CHANGELOG.md` con los archivos y comportamientos nuevos.
3. Actualizar `docs/ARQUITECTURA.md` si cambió la tabla de pantallas/templates o pendientes.
4. Si cambió una convención o comando, reflejarlo en este `AGENTS.md`.