# 🛒 Shop

This is the backend for a fully dockerized e-commerce platform built with Django.  
It supports JWT authentication, product and basket management, Elasticsearch-powered search, and background tasks with Celery.

---

## 🚀 Features

- 🔐 **Custom registration** and authentication using `simplejwt` (no djoser)
- 👤 User profile and password change endpoints
- 🛒 Basket functionality: add/remove/list items
- 🛍 Product catalog with categories and filters
- 🔍 Full-text search with Elasticsearch (supports stemming & fuzzy matching)
- ⚙️ Asynchronous email sending with Celery + Redis
- 🧠 Smart caching with Redis + auto-invalidation on changes
- 🧪 Endpoint testing with Pytest
- 🐋 Dockerized with multi-container architecture
- 📄 Interactive API documentation at `/api/swagger/`

---

## 📦 Tech Stack

| Component        | Tool/Library                          |
|------------------|----------------------------------------|
| **Backend**      | Django 5.1, DRF                        |
| **Auth**         | SimpleJWT (custom registration logic) |
| **Database**     | PostgreSQL                            |
| **Search**       | Elasticsearch                         |
| **Async Tasks**  | Celery + Redis                        |
| **Caching**      | Redis + Django cache framework        |
| **Testing**      | Pytest + pytest-django                |
| **Docs**         | drf-yasg (Swagger UI)                 |
| **Deployment**   | Docker, Docker Compose, Nginx, Gunicorn |
| **Media/Static** | Pillow, nginx                         |

---

## 🔐 Authentication Flow

- **JWT-based auth** using `djangorestframework-simplejwt`
- Custom registration endpoint (`/auth/register/`)
- Token endpoints:
  - `POST /auth/login/` – authenticate and get access/refresh tokens
  - `POST /token/refresh/` – get new access token
  - `POST /token/verify/` – verify a token’s validity

> Note: Registration, login, password reset, and email confirmation are implemented manually — **`djoser` is not used**.

---

## 📂 API Overview

The API follows RESTful principles, organized by module:

| Module        | Endpoints                                      |
|---------------|------------------------------------------------|
| `auth/`       | Login, logout, register, reset password        |
| `profile/`    | Change password, get current user info         |
| `shop/`       | Products, categories, filters, basket actions  |
| `token/`      | Refresh and verify JWT tokens                  |
| `user/`       | User CRUD endpoints                            |

Explore the full API at:  
📚 `http://127.0.0.1/api/swagger/`

---

## 🐳 Getting Started with Docker

> **Requirements**: Docker & Docker Compose

```bash
git clone https://github.com/alisovskij/shop.git
cd shop
docker-compose up --build

