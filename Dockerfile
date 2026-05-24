FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile


FROM python:3.13-slim

LABEL maintainer="HiveBox Team"
LABEL description="HiveBox - Environmental sensor data API"

RUN useradd -m -u 1000 appuser

WORKDIR /app


COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser src/ src/


ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
