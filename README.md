# Airport API

API service for airport management written with Django REST Framework

---

## Installation (Local)

**Requirements:**
- Python 3.11+
- PostgreSQL
- Redis (optional, if used for caching)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/d-stegantsev/py-api-airport
cd py-api-airport
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a file named `.env` in the project root. You can use `.env.sample` as a template:
```bash
cp .env.sample .env
```
Then edit `.env` and set the following values:
- `POSTGRES_DB` — your database name
- `POSTGRES_USER` — your database user
- `POSTGRES_PASSWORD` — your database password
- `POSTGRES_HOST` — usually `localhost` for local dev
- `POSTGRES_PORT` — usually `5432`
- `REDIS_HOST` — if using Redis (e.g., `localhost` or service name in docker)
- `DJANGO_SECRET_KEY` — any strong secret key (use [https://djecrety.ir/](https://djecrety.ir/) or python secrets)

### 5. Run migrations & collectstatic
```bash
python manage.py migrate
python manage.py collectstatic --no-input
```

### 6. Run the development server
```bash
python manage.py runserver
```

---

## Installation & Run with Docker

**Requirements:**
- Docker
- Docker Compose

### 1. Build and run services
```bash
docker-compose build
docker-compose up
```

---

## Getting access

- Register user via `/api/v1/accounts/signup/`
- Obtain JWT token via `/api/v1/accounts/token/`

### Demo users

You can load demo users with the fixture:
```bash
python manage.py loaddata accounts/fixtures/users.json
```

Demo credentials:
- **User:**  
  email: user@example.com  
  password: password123
- **Admin:**  
  email: admin@example.com  
  password: password123

### Demo data

You can load demo data with the fixture:
```bash
python manage.py loaddata airport/fixtures/test_data.json
```

---

## Useful commands

- Run tests:
  ```bash
  docker-compose exec app pytest
  ```
- Run tests for a specific app:
  ```bash
  docker-compose exec app pytest airport/
  ```
  ```bash
  docker-compose exec app pytest accounts/
  ```
  