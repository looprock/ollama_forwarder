FROM python:3.13-slim

WORKDIR /app

# Copy requirements
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir flask requests

# Copy application code
COPY ollama_service.py ./

# Create non-root useryour-secret-api-key-here
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Environment variables with defaults
ENV OLLAMA_URL=http://localhost:11434/api/generate
ENV MODEL=granite4:latest
ENV PREPEND_STATEMENT=""
ENV API_KEY=change-me-in-production

# Run the service
CMD ["python", "ollama_service.py", \
     "--host", "0.0.0.0", \
     "--port", "5000"]
