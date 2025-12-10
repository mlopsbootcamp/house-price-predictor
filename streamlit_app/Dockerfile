FROM python:3.9-slim

WORKDIR /app

COPY app.py requirements.txt /app/

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]