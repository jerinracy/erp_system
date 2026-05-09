![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST_Framework-red?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Broker-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-Task_Queue-37814A?style=for-the-badge&logo=celery&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
# ERP System

Backend for a **multi-tenant ERP platform**: organizations (**tenants**) onboard through registration (including a time-limited **trial subscription**), manage **inventory** and **sales**, connect **integrations** (API keys and webhooks), run **automation** when business events occur, review **analytics**, and manage **billing** via **SSLCommerz** (subscription plans and payments). The API is built with **Django** and **Django REST Framework**, uses **JWT** for authenticated tenant users, and uses **Celery** with **Redis** for background work such as rule processing, subscription expiry, and notifications.

**Repository**

```bash
git clone https://github.com/jerinracy/erp_system.git
cd erp_system
```

---

## Tech stack

| Layer | Technology |
|--------|------------|
| Runtime | Python 3.10+ |
| Web framework | Django 5.x |
| API | Django REST Framework |
| Authentication | JWT (djangorestframework-simplejwt) |
| Database | PostgreSQL |
| Task queue | Celery |
| Broker & results | Redis |
| Configuration | python-dotenv (`.env`) |
| Outbound HTTP | requests (webhooks, SMS provider) |
| Payments | SSLCommerz (`sslcommerz-lib`; subscription checkout) |
| Images | Pillow (tenant logo `ImageField`) |

---

## Backend capabilities

### Authentication & accounts (`apps.authentication`)

- Company registration with initial tenant and admin user (email-based identity).
- Email verification and resend flows.
- JWT-based login aligned with the custom user model (`email` as username).
- Password reset via tokenized email links.

### Tenants (`apps.tenants`)

- Middleware attaches the current user’s **tenant** to each request.
- Tenant profile read/update and structured fields for company metadata.
- Account deletion request flag for operational follow-up.

### Inventory (`apps.inventory`)

- Full **product** lifecycle: create, list, retrieve, update, delete.
- Tenant-scoped catalog with validation on pricing, stock, and naming.

### Sales (`apps.sales`)

- **Orders** created from line items with transactional stock checks and decrements.
- Order listing, detail, and a structured **invoice** view derived from orders.
- **Public order API** secured by per-tenant **API keys** (`X-API-KEY`), with middleware-level rate limiting.

### Integrations (`apps.integrations`)

- **API keys** for external systems to act on behalf of a tenant (e.g. create orders).
- **Webhooks** for outbound event delivery with signed payloads; failed deliveries can be retried via management commands.

### Automation (`apps.automation`)

- **Domain events** (for example when an order is created) recorded per tenant.
- **Rules** that react to events with actions such as SMS or email, executed asynchronously via Celery.

### Analytics (`apps.analytics`)

- Dashboard-style aggregates: sales totals, order counts, time-bucketed revenue, low-stock signals.
- Additional endpoints for top products, profit-style rollups, growth metrics, and chart-oriented series.

### Billing & subscriptions (`apps.billing`)

- **Subscription plans** (admin-managed): name, price, duration in days, max users, active flag.
- **Registration** creates a **Trial** plan subscription (default **7 days**) so new tenants can use the product immediately.
- **Payments** through **SSLCommerz**: authenticated users start a session (`gateway_url`), complete checkout at the gateway; success activates or renews the tenant subscription and sets tenant status to **active**. Failed or cancelled payments are recorded without extending access.
- **Payment history** per tenant (amount, status, plan name, transaction id).
- **Access control:** inventory, sales (JWT routes), integrations, automation, and analytics require an **active** subscription (`end_date` in the future, status **active**). **Superusers** bypass this check. **Tenant profile** and **billing** endpoints remain available with JWT alone so expired organizations can update company details and purchase a plan. The **public order API** (`X-API-KEY`) also requires an active subscription for the key’s tenant.
- **Celery Beat** runs daily tasks: notify subscriptions expiring in three days (email to `owner_email`), and expire overdue subscriptions (tenant status **inactive**).

### Notifications (`apps.notifications`)

- Shared email utilities used by authentication flows and automation-driven messages.

### Operations

- **Django Admin** for staff-facing data management.
- Optional **`apps/hr`** package exists in the repository; wire it into `INSTALLED_APPS` when you extend the system with HR features.

Endpoint-level contract notes for client applications are in [`docs/FRONTEND_REQUIREMENTS.md`](docs/FRONTEND_REQUIREMENTS.md); [`doc/FRONTEND_REQUIREMENTS.md`](doc/FRONTEND_REQUIREMENTS.md) points to the same document.

---

## Prerequisites

- Python **3.10** or newer  
- **PostgreSQL**  
- **Redis** (Celery broker and result backend; default URL in settings is `redis://127.0.0.1:6379/0`)  
- **Git**

---

## Installation and local run

### 1. Clone the repository

```bash
git clone https://github.com/jerinracy/erp_system.git
cd erp_system
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
```

### 3. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a **`.env`** file in the project root (next to `manage.py`). Development settings load it automatically.

**PostgreSQL**

```env
DB_NAME=erp_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

**Email (recommended for verification and password reset)**

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your_smtp_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=you@example.com
```

**SMS automation (optional)**

```env
SMS_API_KEY=
```

**SSLCommerz (billing; required for paid checkout in non-sandbox only if you enable real charges)**

```env
SSLCOMMERZ_STORE_ID=
SSLCOMMERZ_STORE_PASSWORD=
SSLCOMMERZ_IS_SANDBOX=True
```

Use sandbox credentials while developing; set `SSLCOMMERZ_IS_SANDBOX=False` with live keys only in controlled production environments.

Ensure application URLs in email templates match your deployment by setting **`BASE_URL`** (or equivalent) in the appropriate settings module for each environment. Payment **success, fail, and cancel** callback URLs are derived from the incoming HTTP host when creating a session, so the app must be reachable by SSLCommerz at that host (use a public URL or tunnel for end-to-end gateway tests).

### 5. Create the database

Create an empty PostgreSQL database whose name matches `DB_NAME`, then run migrations:

```bash
python manage.py migrate
```

`manage.py` defaults to **`DJANGO_SETTINGS_MODULE=config.settings.dev`**.

### 6. Create an administrator user

```bash
python manage.py createsuperuser
```

The custom user model authenticates with **email** (not username).

### 7. Start Redis

The default Celery configuration expects Redis on `127.0.0.1:6379`. Example:

```bash
redis-server
```

### 8. Run the HTTP server

```bash
python manage.py runserver
```

Browse the API under paths such as `http://127.0.0.1:8000/api/…` and the admin at `http://127.0.0.1:8000/admin/`.

### 9. Run a Celery worker

In a separate shell, with the same virtual environment and working directory:

```bash
celery -A config worker -l info
```

Run **Celery Beat** in another process if you rely on scheduled tasks (this project schedules **subscription expiry** and **expiry reminder** emails):

```bash
celery -A config beat -l info
```

### 10. Webhook retries (when using integrations)

If failed webhooks are stored in the database, use the project’s management command to retry them, for example:

```bash
python manage.py retry_webhooks
```

Run `python manage.py retry_webhooks --help` for supported options.

---

## Settings layout

| Module | Role |
|--------|------|
| `config.settings.dev` | Default for local development: `DEBUG=True`, PostgreSQL from `.env`. |
| `config.settings.base` | Shared defaults (apps, middleware, JWT, Celery broker URL, etc.). |
| `config.settings.prod` | Starting point for production; supply a strong `SECRET_KEY`, hosts, database credentials, and email configuration via the environment. |

Example:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
```

---

## Repository layout

```text
config/                 # Project settings, URLs, Celery, WSGI/ASGI
apps/
  authentication/     # Users, JWT, verification, password reset
  tenants/              # Multi-tenant company model and middleware
  inventory/            # Products
  sales/                # Orders, invoices, public API
  integrations/       # API keys, webhooks, retries
  automation/         # Events, rules, Celery tasks
  analytics/          # Reporting and dashboards
  billing/            # Subscription plans, payments, SSLCommerz
  notifications/      # Email helpers
  hr/                 # Optional; enable in INSTALLED_APPS when used
core/                 # Shared model utilities
docs/
  FRONTEND_REQUIREMENTS.md
doc/
  FRONTEND_REQUIREMENTS.md  # entry point → see docs/
manage.py
requirements.txt
```

