FROM python:3.11-slim

WORKDIR /app    # Set working directory in container
COPY . /app     # Copy all files into the container

RUN pip install --no-cache-dir -r requirements.txt      # Install dependencies from requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]      # Run FastAPI server inside container