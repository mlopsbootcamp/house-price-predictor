FROM python:3.13-slim

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY src/api/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup src/api/ /app/src/api/
COPY --chown=appuser:appgroup models/trained/ /app/models/trained/

# Ensure Python can find the modules
ENV PYTHONPATH=/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


