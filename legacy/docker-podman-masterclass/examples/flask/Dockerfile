# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime

# Sécurité de base : non-root
RUN useradd -u 10001 -m appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER 10001
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/').read()" || exit 1

CMD ["python", "app.py"]
