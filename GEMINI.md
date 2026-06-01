# HiveBox Project Instructions

HiveBox is a FastAPI application designed to aggregate and monitor temperature data from several senseBox sensors via the openSenseMap API. It features multi-tier caching, cloud-native storage, and Prometheus monitoring.

## 🛠 Tech Stack
- **Language:** Python 3.13
- **Framework:** FastAPI (Asynchronous)
- **Package Manager:** `uv`
- **Caching:** Valkey (Redis-compatible) with in-memory fallback
- **Storage:** Minio (S3-compatible) for periodic data persistence
- **Monitoring:** Prometheus (`prometheus_client`)
- **Infrastructure:** Kubernetes (Helm, Kustomize), Docker

## 📁 Project Structure
- `src/app/`: Core application logic.
  - `routes/`: API endpoints (version, temperature, metrics, readyz, store).
  - `services/`: Business logic and integrations.
    - `sensor_service.py`: Aggregation logic and API interaction.
    - `storage_service.py`: Minio/S3 storage logic.
    - `valkey_service.py`: Redis-based caching layer.
- `tests/`: Test suite.
  - `unit/`: Component-level tests (mocking external dependencies).
  - `integration/`: API-level tests using `TestClient`.
- `infra/` & `k8s/`: Infrastructure as Code (Kustomize, Helm, Kubernetes manifests).
- `charts/`: Helm charts for the application.

## 🚀 Key Commands
- **Setup:** `uv sync --dev`
- **Run Development Server:** `uv run uvicorn src.app.main:app --reload`
- **Run Tests:** `uv run pytest`
- **Linting:** `uv run flake8 src/`
- **Docker Build:** `docker build -t hivebox:local .`

## ⚖️ Development Conventions
- **Code Style:** Strictly follow PEP 8 using `flake8`.
- **Quality Gates:** Code must pass `pylint` and `SonarQube` scans. Fix warnings in touched files rather than silencing them.
- **Type Safety:** Use systematic Python type hinting.
- **Async First:** Leverage FastAPI's asynchronous capabilities for I/O bound tasks.
- **Testing:** Add or update unit tests for every logic change. A change is incomplete without verification.
- **PR Style:** Keep edits small, surgical, and easy to review. Match existing project structure and naming conventions.

## 💡 Important Logic & Gotchas
- **Caching:** Data is cached in Valkey with a 5-minute TTL. `SensorService.get_data()` handles the tiered lookup (Valkey -> API -> In-memory fallback).
- **Health Checks:** The `/readyz` endpoint uses a majority-rule logic: it reports unhealthy only if the majority of sensors are unreachable AND the cache is stale (> 5 mins).
- **Data Freshness:** Sensor measurements are considered "too old" if they exceed 1 hour (configured in `src/app/routes/temperature.py`).
- **Temperature Status:**
  - `< 10`: "Too Cold"
  - `10 - 37`: "Good"
  - `> 37`: "Too Hot"

## 📚 References
- `readme.md`: High-level repository structure.
- `AGENTS.md`: Detailed agent-specific instructions and known bug tracking.
- `.github/subject.md`: Project specification and phase roadmap.
