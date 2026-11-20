# My Bookstore App

[![Build Status](https://github.com/matrosovanastya19/hillel_homework/actions/workflows/django.yml/badge.svg)](https://github.com/matrosovanastya19/hillel_homework/actions)
![Coverage](http://localhost:63342/hillel_homework/bookstore/htmlcov/index.html?_ijt=5lqfn6e3pfdoa5bbqnatdhb2oi&_ij_reload=RELOAD_ON_SAVE)
# Bookstore & Warehouse Microservices (Hillel Final Project)

Two independent Django microservices orchestrated via Docker Compose and exposed through a single NGINX reverse proxy.

## Architecture

- **Project A — Bookstore (`bookstore/`)**: Online bookstore service (Django, DRF, PostgreSQL, Redis DB 0–1, Celery, Stripe, Gunicorn).
- **Project B — Warehouse (`warehouse/`)**: Inventory and stock reservation service (Django, DRF, JWT, Swagger/OpenAPI, PostgreSQL, Redis DB 2–3, Celery, Gunicorn).
- **Inter-Service Communication**: REST API calls from `Bookstore` (`WarehouseClient`) to `Warehouse` authenticated via `X-Service-Token`, atomic stock reservation on checkout, and Celery tasks for low-stock alerts / stock release.
- **NGINX (`nginx/default.conf`)**: Single entry point on port `8000`.

## Environment Configuration

Before starting the containers, create `.env` files in both service directories. Make sure `WAREHOUSE_API_TOKEN` has the **exact same value** in both files.

### 1. `bookstore/.env`

```env
SECRET_KEY=your-bookstore-secret-key
DEBUG=True

DB_NAME=bookstore_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

WAREHOUSE_SERVICE_URL=http://warehouse-web:8001
WAREHOUSE_API_TOKEN=super-secret-service-token

STRIPE_PUBLIC_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
SENTRY_DSN=