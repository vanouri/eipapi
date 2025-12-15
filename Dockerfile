# Dockerfile

# ----------------------------------------------------
# STAGE 1: Builder - Install Dependencies
# ----------------------------------------------------
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copier le fichier des dépendances
COPY requirements.txt .

# Install dependencies directly using pip and store them locally
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --target /install

# ----------------------------------------------------
# STAGE 2: Runtime - Final Image
# ----------------------------------------------------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copy pre-installed dependencies from the builder stage
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# Copy application code (Assuming 'main.py' and other files are in the current directory)
COPY . .

# Expose the default FastAPI/Uvicorn port
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]