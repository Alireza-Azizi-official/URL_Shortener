# FastAPI URL Shortener

A high-performance URL shortener built with **FastAPI**, **PostgreSQL**, and **Redis**. Features a modern, minimalistic dark-themed web interface for easy URL shortening and statistics tracking.

---

## **Features**

* **Modern Web Interface** - Beautiful, minimalistic dark-themed frontend
* Shorten URLs and generate unique short codes.
* Asynchronous CRUD operations using SQLAlchemy with PostgreSQL.
* Visit tracking with automatic incrementing of visit counts.
* Redis caching for fast URL resolution and visit count tracking.
* Alembic migrations for database schema management.
* Middleware for logging all visits.
* Configurable via environment variables.
* Rate limiter to control and manage the requests number.
* Pagination to control the Read requests and db heat control

---

## **Tech Stack**

* **Python 3.12**
* **FastAPI** – Web framework
* **SQLAlchemy (async)** – ORM for PostgreSQL
* **PostgreSQL** – Primary database
* **Redis** – Caching layer for URLs and visit counts
* **Alembic** – Database migrations
* **Uvicorn** – ASGI server
* **HTML/CSS/JavaScript** – Modern frontend interface

---

## **Project Structure**

```
URL_Shortener/
├── url_shortener/
│   └── app/
│       ├── config.py              # Application settings with Pydantic
│       ├── db.py                  # Database engine & session setup
│       ├── rate_limiter_redis.py  # A specific redis client for rate limiter
│       ├── log_config.py          # Logger configuration
│       ├── middleware.py          # Visit logging middleware
│       ├── models.py              # SQLAlchemy models (URL, VisitLog)
│       ├── router.py              # API routes
│       ├── schemas.py             # Pydantic models
│       ├── main.py                # Core of the app
│       ├── utils.py               # Base62 encoding/decoding
│       ├── shortener_service.py   # API's logic
│       └── redis_conf.py          # Redis and other dependency initialization
├── static/                        # Frontend files
│   ├── index.html                 # Main frontend page
│   ├── css/
│   │   └── style.css              # Dark theme styles
│   └── js/
│       └── app.js                 # Frontend JavaScript
├── migrations/                    # Alembic migration scripts
├── .env                           # Environment variables (create from env.example)
├── env.example                    # Environment variables template
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
└── docker-compose.yml             # Docker Compose configuration
```

---

## **Setup**

### **1. Clone the repository**

```bash
git clone <https://github.com/Alireza-Azizi-official/URL_Shortener>
cd <URL_Shortener>
```

### **2. Create a virtual environment**

```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Set environment variables**

Copy the example environment file and update it:

```bash
# On Linux/Mac
cp env.example .env

# On Windows
copy env.example .env
```

Edit `.env` and set the following variables:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/url_shortener
REDIS_URL=redis://localhost:6379/0
BASE_URL=http://127.0.0.1:8000
POSTGRES_DB=url_shortener
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

* `DATABASE_URL`: PostgreSQL async connection URL.
* `REDIS_URL`: Redis server URL.
* `BASE_URL`: Base URL for short URLs.
* `POSTGRES_DB`: PostgreSQL database name.
* `POSTGRES_USER`: PostgreSQL username.
* `POSTGRES_PASSWORD`: PostgreSQL password.

---

### **5. Run Alembic migrations**

```bash
alembic upgrade head
```

> This ensures your database tables (`urls` and `visit_logs`) are created.

---

## **Running the application**

### **Option 1: Using Docker Compose (Recommended)**

The easiest way to run the application:

```bash
docker-compose up --build
```

This will start:
- PostgreSQL database
- Redis cache
- FastAPI application with frontend

The web interface will be available at `http://localhost:8000`

### **Option 2: Manual Setup**

1. Make sure PostgreSQL and Redis are running locally
2. Run Alembic migrations:
   ```bash
   cd url_shortener
   alembic upgrade head
   ```
3. Start the application:
   ```bash
   uvicorn url_shortener.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

* The web interface will be available at `http://127.0.0.1:8000`
* The API documentation will be available at `http://127.0.0.1:8000/docs`

---

## **Web Interface**

The application includes a modern, minimalistic dark-themed web interface accessible at the root URL (`/`). Features include:

* **URL Shortening** - Enter any URL to get a shortened version
* **Copy to Clipboard** - One-click copy of shortened URLs
* **Statistics View** - View visit counts and creation date for shortened URLs
* **Responsive Design** - Works on desktop and mobile devices
* **Dark Theme** - Easy on the eyes with a modern dark color scheme

## **API Endpoints**

### **1. Shorten a URL**

* **POST** `/shorten`
* **Body:**

```json
{
    "url": "https://example.com"
}
```

* **Response:**

```json
{
    "short_code": "abc123",
    "short_url": "http://127.0.0.1:8000/abc123"
}
```

---

### **2. Redirect using short code**

* **GET** `/{short_code}`
* Redirects to the original URL.
* Automatically records visit in DB and Redis.

---

### **3. Get URL stats**

* **GET** `/stats/{short_code}`
* **Response:**

```json
{
    "short_code": "abc123",
    "original_url": "https://example.com",
    "created_at": "2025-12-04T12:34:56.789Z",
    "visits_count": 42
}
```

---

## **Caching & Redis**

* Redis stores:

  * `url:<short_code>` → original URL
  * `count:<short_code>` → visit count
* Cache is automatically updated on visit or URL creation.

---

## **Visit Logging Middleware**

* Automatically logs visits to:

  * Database (`visit_logs` table)
  * Redis (increment count)
* Skips documentation paths (`docs`, `openapi.json`, `redoc`) and static files (`/static`).

---

## **Database Models**

**URL Table**

| Column       | Type     | Description           |
| ------------ | -------- | --------------------- |
| id           | int      | Primary key           |
| original_url | string   | Original URL          |
| short_code   | string   | Unique short code     |
| created_at   | datetime | Timestamp of creation |
| visits_count | int      | Total visits          |

**VisitLog Table**

| Column     | Type     | Description               |
| ---------- | -------- | ------------------------- |
| id         | int      | Primary key               |
| url_id     | int      | FK to URL table           |
| timestamp  | datetime | Visit timestamp           |
| ip         | string   | Visitor IP                |
| user_agent | string   | User agent of the visitor |

---

## **Base62 Encoding**

* Generates short codes for URLs using numbers → `[0-9a-zA-Z]`.
* Ensures short, human-readable codes.

---

## **Logging**

* Logs all important events (DB queries, cache hits/misses, errors) using Python logging.
* Format: `[timestamp] [level][logger_name] message`.

---

## **Contributing**

1. Fork the repo.
2. Create a new feature branch.
3. Add migrations if DB schema changes.
4. Ensure tests pass.
5. Submit a pull request.

---

## **References**

* [FastAPI Docs](https://fastapi.tiangolo.com/)
* [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
* [Redis Python Docs](https://github.com/redis/redis-py)
* [Alembic Docs](https://alembic.sqlalchemy.org/)
