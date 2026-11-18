FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY src/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/api/*.py ./
COPY models/trained/house_price_model.pkl models/trained/preprocessor.pkl ./models/trained/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
