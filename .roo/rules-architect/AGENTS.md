# Architect Mode Rules (Non-Obvious Only)

## Architecture Constraints
- FastAPI app with modular router pattern
- External API calls via `requests` library (no internal HTTP client)
- No database layer in current phase
- Stateless design for future caching layer (Valkey/Redis)

## Extension Points
- `src/app/services/` for future service layer
- `src/app/routes/` for new endpoints
- Environment-based configuration pattern

## Phase Progression
- Phase 1-2: Basic version endpoint
- Phase 3: Temperature endpoint with external API
- Phase 4+: Metrics, caching, storage layers
