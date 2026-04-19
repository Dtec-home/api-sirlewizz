
# Audit Report

## Backend (/home/md/Tweny5/Lewizzz)

Status: Skeleton only — nothing is implemented.

| Area | Expected (Design Doc) | Actual |
|---|---|---|
| products/models.py | Product, Category, Variant, Size, Color | Empty |
| inventory/models.py | StockEntry, StockAlert | Empty |
| orders/models.py | Order, OrderItem, OrderStatus | Empty |
| payments/models.py | MpesaTransaction | Empty |
| users/models.py | Staff/Admin user | Empty |
| schema/ | Strawberry types, queries, mutations | All empty files |
| config/settings.py | CORS, Strawberry, custom apps registered | Missing — apps not in INSTALLED_APPS,
no CORS, no Strawberry |
| config/urls.py | GraphQL endpoint at /graphql | Only Django admin |
| payments/daraja.py | STK Push, token auth, callback | File doesn't exist |
| orders/services.py | Order creation logic | File doesn't exist |
| inventory/signals.py | Low stock auto-alerts | File doesn't exist |
| Settings split | base.py, development.py, production.py | Single flat settings.py |

Critical gaps: The backend is a django-admin startproject output with empty app files. Zero business
logic exists.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Frontend (menswear-e-commerce-store/)

Status: Well-scaffolded UI shell — data layer is all mock, no real backend connection.

| Area | Expected | Actual |
|---|---|---|
| All pages | ✅ All routes exist | ✅ |
| All storefront components | ✅ All present | ✅ |
| Dashboard components | InventoryTable, StockAlertBanner missing | Only Sidebar, StatsCard, SalesChart
|
| components/animations/ | PageTransition, StaggerReveal, HeroText | ❌ Directory doesn't exist |
| lib/apollo/queries/orders.ts | Required | ❌ Missing |
| lib/apollo/queries/inventory.ts | Required | ❌ Missing |
| useProducts hooks | Real Apollo queries | Mock data, TODO comments |
| usePayment | Calls real STK Push | Posts to webhook (wrong — should call mutation) |
| lib/mpesa/daraja.ts | STK Push active | Commented out, placeholder response |
| app/api/mpesa/webhook/route.ts | Validates callback, updates DB | Placeholder only |
| Apollo Client | Configured with ApolloProvider | Client exists but no ApolloProvider wrapping the app
|
| GSAP animations | All motion language implemented | Zero GSAP code, only comments |
| Product detail page | Image gallery, size/color selector, sticky CTA | Scaffolded |
| Checkout confirmation | Order confirmed screen | Scaffolded |
| lib/gsap/config.ts | Centralized GSAP config | ❌ Missing |

Critical gap: ApolloProvider is never mounted — Apollo queries will fail even when the backend is
ready.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# Sprint Breakdown

## Sprint 1 — Backend Foundation (3–4 days)
Goal: Working Django API with data models and GraphQL endpoint

1. Register all apps in INSTALLED_APPS, add corsheaders, strawberry_django
2. Split settings into base.py / development.py / production.py
3. Write products/models.py — Category, Product, Variant (size + color + stock per variant)
4. Write inventory/models.py — StockEntry (in/out log), StockAlert
5. Write orders/models.py — Order, OrderItem, OrderStatus enum
6. Write payments/models.py — MpesaTransaction
7. Write users/models.py — extend AbstractUser for staff roles
8. Run migrations, register all models in admin.py, seed categories + sample products
9. Wire Strawberry schema: schema/types.py → schema/queries.py → mount at /graphql in urls.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Sprint 2 — GraphQL API (2–3 days)
Goal: All queries and mutations the frontend needs

1. Queries: products, product(slug), categories, productsByCategory, inventoryItems(lowStock),
orderPaymentStatus(orderId), salesReport(from, to)
2. Mutations: createOrder, initiateMpesaPayment, updateStock, upsertProduct
3. orders/services.py — order creation logic (validate stock, create Order + OrderItems, decrement
stock)
4. inventory/signals.py — post-save signal on StockEntry to auto-create StockAlert when below threshold
5. CORS configured to allow localhost:3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Sprint 3 — M-PESA Integration (2–3 days)
Goal: Real STK Push flow end-to-end

1. payments/daraja.py — token auth, STK Push, callback validation
2. payments/views.py — Daraja webhook endpoint (validates signature, updates MpesaTransaction + Order
status)
3. Wire webhook URL in config/urls.py
4. Front: uncomment STK Push in lib/mpesa/daraja.ts, add real credentials to .env
5. Front: usePayment — replace axios-to-webhook hack with initiateMpesaPayment GraphQL mutation
6. Front: app/api/mpesa/webhook/route.ts — forward Daraja callback to Django (or remove and point
Daraja directly at Django)
7. Front: implement Apollo polling on orderPaymentStatus in checkout page

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Sprint 4 — Frontend–Backend Connection (2 days)
Goal: Replace all mock data with live Apollo queries

1. Add ApolloProvider to app/layout.tsx (this is the single most critical fix)
2. Replace mock returns in useProducts, useProductBySlug, useCategories, useProductsByCategory with
real useQuery calls
3. Add lib/apollo/queries/orders.ts and lib/apollo/queries/inventory.ts
4. Dashboard pages: wire StatsCard and SalesChart to real salesReport query
5. Inventory page: wire table to real inventoryItems query, implement edit/delete via upsertProduct
mutation
6. Stock page: wire to real StockEntry log
7. Add skeleton loaders (already have the component) for Apollo loading states

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Sprint 5 — Missing Components & Dashboard Features (2 days)
Goal: Complete the component inventory per the design doc

1. components/dashboard/InventoryTable.tsx — full CRUD table with shadcn Sheet for inline editing
2. components/dashboard/StockAlertBanner.tsx — banner for low-stock alerts
3. Dashboard inventory: CSV bulk upload
4. Dashboard sales: date range picker + export to CSV
5. Product detail page: image gallery with zoom, sticky mobile add-to-cart bar
6. checkout/confirmation/page.tsx — wire to real order data

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Sprint 6 — GSAP Animations (2 days)
Goal: Implement the full motion language from the design doc

1. lib/gsap/config.ts — centralized easing/duration config
2. components/animations/HeroText.tsx — SplitText character-by-character
3. components/animations/StaggerReveal.tsx — ScrollTrigger product card reveal
4. components/animations/PageTransition.tsx — horizontal slide + fade
5. Dashboard StatsCard — count-up on mount
6. CartDrawer — slide-in from right
7. Navbar link underline reveal on hover
8. Checkout success screen animation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Sprint 7 — Polish & Production Readiness (2 days)
Goal: Ship-ready

1. Replace all next/image usages with proper width/height or fill + sizes
2. Add Open Graph metadata to product pages
3. Enable ISR (revalidate) on product and category pages
4. Add Zod validation to all form inputs (checkout already done, verify others)
5. Auth: protect /dashboard routes (middleware or layout guard)
6. Production settings: PostgreSQL config, DEBUG=False, ALLOWED_HOSTS, SECRET_KEY from env
7. Celery worker setup for async M-PESA callbacks
8. E2E smoke test: shop → add to cart → checkout → M-PESA → confirmation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## Priority Order Summary

Sprint 1 → Sprint 2 → Sprint 3 (parallel with Sprint 4) → Sprint 5 → Sprint 6 → Sprint 7


Sprints 3 and 4 can run in parallel once Sprint 2 is done — one person wires M-PESA while the other
connects Apollo. The single most impactful fix you can do right now before anything else: add
ApolloProvider to app/layout.tsx — without it, every Apollo query will silently fail the moment you
switch from mock data.