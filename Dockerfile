FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better cache utilization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_DIRECTORY=/app/data

# Expose port for FastAPI
EXPOSE 5000

# Create an entrypoint script to handle different commands
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default command - run the application with uvicorn
CMD ["app"]