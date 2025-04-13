FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies (with psycopg[binary])
COPY requirements.txt .
RUN pip install --no-cache-dir "psycopg[binary]==3.2.6" && \
    pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Copy and set entrypoint
COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]