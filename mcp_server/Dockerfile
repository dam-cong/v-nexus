FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 -r requirements.txt
COPY mcp_server/server.py .
EXPOSE 8100
CMD ["python", "server.py"]
