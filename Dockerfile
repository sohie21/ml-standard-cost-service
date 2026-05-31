FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV MODEL_VERSION=1.0.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data ./data
COPY src ./src

RUN python src/train.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
