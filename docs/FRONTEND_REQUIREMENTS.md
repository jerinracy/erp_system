# Frontend developer requirements — SaaS ERP API

This document maps **features → pages/UI → HTTP endpoints → payloads** so a frontend team can implement the full product against the current Django REST Framework backend.

**Assumed API base URL:** `{API_BASE}` (e.g. `https://api.yourcompany.com` or `http://127.0.0.1:8000`). All paths below are **relative** to `{API_BASE}` unless noted.

---

## Global conventions

### Authentication (tenant user app)

| Mechanism | When to use |
|-----------|----------------|
| **JWT Bearer** | Authenticated `/api/auth/*`, `/api/tenants/`, `/api/billing/*`, and—when the tenant has an **active subscription**—`/api/inventory/`, `/api/sales/` (non-public), `/api/integrations/`, `/api/automation/`, `/api/analytics/`. |
| **Header** | `Authorization: Bearer <access_token>` |
| **Token pair** | Obtained from `POST /api/auth/login/`. The backend uses **email** as the username field (`USERNAME_FIELD`), not `username`. |
| **No cookie session** | Unless you add session auth, treat the API as **stateless JWT**. |

### Public / integration (server-to-server or external checkout)

| Mechanism | When to use |
|-----------|----------------|
| **API key** | `POST /api/sales/public/orders/` only. |
| **Header** | `X-API-KEY: <uuid_api_key>` |
| **No JWT** | Do not send `Authorization` for this route; middleware resolves tenant from the key. |

### Tenant context

- After login, every authenticated request is scoped to **`request.user.tenant`** on the server.
- The client does **not** send `tenant_id` in headers for normal operations; the backend derives it from the user (except public API key flow, where tenant comes from the key).

### Subscription gating (ERP features)

- **Active subscription** means the tenant has at least one `Subscription` with `status === "active"` and `end_date` in the future. **Superusers** skip this check.
- Endpoints under **inventory, sales (JWT), integrations, automation, and analytics** use `ERPAPIView` and return **`403`** with message **`Subscription expired`** when there is no active subscription.
- **`/api/tenants/*`** profile and delete-request routes use authentication only (no subscription check) so users can fix company details or subscribe after expiry.
- **`/api/billing/*`** uses `AuthenticatedAPIView` only—**expired tenants can list plans, create payments, and view payment history** to renew.
- **`POST /api/sales/public/orders/`** returns **`403`** `{ "error": "Subscription expired" }` if the API key’s tenant has no active subscription.
- **Login response** includes a **`subscription`** summary (see A2) so the SPA can show status, plan name, and expiry without an extra call.

### Content type

- Use `Content-Type: application/json` for JSON bodies.

### Error shapes (typical)

Responses are not fully normalized; handle all of these:

| Shape | Example | Typical status |
|-------|---------|----------------|
| Field errors | `{"email": ["This field is required."]}` | `400` |
| Custom object | `{"error": "Verify your email first"}` | `400` / `401` |
| DRF default | `{"detail": "Authentication credentials were not provided."}` | `401` |

### CORS

- Backend settings in this repo do not define `django-cors-headers`; coordinate with backend if the SPA is on another origin.

### Pagination / filtering

- **Not implemented** on list endpoints: responses are full lists. Plan UI pagination client-side or agree a backend change.

### Date / numbers

- Datetimes are ISO-8601 strings (UTC with `USE_TZ = True`).
- Money fields are decimals serialized as numbers or strings depending on serializer/JSON encoder; treat as **decimal** in UI.

---

## Feature group A — Authentication & onboarding

**Product goal:** Register a company (tenant), verify email, log in with JWT, reset password.

### Suggested pages

| Page | Purpose |
|------|---------|
| Register | Collect company + admin user; submit registration. |
| Verify email | Deep link from email (`token` query); show success/failure. |
| Login | Email + password → store tokens. |
| Forgot password | Submit email (generic success message). |
| Reset password | Deep link from email (`token` query) + new password form. |
| Resend verification | Optional; user enters email to get a new link. |

### Endpoints

#### A1 — Register company + admin user

| | |
|--|--|
| **Method / path** | `POST /api/auth/register/` |
| **Auth** | None |
| **Body (JSON)** | `{ "email": string, "password": string, "company_name": string }` |
| **Success** | `201` — `{ "message": "Company registered" }` |
| **Errors** | `400` — validation errors on fields |

**Notes:** Server creates `Tenant` (status **`active`**), `User` (role `admin`), a **7-day trial** `Subscription` linked to a **Trial** plan (`get_or_create` by name, price `0`, `max_users` 3 unless already changed in DB), and sends verification email asynchronously (email configuration must be valid in environment).

#### A2 — Login (JWT)

| | |
|--|--|
| **Method / path** | `POST /api/auth/login/` |
| **Auth** | None |
| **Body** | `{ "email": string, "password": string }` |

**Success `200`:** Body follows **djangorestframework-simplejwt** `TokenObtainPair` (typically includes at least):

- `access` — short-lived JWT string  
- `refresh` — refresh token string (if enabled in library defaults)  
- `subscription` — object added by the backend:  
  - `is_active` — boolean (whether the tenant has a current active subscription window)  
  - `plan` — string \| null (plan name, e.g. `"Trial"`, or `null` if none)  
  - `expires_at` — ISO datetime string \| null (subscription `end_date`, or `null`)

**Important:** This repository **does not** register a `POST /api/auth/token/refresh/` route. Plan either:

- access-token-only UX until access expires, or  
- backend adds SimpleJWT `TokenRefreshView` when you need silent refresh.

**Errors:** `401` / `400` — invalid credentials or validation.

**Unverified users:** Login uses `CustomTokenObtainPairView`; unverified accounts get validation error **`{ "error": "Verify your email first" }`** (no tokens).

**After renewal:** Prefer re-login or another API read if you need an updated `subscription` summary in the client; the JWT claims do not carry subscription state.

#### A3 — Verify email (link from email)

| | |
|--|--|
| **Method / path** | `GET /api/auth/verify-email/?token=<uuid>` |
| **Auth** | None |
| **Success** | `200` — `{ "message": "Email verified successfully" }` |
| **Errors** | `400` — missing/invalid/expired/used token messages under `{ "error": "..." }` |

**UI:** Prefer a dedicated route e.g. `/verify-email?token=…` that calls this GET (or opens in browser if you use full-page redirect).

#### A4 — Resend verification email

| | |
|--|--|
| **Method / path** | `POST /api/auth/resend-verification/` |
| **Auth** | None (default DRF permission is permissive unless changed) |
| **Body** | `{ "email": string }` |
| **Success** | `200` — `{ "message": "Verification link sent" }` |
| **Errors** | `404` — `{ "error": "User not found" }` if email not registered |

**UI:** Consider throttling in UI; backend may not rate-limit.

#### A5 — Request password reset

| | |
|--|--|
| **Method / path** | `POST /api/auth/forgot-password/` |
| **Auth** | None |
| **Body** | `{ "email": string }` |
| **Success** | `200` — `{ "message": "If account exists, reset link sent" }` (same message whether or not user exists) |
| **Errors** | `400` if `email` missing |

#### A6 — Reset password (complete)

| | |
|--|--|
| **Method / path** | `POST /api/auth/reset-password/?token=<uuid>` |
| **Auth** | None |
| **Body** | `{ "password": string }` |
| **Success** | `200` — `{ "message": "Password reset successful" }` |
| **Errors** | `400` — invalid/expired token or missing fields |

#### A7 — Test tenant (debug / QA)

| | |
|--|--|
| **Method / path** | `GET /api/auth/test-tenant/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "user": "<email>", "tenant": "<Tenant str>" }` |

**UI:** Optional internal/debug screen only; remove from production UX if not desired.

---

## Feature group B — Tenant profile & company settings

**Product goal:** View and edit company profile; request account deletion.

### Suggested pages

| Page | Purpose |
|------|---------|
| Company profile | Read-only display of tenant fields. |
| Company settings | Edit allowed fields (partial update). |
| Danger zone | Submit “delete my organization” request. |

### Data model (API surface)

`GET`/`PUT` use the same logical **Tenant** resource. Serializer exposes **all model fields** except these are **read-only** on writes: `id`, `status`, `is_delete_requested`.

Typical fields returned (align with live API and migrations):

| Field | Type | Notes |
|-------|------|--------|
| `id` | number | Read-only |
| `name` | string | Company name |
| `owner_name` | string \| null | |
| `owner_email` | string \| null | |
| `phone_number` | string \| null | |
| `address` | string \| null | |
| `business_type` | string \| null | |
| `logo` | file URL \| null | `ImageField` — multipart if backend extended; current update uses JSON in code paths |
| `is_delete_requested` | boolean | Read-only via serializer |
| `status` | `"pending"` \| `"active"` \| `"inactive"` | Read-only via serializer |
| `created_at` / `updated_at` | datetime | If on `TimeStampedModel` and included in `__all__` |

**Logo uploads:** Current `TenantUpdateView` uses JSON `TenantSerializer`; if `logo` is not writable via JSON in practice, confirm with backend or use multipart if they add `MultiPartParser`.

### Endpoints

#### B1 — Get tenant profile

| | |
|--|--|
| **Method / path** | `GET /api/tenants/profile/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — tenant JSON object |

#### B2 — Update tenant profile (partial allowed)

| | |
|--|--|
| **Method / path** | `PUT /api/tenants/profile/update/` |
| **Auth** | Bearer JWT |
| **Body** | Partial tenant fields (same keys as profile) |
| **Success** | `200` — updated tenant object |
| **Errors** | `400` — validation |

#### B3 — Request tenant deletion

| | |
|--|--|
| **Method / path** | `POST /api/tenants/delete-request/` |
| **Auth** | Bearer JWT |
| **Body** | Empty object `{}` acceptable |
| **Success** | `200` — `{ "message": "Delete request submitted" }` |

**Effect:** Sets `tenant.is_delete_requested = true` (admin workflow on backend TBD).

---

## Feature group C — Inventory (products)

**Product goal:** CRUD products for the current tenant. **Categories** exist in the DB model as `Product.category` FK but **there is no Category API** in this repo—either omit category management UI or send `category` id only if pre-seeded via admin.

### Suggested pages

| Page | Purpose |
|------|---------|
| Product list | Table/grid with stock, price, actions. |
| Product create | Form with validation rules below. |
| Product detail | Single product read. |
| Product edit | Partial update. |
| Product delete | Confirm then delete. |

### Product fields (from API serializer `fields = "__all__"`)

Includes at minimum:

| Field | Type | Validation (server) |
|-------|------|---------------------|
| `id` | number | Read-only on create |
| `tenant` | number | Read-only; set by server from user |
| `name` | string | Non-empty after trim; unique per tenant case-insensitive |
| `description` | string \| null | |
| `cost_price` | decimal | Default 0 |
| `price` | decimal | Must be `> 0` |
| `stock` | integer | Must be `>= 0` |
| `category` | number \| null | FK to `Category` |
| `created_at` / `updated_at` | datetime | If present on model |

### Endpoints

#### C1 — List products

| | |
|--|--|
| **Method / path** | `GET /api/inventory/products/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — JSON array of product objects |

#### C2 — Create product

| | |
|--|--|
| **Method / path** | `POST /api/inventory/products/create/` |
| **Auth** | Bearer JWT |
| **Body** | Product fields **excluding** `tenant` (server assigns) |
| **Success** | `201` — created product object |
| **Errors** | `400` |

#### C3 — Product detail

| | |
|--|--|
| **Method / path** | `GET /api/inventory/products/<pk>/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — product object |
| **Errors** | `404` — `{ "error": "Product not found" }` |

`<pk>` = integer primary key.

#### C4 — Update product (partial)

| | |
|--|--|
| **Method / path** | `PUT /api/inventory/products/<pk>/update/` |
| **Auth** | Bearer JWT |
| **Body** | Any subset of writable product fields |
| **Success** | `200` — updated product |
| **Errors** | `404` / `400` |

#### C5 — Delete product

| | |
|--|--|
| **Method / path** | `DELETE /api/inventory/products/<pk>/delete/` |
| **Auth** | Bearer JWT |
| **Success** | `204` — no body |
| **Errors** | `404` |

---

## Feature group D — Sales (orders & invoices)

**Product goal:** Staff creates orders from line items (product + quantity); lists orders; views detail and printable-style invoice JSON. Stock is decremented on the server inside a transaction.

### Suggested pages

| Page | Purpose |
|------|---------|
| New order | Line items: product picker + quantity; submit array. |
| Orders list | Columns: id, total, date. |
| Order detail | Line items with product name, qty, unit price. |
| Invoice view | Same as detail + invoice-specific fields (invoice id, subtotals). |

### Line item input (create order)

Array of objects (send as **JSON array** at root for `many=True` serializer):

```json
[
  { "product_id": 1, "quantity": 2 },
  { "product_id": 3, "quantity": 1 }
]
```

**Server behavior:** Looks up each product by `id` **and tenant**; checks `stock >= quantity`; decrements stock; creates `Order` and `OrderItem` rows; sets `Order.total_amount`.

**Errors:** `400` with `{ "error": "<message>" }` for business failures (e.g. insufficient stock, product not found). Non-array or invalid items return serializer errors.

### Endpoints (authenticated)

#### D1 — Create order

| | |
|--|--|
| **Method / path** | `POST /api/sales/orders/create/` |
| **Auth** | Bearer JWT |
| **Body** | JSON array of `{ "product_id": int, "quantity": int }` |
| **Success** | `201` — `{ "message": "Order created", "order_id": int }` |
| **Errors** | `400` |

#### D2 — List orders

| | |
|--|--|
| **Method / path** | `GET /api/sales/orders/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — array of `{ "id", "total_amount", "created_at" }` (newest first) |

#### D3 — Order detail

| | |
|--|--|
| **Method / path** | `GET /api/sales/orders/<pk>/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "id", "total_amount", "created_at", "items": [ { "product": string, "quantity": int, "price": decimal } ] }` |
| **Errors** | `404` |

#### D4 — Invoice (JSON)

| | |
|--|--|
| **Method / path** | `GET /api/sales/orders/<pk>/invoice/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "invoice_id": "INV-<id>", "date": <datetime>, "items": [ { "product", "quantity", "unit_price", "subtotal" } ], "total_amount": decimal }` |
| **Errors** | `404` |

### Endpoints (public API key — external / partner)

#### D5 — Create order (public)

| | |
|--|--|
| **Method / path** | `POST /api/sales/public/orders/` |
| **Auth** | Header `X-API-KEY: <key>` **only** |
| **Body** | Same JSON array as D1 |
| **Success** | `201` — `{ "message": "Order created", "order_id": int }` |
| **Errors** | `401` — missing tenant context, missing key, or key inactive; `403` — key has `can_create_order: false` **or** tenant subscription expired (`{ "error": "Subscription expired" }`); `429` — rate limit (IP or key); `400` business/validation |

**Rate limits (middleware):** Roughly **100 requests/minute per IP** and **100 requests/minute per API key** on this path (implementation detail; tune with backend).

---

## Feature group E — Integrations (API keys & webhooks)

**Product goal:** Tenant admins generate API keys for integrations, list/deactivate keys, register webhook URLs for events (e.g. `order.created`).

### Suggested pages

| Page | Purpose |
|------|---------|
| API keys | List keys, create with label/name, deactivate. |
| Webhooks | Add destination URL + event type. |

### API key object (typical)

| Field | Type | Notes |
|-------|------|--------|
| `id` | number | |
| `name` | string | Label |
| `key` | string | UUID string; returned on create and **also exposed in list** in current API—treat as secret in UI (mask in tables). |
| `is_active` | boolean | |
| `created_at` | datetime | |

**Create body:** `{ "name": string }` — `can_create_order` is **not** in serializer; backend defaults apply unless extended.

### Endpoints

#### E1 — List API keys

| | |
|--|--|
| **Method / path** | `GET /api/integrations/keys/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — array of API key objects |

#### E2 — Create API key

| | |
|--|--|
| **Method / path** | `POST /api/integrations/keys/create/` |
| **Auth** | Bearer JWT |
| **Body** | `{ "name": string }` |
| **Success** | `201` — API key object **including plaintext `key`** |

**UI:** Show “copy once” modal; warn that key cannot be retrieved later if backend is changed to hide it.

#### E3 — Deactivate API key

| | |
|--|--|
| **Method / path** | `POST /api/integrations/keys/<pk>/deactivate/` |
| **Auth** | Bearer JWT |
| **Body** | Optional empty `{}` |
| **Success** | `200` — `{ "message": "API key deactivated" }` |
| **Errors** | `404` |

#### E4 — Create webhook

| | |
|--|--|
| **Method / path** | `POST /api/integrations/webhooks/create/` |
| **Auth** | Bearer JWT |
| **Body** | `{ "url": string, "event": string }` |
| **Success** | `200` — `{ "message": "Webhook created" }` |

**Allowed `event` values (model):** `order.created`, `order.updated` (backend validates loosely in view—confirm payloads with backend).

**UI:** URL validation, HTTPS enforcement policy, retry behavior is server-side (`FailedWebhook`, management commands).

---

## Feature group F — Automation rules

**Product goal:** When an event occurs (currently **`order.created` only**), run an action: **send SMS** or **send email** using payload fields from the automation pipeline.

### Suggested pages

| Page | Purpose |
|------|---------|
| Rules list | Show event + action + active flag. |
| Create rule | Pick `event_type` + `action`. |
| Edit rule | Toggle `is_active` or change fields if allowed. |
| Delete rule | Remove rule. |

### Rule object

| Field | Type | Constraints |
|-------|------|----------------|
| `id` | number | Read-only |
| `event_type` | string | **Only** `order.created` accepted by serializer |
| `action` | string | `send_sms` \| `send_email` |
| `is_active` | boolean | Default true |

**Uniqueness:** One rule per `(tenant, event_type, action)` combination.

### Endpoints

#### F1 — List rules

| | |
|--|--|
| **Method / path** | `GET /api/automation/rules/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — array of rules |

#### F2 — Create rule

| | |
|--|--|
| **Method / path** | `POST /api/automation/rules/create/` |
| **Auth** | Bearer JWT |
| **Body** | `{ "event_type": "order.created", "action": "send_email" \| "send_sms", "is_active": true }` |
| **Success** | `201` — rule object |
| **Errors** | `400` — duplicate rule or unsupported `event_type` |

#### F3 — Update rule

| | |
|--|--|
| **Method / path** | `PUT /api/automation/rules/<pk>/` |
| **Auth** | Bearer JWT |
| **Body** | Partial fields |
| **Success** | `200` — updated rule |
| **Errors** | `404` / `400` |

#### F4 — Delete rule

| | |
|--|--|
| **Method / path** | `DELETE /api/automation/rules/<pk>/delete/` |
| **Auth** | Bearer JWT |
| **Success** | `204` — **note:** current backend may still attach a JSON body; prefer handling empty body |
| **Errors** | `404` |

### Payload expectations (for UX / documentation)

When `order.created` fires, server payload includes at least: `order_id`, `total_amount`, `email` (tenant `owner_email`), `phone` (tenant `phone_number`). SMS action uses `phone` from payload; email action uses `email`. Ensure tenant profile has these filled for rules to be useful.

---

## Feature group G — Analytics & reporting

**Product goal:** Dashboard KPIs and charts for the tenant.

### Suggested pages

| Page | Purpose |
|------|---------|
| Dashboard home | KPI cards + link-outs. |
| Sales report | Tabular or simple series from `sales-report`. |
| Top products | Leaderboard. |
| Profit | Single KPI. |
| Growth | Today vs yesterday + %. |
| Sales chart | Labels + values for line/bar chart. |

### Endpoints

#### G1 — Dashboard summary

| | |
|--|--|
| **Method / path** | `GET /api/analytics/dashboard/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "total_sales", "total_orders", "today_sales", "weekly_sales", "low_stock_products" }` (numeric aggregates; `weekly_sales` = last 7 days including today—confirm with product) |

#### G2 — Sales over time (raw series)

| | |
|--|--|
| **Method / path** | `GET /api/analytics/sales-report/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — array of `{ "date": "<date>", "total": decimal }` ordered by date |

#### G3 — Top products

| | |
|--|--|
| **Method / path** | `GET /api/analytics/top-products/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — array (max 5) of `{ "product__name": string, "total_sold": int }` |

**UI:** Map `product__name` → display column “Product name”.

#### G4 — Profit estimate

| | |
|--|--|
| **Method / path** | `GET /api/analytics/profit/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "total_profit": decimal }` (sum over order lines of `(sold_price - cost_price) * qty`) |

#### G5 — Sales growth

| | |
|--|--|
| **Method / path** | `GET /api/analytics/growth/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "today_sales", "yesterday_sales", "growth_percent": number }` |

#### G6 — Sales chart (frontend-friendly)

| | |
|--|--|
| **Method / path** | `GET /api/analytics/sales-chart/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — `{ "labels": string[], "data": decimal[] }` — parallel arrays by index |

---

## Feature group H — Billing & subscriptions (SSLCommerz)

**Product goal:** Show **active subscription plans**, start a **paid checkout** for the current tenant, and show **payment history**. Renewals replace the previous active subscription on successful payment. Currency for the gateway session is **BDT** (see `apps.billing.sslcommerz`).

### Suggested pages

| Page | Purpose |
|------|---------|
| Plans & subscribe | List plans; user picks one → create payment → redirect browser to `gateway_url`. |
| Payment return | After gateway redirect, user lands on frontend routes you control; optionally poll payment history or re-login for updated `subscription`. |
| Billing history | Table of past payments (status, amount, plan, date). |

**UI:** If core ERP calls return **`403` `Subscription expired`**, deep-link to billing/plans.

### Plan object (list)

| Field | Type | Notes |
|-------|------|--------|
| `id` | number | |
| `name` | string | |
| `price` | decimal | Charged amount for this plan |
| `duration_days` | number | Subscription length after successful payment |
| `max_users` | number | Plan limit (informational for UI) |

### Endpoints (JWT; subscription **not** required)

#### H1 — List active subscription plans

| | |
|--|--|
| **Method / path** | `GET /api/billing/plans/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — JSON array of plan objects |

#### H2 — Create payment session (SSLCommerz)

| | |
|--|--|
| **Method / path** | `POST /api/billing/payment/create/` |
| **Auth** | Bearer JWT |
| **Body** | `{ "plan_id": number }` |
| **Success** | `200` — `{ "payment_id", "transaction_id", "gateway_url", "gateway_response" }` — open **`gateway_url`** in the browser (or redirect) for checkout. `gateway_response` is the raw SSLCommerz session payload (useful for debugging). |
| **Errors** | `404` — `{ "error": "Plan not found" }` if `plan_id` invalid or inactive |

**Flow:** Server creates a `Payment` row (`pending`), calls SSLCommerz `createSession`, stores the response. Success/fail/cancel URLs point back to **`/api/billing/payment/success/`**, **`failed/`**, **`cancel/`** on the **same host** as the create request—use a publicly reachable base URL when testing with the real gateway.

#### H3 — Payment history

| | |
|--|--|
| **Method / path** | `GET /api/billing/payments/` |
| **Auth** | Bearer JWT |
| **Success** | `200` — array of `{ "id", "plan" (name string), "transaction_id", "amount", "status" ("pending"\|"success"\|"failed"), "created_at" }` newest first |

### Gateway callbacks (not for SPA — SSLCommerz server / redirect)

These accept **unauthenticated** `POST` (gateway posts form-like data; DRF parses `request.data`). The SPA does not call them.

| Path | Role |
|------|------|
| `POST /api/billing/payment/success/` | Marks payment **success**, merges payload into `gateway_response`, runs **`activate_subscription`** (expires prior active subs for tenant, creates new active subscription, sets tenant `status` **active**). Body includes **`tran_id`** matching `transaction_id`. |
| `POST /api/billing/payment/failed/` | Marks payment **failed**. |
| `POST /api/billing/payment/cancel/` | Marks payment **failed** (cancelled). |

**Success response:** `{ "message": "Payment successful", "transaction_id": "..." }` (and analogous messages for fail/cancel).

---

## Feature group I — Django admin (out of SPA scope)

| Path | Purpose |
|------|---------|
| `GET/POST /admin/...` | Django admin UI for operators; not part of the JWT SPA unless you embed it (unusual). |

**Operators** use admin to manage `SubscriptionPlan` rows (and other models) unless you build an internal console.

---

## Quick reference — all REST paths

| Group | Method | Path |
|-------|--------|------|
| **A Auth** | POST | `/api/auth/register/` |
| | POST | `/api/auth/login/` |
| | GET | `/api/auth/verify-email/` |
| | POST | `/api/auth/resend-verification/` |
| | POST | `/api/auth/forgot-password/` |
| | POST | `/api/auth/reset-password/` |
| | GET | `/api/auth/test-tenant/` |
| **B Tenant** | GET | `/api/tenants/profile/` |
| | PUT | `/api/tenants/profile/update/` |
| | POST | `/api/tenants/delete-request/` |
| **C Inventory** | GET | `/api/inventory/products/` |
| | POST | `/api/inventory/products/create/` |
| | GET | `/api/inventory/products/<pk>/` |
| | PUT | `/api/inventory/products/<pk>/update/` |
| | DELETE | `/api/inventory/products/<pk>/delete/` |
| **D Sales** | POST | `/api/sales/orders/create/` |
| | GET | `/api/sales/orders/` |
| | GET | `/api/sales/orders/<pk>/` |
| | GET | `/api/sales/orders/<pk>/invoice/` |
| | POST | `/api/sales/public/orders/` |
| **E Integrations** | GET | `/api/integrations/keys/` |
| | POST | `/api/integrations/keys/create/` |
| | POST | `/api/integrations/keys/<pk>/deactivate/` |
| | POST | `/api/integrations/webhooks/create/` |
| **F Automation** | GET | `/api/automation/rules/` |
| | POST | `/api/automation/rules/create/` |
| | PUT | `/api/automation/rules/<pk>/` |
| | DELETE | `/api/automation/rules/<pk>/delete/` |
| **G Analytics** | GET | `/api/analytics/dashboard/` |
| | GET | `/api/analytics/sales-report/` |
| | GET | `/api/analytics/top-products/` |
| | GET | `/api/analytics/profit/` |
| | GET | `/api/analytics/growth/` |
| | GET | `/api/analytics/sales-chart/` |
| **H Billing** | GET | `/api/billing/plans/` |
| | POST | `/api/billing/payment/create/` |
| | GET | `/api/billing/payments/` |
| | POST | `/api/billing/payment/success/` |
| | POST | `/api/billing/payment/failed/` |
| | POST | `/api/billing/payment/cancel/` |

---

## Suggested information architecture (SPA routes)

| Route | Feature group |
|-------|----------------|
| `/register`, `/login`, `/verify-email`, `/forgot-password`, `/reset-password` | A |
| `/settings/company` | B |
| `/inventory/products`, `/inventory/products/new`, `/inventory/products/:id` | C |
| `/sales/orders`, `/sales/orders/new`, `/sales/orders/:id`, `/sales/orders/:id/invoice` | D |
| `/settings/integrations/api-keys`, `/settings/integrations/webhooks` | E |
| `/automation/rules` | F |
| `/analytics`, `/analytics/sales`, `/analytics/products`, `/analytics/profit` | G |
| `/billing/plans`, `/billing/history` (and optional return/thank-you routes after gateway) | H |

Adjust naming to your design system; routes are **frontend-only**—only the API paths in the table must match the backend.

---

## Out of scope in current backend (do not promise in UI without API work)

- Category CRUD, HR module, in-app notifications list, JWT refresh endpoint, file upload flow for tenant logo (verify multipart support), role-based UI per `User.role` (not enforced per-endpoint in this codebase).

---

*Document generated from repository URLconf and views as of the project snapshot; after backend changes, regenerate or diff this file.*
