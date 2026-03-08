# Multistage build for minimizing size (optimal for Raspberry Pi)
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies if needed, then Python dependencies
# Using --user to install in /root/.local so we can easily copy it later
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Final Runtime Image ---
FROM python:3.10-slim

WORKDIR /app

# Copy installed dependencies from the builder image
COPY --from=builder /root/.local /root/.local

# Ensure the local bin is on the PATH for streamlit/python execution
ENV PATH=/root/.local/bin:$PATH

# Copy source code and data directory structure
COPY src/ ./src/
COPY data/ ./data/

# At runtime we don't define a CMD here because docker-compose 
# will specify the command to run for each service (daemon vs dashboard)
