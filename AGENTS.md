# HiveBox agent instructions

## Source of truth
- Treat [`.github/subject.md`](.github/subject.md) as the project specification and phase roadmap.
- Prefer linking to existing docs instead of repeating them here.

## Repo shape
- Python app code lives under `src/app/`.
- Keep routing concerns in `src/app/routes/` and service/integration code in `src/app/services/`.
- The repository is currently at an early scaffold stage; several source files are placeholders.

## Working style
- Make changes that match the current phase only; avoid building later-phase features early.
- Keep edits small and easy to review.
- Preserve the existing project structure and naming style.
- If a convention is missing from the codebase, infer it from the spec or ask rather than inventing a new one.

## Documentation
- Update or add docs in `docs/` when behavior changes, but keep implementation details out of this file.
- For phase-specific requirements, reference the relevant section in `subject.md`.

## Validation
- Use the project’s existing test, lint, and build setup when it exists.
- If tooling is not yet present, report the gap instead of assuming commands or config.

## Useful references
- `readme.md` — high-level repository structure
- `.github/subject.md` — phased requirements and constraints

## Critical Bugs
- Data freshness check: `> 100 weeks` should be `> 1 hour` (currently skips all data)
- Temperature status thresholds: code uses `<11`, `11-36`, `>36` but spec says `<10`, `10-37`, `>37`

## Environment
- Load `.env` before running API calls (required for `BASE_URL` and `BOX_ID`)
- API calls use 30s timeout; handle `requests.RequestException` and `ValueError`

## Docker
- Runs uvicorn on port 8000
- User `appuser` for security
