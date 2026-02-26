FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn   # serveur WSGI de prod

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Gunicorn à la place de python app.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]