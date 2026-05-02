FROM python:3.14-slim AS builder

WORKDIR /tmp

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.14-slim

LABEL maintainer="HiveBox Team"
LABEL description="HiveBox - Environmental sensor data API"


RUN useradd -m -u 1000 appuser

WORKDIR /app


COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local


COPY --chown=appuser:appuser src/ .


ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]