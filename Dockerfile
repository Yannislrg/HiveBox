FROM astral-sh/uv:latest AS builder

WORKDIR /app


ENV UV_COMPILE_BYTECODE=1


COPY pyproject.toml uv.lock ./


RUN uv sync --frozen --no-dev


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
