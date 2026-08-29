FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apk upgrade --no-cache \
    && addgroup -S appgroup \
    && adduser -S -D -H -G appgroup -u 10001 appuser

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && rm -rf /usr/local/lib/python3.13/site-packages/pip* \
              /usr/local/bin/pip*

COPY --chown=appuser:appgroup app.py .

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"]

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=2", "--threads=2", "--access-logfile=-", "--error-logfile=-", "app:app"]
