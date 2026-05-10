# Debug Mode Rules (Non-Obvious Only)

## Environment Variables
- `BASE_URL` and `BOX_ID` required for temperature endpoint
- `BOX_ID` is comma-separated list of senseBox IDs

## Common Issues
- Data freshness check bug: `> 100 weeks` returns True for all data (always skips)
- Temperature status threshold mismatch: code uses 11-36, spec says 10-37
- Missing `.env` file causes API calls to fail silently

## Logging
- Logs to console via Python logging module
- Check `logger.debug()` for sensor filtering
- Check `logger.warning()` for no active boxes
