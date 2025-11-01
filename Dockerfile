FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF generation
RUN apt-get update && apt-get install -y \
    pandoc \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install WeasyPrint
RUN pip install --no-cache-dir weasyprint

# Install Charm Pop for email delivery
RUN wget https://github.com/charmbracelet/pop/releases/download/v0.1.0/pop_0.1.0_linux_amd64.tar.gz \
    && tar -xzf pop_0.1.0_linux_amd64.tar.gz \
    && mv pop /usr/local/bin/ \
    && rm pop_0.1.0_linux_amd64.tar.gz

# Copy requirements
COPY requirements-service.txt /app/
COPY setup.py /app/
COPY pyproject.toml /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-service.txt
RUN pip install --no-cache-dir -e .

# Copy application code
COPY barque/ /app/barque/
COPY barque_service.py /app/

# Create directory for temporary files
RUN mkdir -p /tmp/barque

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "barque_service:app", "--host", "0.0.0.0", "--port", "8000"]
