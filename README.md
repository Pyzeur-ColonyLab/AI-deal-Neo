# Aid-al-Neo: AI Model API Platform

## Overview
Aid-al-Neo is a modular, production-ready AI model serving platform. It exposes a secure RESTful API for multi-channel access (Telegram, webapp, mail, etc.), supporting dynamic model management, parameter configuration, and system administration. The system is designed for high performance, security, and maintainability, and is deployable on both local Mac OS and Infomaniak server instances.

## Architecture Summary
- **API Server:** FastAPI backend with OpenAPI/Swagger UI
- **Model Management:** Dynamic loading/unloading, Hugging Face Hub integration
- **Authentication:** API key and admin token support
- **Logging & Monitoring:** Request/response logging, health/status endpoints
- **Parameter Management:** Per-model parameter config, validation, and reset
- **System Admin:** Endpoints for cleanup, log purging, and resource monitoring
- **Deployment:** Dockerized, Nginx reverse proxy, SSL/HTTPS enforced

## Directory Structure
- `/backend/` — Source code for FastAPI backend and all modules
- `/config/` — Environment and deployment configuration files
- `/docker/` — Docker and Nginx setup
- `/documentation/` — Requirements, technical specs, API docs, validation criteria

## Quick Start
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Aid-al-Neo
   ```
2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```
3. **Access the API:**
   - Swagger UI: [https://cryptomaltese.com/docs](https://cryptomaltese.com/docs)
   - Health check: `/api/v1/health`

## Documentation
- [Technical Specs](documentation/technical-specs.md)
- [API Documentation](documentation/api-documentation.md)
- [Requirements](documentation/requirements.md)
- [Validation Criteria](documentation/validation-criteria.md)

## Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- Domain (e.g., cryptomaltese.com) pointed to your server
- SSL certificates (Let's Encrypt recommended; see below)

### 1. Build and Run the System
From the project root:
```bash
cd docker
# Build and start all services
sudo docker-compose up --build -d
```

### 2. Environment Variables
Set environment variables in `docker-compose.yml` or via a `.env` file:
- `API_KEY`: Main API key for user access
- `ADMIN_TOKEN`: Admin token for privileged endpoints
- `MODEL_CACHE_DIR`, `LOG_DIR`, `PARAMS_DIR`: Data persistence paths
- `HF_TOKEN`: (Optional) Hugging Face token for private models

### 3. Volumes and Persistence
- Models, logs, and parameters are persisted via Docker volumes:
  - `../models:/models`
  - `../logs:/logs`
  - `../params:/params`

### 4. SSL Certificates
- Place your SSL certificates in `certs/` (or use Let's Encrypt)
- Nginx is preconfigured for SSL termination and HTTP→HTTPS redirection
- Certificates are mounted at `/etc/letsencrypt` in the Nginx container

### 5. Accessing the API
- API: `https://cryptomaltese.com/api/v1/`
- Swagger UI: `https://cryptomaltese.com/docs`

### 6. Stopping and Updating
```bash
sudo docker-compose down   # Stop all services
sudo docker-compose pull   # Update images (if using remote images)
sudo docker-compose up --build -d  # Rebuild and restart
```

### 7. Production Best Practices
- Use strong, unique API keys and admin tokens
- Restrict CORS in production (see `backend/main.py`)
- Monitor logs and resource usage
- Regularly backup models, logs, and params
- Keep Docker and dependencies up to date

For more details, see the `docker/` directory and documentation.

### SSL Certificate Setup
To automate SSL certificate installation and renewal for `cryptomaltese.com`:

1. SSH into your server and switch to the project root.
2. Run the SSL fix script as root:
   ```bash
   cd docker
   sudo ./fix_ssl_certificate.sh
   ```
   - This will:
     - Check DNS resolution
     - Obtain a Let's Encrypt SSL certificate
     - Place certs in `../certs/` (used by Nginx)
     - Restart Docker services
     - Set up auto-renewal via cron
3. After completion, your API and docs will be available at:
   - `https://cryptomaltese.com/api/v1/`
   - `https://cryptomaltese.com/docs`

**Note:**
- Edit `docker/fix_ssl_certificate.sh` to change domain/email if needed.
- Certbot must be installed on the server (`sudo apt install certbot`).
- The script will stop/start Docker services as needed.

## Using Adapter (PEFT/LoRA) Models

1. **Download the adapter model via the API:**
   ```bash
   curl -X POST "https://cryptomaltese.com/api/v1/models/download" \
     -H "Authorization: Bearer adminchangeme" \
     -H "Content-Type: application/json" \
     -d '{"model_name": "Pyzeur/Code-du-Travail-mistral-finetune"}'
   ```
2. **Load the model via the API:**
   ```bash
   curl -X POST "https://cryptomaltese.com/api/v1/models/adapter_model.safetensors/load" \
     -H "Authorization: Bearer adminchangeme"
   ```
3. **Test inference:**
   ```bash
   curl -X POST "https://cryptomaltese.com/api/v1/chat" \
     -H "Authorization: Bearer changeme" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "channel": "webapp", "user_id": "user123"}'
   ```

## After Pulling Latest Code on Server

1. Pull the latest code:
   ```bash
   git pull origin master
   ```
2. Rebuild and restart the backend container:
   ```bash
   cd docker
   docker compose down
   docker compose up -d
   ```
3. Verify the Hugging Face token is set in the container:
   ```bash
   sudo docker exec -it aidalneo-backend /bin/bash
   echo $HF_TOKEN
   exit
   ```
4. Download, load, and test the adapter model as above.

## License
MIT 