# Code Mode Rules (Non-Obvious Only)

## Testing
- Run tests from project root: `pytest` (conftest.py modifies sys.path)
- Single test: `pytest tests/unit/test_version.py::test_get_version`

## Environment
- API credentials loaded via `load_dotenv(ROOT / ".env")` - ensure `.env` exists before running

## API Implementation
- Temperature status thresholds: <11 "Too cold", 11-36 "good", >36 "Too hot" (spec says 10-37)
- Data freshness check uses `> 100 weeks` (bug: should be 1 hour)
- API calls use `requests.get()` with 30s timeout
- Non-temperature sensors skipped by checking `sensor["title"] != "Temperatur"`
