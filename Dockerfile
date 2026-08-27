FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# Intentionally runs as root for the later container-misconfiguration demo.
CMD ["python", "app.py"]
