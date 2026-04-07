# Agribuddy Authentication Backend

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:

   ```bash
   python main.py
   ```

The app auto-creates the SQLite database and seeds:
- administrator: `admin@agribuddy.com` / `Admin@123`
- farmer: `farmer@agribuddy.com` / `Farmer@123`

## Authentication API

Base URL: `http://127.0.0.1:5000`

### 1) Login

**POST** `/api/login`

Request body:

```json
{
  "email": "admin@agribuddy.com",
  "password": "Admin@123",
  "role": "administrator"
}
```

Success response returns `access_token`.

### 2) Register Farmer

**POST** `/api/register`

Request body:

```json
{
  "email": "newfarmer@agribuddy.com",
  "password": "Farmer@123"
}
```

Creates a new user with `role = farmer`.

### 3) Current User (Token Check)

**GET** `/api/me`

Header:

```http
Authorization: Bearer <access_token>
```

### 4) Admin: List Users

**GET** `/api/admin/users`

Header:

```http
Authorization: Bearer <admin_access_token>
```

### 5) Admin: Create User

**POST** `/api/admin/users`

Header:

```http
Authorization: Bearer <admin_access_token>
```

Request body:

```json
{
  "email": "staff@agribuddy.com",
  "password": "StrongPass123",
  "role": "farmer"
}
```

`role` must be `administrator` or `farmer`.

### 6) Farmer: Profile

**GET** `/api/farmer/profile`

Header:

```http
Authorization: Bearer <farmer_access_token>
```

## Example cURL Flow

```bash
# Login as admin
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agribuddy.com","password":"Admin@123","role":"administrator"}'
```

Copy `access_token` from response and use it in protected routes.
