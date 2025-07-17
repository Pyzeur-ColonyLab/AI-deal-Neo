FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Install python-dotenv for environment variable support
RUN pip install --no-cache-dir python-dotenv

# Copy config if needed (uncomment if config.py is required)
# COPY ./backend/config.py ./backend/config.py

# Use Uvicorn in production mode
# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

COPY ./backend ./backend
COPY run_server.py ./
COPY setup_server.py ./

EXPOSE 8000

# Use the improved main application for production
CMD ["uvicorn", "backend.main_improved:app", "--host", "0.0.0.0", "--port", "8000"] 