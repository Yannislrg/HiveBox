# Ask Mode Rules (Non-Obvious Only)

## Project Structure
- Python app code in `src/app/`
- Routes in `src/app/routes/`
- Services in `src/app/services/`
- Tests in `tests/unit/` (not separate test folder)

## Configuration
- Environment variables loaded from `.env` in project root
- Docker runs uvicorn on port 8000

## API Endpoints
- `/version` - returns app version
- `/temperature` - returns average temperature with status
- `/metrics` - Prometheus metrics (Phase 4+)
- `/readyz` - readiness probe (Phase 5+)
- `/store` - force store to MinIO (Phase 5+)
