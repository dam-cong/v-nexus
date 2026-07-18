FROM python:3.11-slim
WORKDIR /app
COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 -r requirements.txt
COPY agent/ ./agent/
COPY tools/ ./tools/
COPY domain/ ./domain/
COPY db/ ./db/
COPY docs/data/ ./docs/data/
COPY gateway/app/ ./app/
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
