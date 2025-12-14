FROM python:3.11-slim

WORKDIR /app

# Copy API source code and requirements
COPY src/api/ ./
COPY models/trained/*.pkl ./models/trained/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
