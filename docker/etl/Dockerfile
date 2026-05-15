# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /src

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . /src

# Wait for Postgres to be initialized, then run the ETL
CMD bash -c "\
    echo '⏳ Waiting for PostgreSQL initialization...'; \
    sleep 10; \
    echo '🚀 Starting ETL process...'; \
    python3 etl/load.py; \
    echo '✅ ETL pipeline completed successfully.'; \
"
