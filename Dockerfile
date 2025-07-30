FROM python:3.11-slim

WORKDIR /app

COPY src/api/ .

RUN pip install -r requirements.txt

COPY models/trained/*.pkl models/trained/

EXPOSE 8000

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]