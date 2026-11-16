# ClinicFlow API

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Pytest Tests](https://img.shields.io/badge/Pytest-22%20passed-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ClinicFlow API** is a backend healthcare and appointment scheduling engine built with **FastAPI**, **SQLAlchemy 2.0**, and **PostgreSQL**. 

The goal of this project is to implement a robust, production-style appointment system that handles real-world domain challenges: discrete time slot allocation, concurrency and race condition safety, patient quota rules, and API security.

---

## 🎯 Problems Solved & Technical Highlights

### 1. Discrete TimeSlot Architecture
Free-form time inputs (`"10:01"`, `"10:20"`) frequently cause overlapping intervals and difficult validation logic. ClinicFlow solves this by modeling appointments around standardized, discrete 30-minute `TimeSlot` entities.
* Doctor schedules are bound to slot availability.
* Double-booking is strictly prevented at the database layer via a composite constraint: `UniqueConstraint("doctor_id", "appointment_date", "slot_id")`.

### 2. Concurrency & Race Condition Safety
* Implements `SELECT ... FOR UPDATE` row-level locking on active user records during booking.
* Handled through database constraints combined with explicit `IntegrityError` rollback handling, ensuring parallel booking requests for the exact same slot fail gracefully (`409 Conflict`) without database corruption.

### 3. Healthcare Domain Rules (Business Logic)
* **Single Active Appointment per Specialty:** A patient cannot hold multiple active bookings within the same medical department (e.g., Cardiology).
* **Cross-Doctor Time Collision Prevention:** A patient cannot book appointments with different doctors at the exact same date and time slot.
* **Quota Enforcement:** Patients are capped at a maximum of 3 active scheduled appointments.
* **Slot Reactivation Lifecycle:** When an appointment is cancelled, its composite slot becomes bookable again. Subsequent bookings re-activate and update the existing slot record rather than conflicting with historical cancelled data.
* **Historical Date Rejection:** Prevents reservations on past dates.

### 4. Security & Defensive Design
* **Insecure Direct Object Reference (IDOR) Prevention:** Ownership verification ensures patients can only view and cancel their own appointments (`403 Forbidden` on unauthorized cancellation attempts).
* **Privilege Escalation Protection:** Registration endpoint strips role inputs and enforces default `PATIENT` role assignment.
* **Dual-Layer XSS Defense:** Pydantic V2 `@field_validator` automatically sanitizes incoming patient notes using `html.escape`, paired with frontend entity encoding.
* **Authentication:** Password hashing via `bcrypt` and stateless session verification using `PyJWT` Bearer tokens.

---

## 🏗️ Project Structure

```text
clinicflow_api/
├── app/
│   ├── core/           # Security, JWT tokens, Pydantic settings
│   ├── models/         # SQLAlchemy 2.0 ORM models (User, Doctor, TimeSlot, Appointment)
│   ├── schemas/        # Pydantic V2 data validation and sanitization
│   ├── routers/        # API endpoints: auth, doctor, appointments
│   └── database.py     # Database session and multi-engine configuration
│
├── static/             # Clean client interface for live testing and manual verification
│   ├── css/style.css   # Custom styling and transitions
│   └── js/             # Modular JS: api.js, auth.js, app.js
│
├── tests/              # Automated test suite (22 tests, 100% passing)
│   ├── conftest.py     # In-memory SQLite fixtures & Factory Pattern helpers
│   ├── test_appointments.py # 15 domain tests (concurrency, quotas, IDOR, lifecycle)
│   ├── test_auth.py    # 5 authentication & registration tests
│   └── test_doctors.py # 2 catalog & slot availability matrix tests
│
├── Dockerfile          # Python 3.11-slim container definition
├── docker-compose.yml  # Multi-container orchestration (FastAPI + PostgreSQL 16)
├── requirements.txt    # Application dependencies
├── seed.py             # Database seeder for standard time slots and demo accounts
└── main.py             # Application entrypoint with startup lifespan automation
```

---

## 🚀 Getting Started

### Using Docker Compose (Recommended)

Run the full stack (FastAPI application + PostgreSQL 16 database) with a single command:

```bash
docker compose up --build
```

* **Interactive Web Portal:** [http://localhost:8000](http://localhost:8000)
* **Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Manual Local Setup (SQLite fallback)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/WATSONSK14/clinicflow-api.git
   cd clinicflow-api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the development server:**
   ```bash
   uvicorn main:app --reload
   ```
   *(Database tables and 20 discrete time slots are automatically initialized on startup via FastAPI lifespan).*

---

## 🧪 Testing

The automated test suite runs against an isolated in-memory SQLite database using dynamic Factory fixtures, making tests resilient and time-independent.

Run all tests:
```bash
pytest -v
```

Expected test run output:
```text
============================= test session starts =============================
collected 22 items

tests/test_appointments.py ...............                                [ 68%]
tests/test_auth.py .....                                                  [ 90%]
tests/test_doctors.py ..                                                  [100%]

============================= 22 passed in 8.14s =============================
```

---

## 🔑 Default Seed Credentials

For manual testing, default credentials seeded into the database:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@clinicflow.com` | `Admin123!` |
| **Doctor** | `dr.watson@clinicflow.com` | `Doctor123!` |
| **Patient** | `hasta@clinicflow.com` | `Hasta123!` |

---

## 👤 Author

* **Serhat Kutlu**
* GitHub: [@WATSONSK14](https://github.com/WATSONSK14)
* Focus: Backend Development, Python, FastAPI, PostgreSQL, Database Optimization

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
