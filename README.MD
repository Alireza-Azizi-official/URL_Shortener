# FastAPI URL Shortener

A high-performance URL shortener built with **FastAPI**, **PostgreSQL**, **Redis**, and **Kafka**. Supports visit tracking, caching, and asynchronous database operations using SQLAlchemy.


![Image](diagram.png)

---

## **Features**

* Shorten URLs and generate unique short codes.
* Asynchronous CRUD operations using SQLAlchemy with PostgreSQL.
* Visit tracking with automatic incrementing of visit counts.
* Redis caching for fast URL resolution and visit count tracking.
* Kafka integration for publishing visit events asynchronously.
* Alembic migrations for database schema management.
* Middleware for logging all visits.
* Configurable via environment variables.

---

## **Tech Stack**

* **Python 3.10.11**
* **FastAPI** – Web framework
* **SQLAlchemy (async)** – ORM for PostgreSQL
* **PostgreSQL** – Primary database
* **Nginx** – Load Balancer
* **Redis** – Caching layer for URLs and visit counts
* **Kafka (optional)** – Event streaming for visits
* **Kafka Cluster**
* **Alembic** – Database migrations
* **Uvicorn** – ASGI server

---

## **Project Structure**

```
app/
├── config.py              # Application settings with Pydantic
├── db.py                  # Database engine & session setup
├── kafka_producer.py      # Kafka producer initialization and event publishing
├── kafka_consumer.py      # Kafka consumer initialization and event consumer
├── rate_limiter_redis.py  # A specific redis client for rate limiter
├── log_config.py          # Logger configuration
├── middleware.py          # Visit logging middleware
├── models.py              # SQLAlchemy models (URL, VisitLog)
├── router.py              # API routes
├── schemas.py             # Pydantic models
├── main.py                # core of the app
├── utils.py               # Base62 encoding/decoding
├── shortener_service.py   # API's logic
└── redis_conf.py          # Redis and other dependency initialization

alembic/                   # Alembic migration scripts
.env                       # Environment variables
main.py                    # FastAPI application entrypoint
requirements.txt           # Python dependencies
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

Create a `.env` file:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/url_shortener
REDIS_URL=redis://localhost:6379/0
BASE_URL=http://127.0.0.1:8000
KAFKA_ENABLED=False
KAFKA_BOOTSTRAP_SERVER=localhost:9092
KAFKA_VISIT_TOPIC=visit_events
```

* `DATABASE_URL`: PostgreSQL async connection URL.
* `REDIS_URL`: Redis server URL.
* `BASE_URL`: Base URL for short URLs.
* Kafka settings are optional.

---

### **5. Run Alembic migrations**

```bash
alembic upgrade head
```

> This ensures your database tables (`urls` and `visit_logs`) are created.

---

## **Running the application**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

* The API will be available at `http://127.0.0.1:8000`.

---

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
* Automatically records visit in DB and Redis, publishes Kafka event if enabled.

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

## **Kafka Integration (Optional)**

* Publishes visit events to a Kafka topic.
* Configurable via `.env`:

  * `KAFKA_ENABLED`
  * `KAFKA_BOOTSTRAP_SERVER`
  * `KAFKA_VISIT_TOPIC`

---

## **Visit Logging Middleware**

* Automatically logs visits to:

  * Database (`visit_logs` table)
  * Redis (increment count)
  * Kafka (event publishing)
* Skips documentation paths (`docs`, `openapi.json`, `redoc`).

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

* Logs all important events (DB queries, cache hits/misses, Kafka publishing, errors) using Python logging.
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
* [aiokafka Docs](https://aiokafka.readthedocs.io/en/stable/)
* [Alembic Docs](https://alembic.sqlalchemy.org/)
