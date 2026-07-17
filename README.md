# JWT Authentication API

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)

A RESTful authentication API built with **FastAPI** that demonstrates secure user authentication using **JWT (JSON Web Tokens)**, password hashing with **bcrypt**, and database persistence with **SQLAlchemy**.

This project was built to better understand authentication, password security, and how cryptographic concepts such as hashing and digital signatures are applied in modern backend development.

---

# Features

- User registration
- Secure user login
- JWT access token generation
- Password hashing using bcrypt
- SQLite database with SQLAlchemy ORM
- Protected API endpoints
- Automated tests with pytest
- Docker Compose support

---

# Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT |
| Security | bcrypt, passlib |
| Testing | pytest |
| Containerization | Docker Compose |

---

# Project Structure

```text
AUTH-API/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── auth.py          # Authentication routes
│   ├── security.py      # Password hashing & JWT utilities
│   ├── database.py      # SQLAlchemy configuration
│   ├── models.py        # Database models
│   └── schemas.py       # Pydantic request/response models
│
├── tests/
│   └── test_auth.py
│
├── docker-compose.yml
└── README.md
```

---

# Quick Start

## Prerequisites

- Python 3.11+
- Docker Desktop (optional)

## Installation

Clone the repository.

```bash
git clone https://github.com/lithasz/auth-api.git
cd AUTH-API
```

Create a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Run the application.

```bash
uvicorn app.main:app --reload
```

---

# API Documentation

FastAPI automatically generates interactive API documentation.

| Service | URL |
|---------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

# Architecture

```text
                    ┌──────────────┐
                    │    Client    │
                    └──────┬───────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │      FastAPI API        │
              └──────────┬──────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
         ▼                                ▼
 ┌──────────────────┐          ┌──────────────────┐
 │ Authentication   │          │    SQLite DB     │
 │  JWT + bcrypt    │          │   SQLAlchemy     │
 └──────────────────┘          └──────────────────┘
```

The API consists of three main components:

- **FastAPI** provides the REST API and request validation.
- **Security Layer** handles password hashing, JWT creation, verification, and protected routes.
- **SQLite** stores user accounts through SQLAlchemy ORM.

---

# API Endpoints
- POST | `/register` | Register a new user |
- POST | `/login` | Authenticate a user and receive a JWT |
- GET | `/me` *(or protected endpoint)* | Access a protected resource using a valid JWT |

> Endpoint names may vary depending on your implementation.

---

# Authentication Flow

The authentication process follows these steps:

1. A user registers with a username and password.
2. The password is hashed using **bcrypt** before being stored.
3. During login, the submitted password is verified against the stored hash.
4. If authentication succeeds, the server generates a signed **JWT access token**.
5. The client includes this token in the `Authorization` header for future requests.
6. Protected endpoints verify the JWT before granting access.

```text
Client
   │
   │ Register/Login
   ▼
FastAPI
   │
   ├── Hash password (bcrypt)
   ├── Verify credentials
   └── Generate JWT
          │
          ▼
      Access Token
          │
          ▼
Client stores token
          │
Authorization: Bearer <token>
          │
          ▼
Protected Endpoint
```

---

# Security

This project implements several authentication best practices:

- Passwords are hashed using **bcrypt**
- Plain-text passwords are never stored
- JWTs are digitally signed to prevent tampering
- Protected endpoints require token verification before access is granted

One important concept learned while building this project is that **JWTs are signed, not encrypted**. The payload can be decoded by anyone, but the signature allows the server to verify that the token has not been modified.

Similarly, password hashing is intentionally **one-way**—the original password cannot be recovered from the stored hash.

---

# Example Usage

Register a user.

```http
POST /register
```

```json
{
  "username": "alice",
  "password": "password123"
}
```

Login.

```http
POST /login
```

Response:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

Access a protected endpoint.

```http
Authorization: Bearer <jwt_token>
```

---

# Testing

Run the automated tests.

```bash
pytest
```

The tests verify:

- User registration
- Successful login
- Invalid credentials
- JWT authentication
- Protected route access

---

# Future Improvements

- Refresh tokens
- Role-Based Access Control (RBAC)
- Email verification
- Password reset functionality
- PostgreSQL support
- Docker deployment
- CI/CD with GitHub Actions

---

# What I Learned

Building this project helped me understand:

- JWT authentication workflows
- Password hashing with bcrypt
- The difference between hashing, encryption, and digital signatures
- Protecting API endpoints with bearer tokens
- FastAPI dependency injection
- Database integration using SQLAlchemy
- Secure backend authentication practices

---

## License

This project was built for learning and portfolio purposes.
