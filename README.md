# Aid-al-Neo: AI Model API Platform

## Overview
Aid-al-Neo is a production-ready AI model serving platform that provides a simple chat API. The system automatically loads the Pyzeur/Code-du-Travail-mistral-finetune model when the container starts and is ready to serve chat requests immediately. The platform is designed for high performance, security, and maintainability, and is deployable on both local Mac OS and Infomaniak server instances.

## Architecture Summary
- **API Server:** FastAPI backend with OpenAPI/Swagger UI
- **Model Management:** Automatic pre-loading of Pyzeur/Code-du-Travail-mistral-finetune model
- **Authentication:** API key support for secure access
- **Logging & Monitoring:** Request/response logging, health endpoint
- **Deployment:** Dockerized, Nginx reverse proxy, SSL/HTTPS enforced

## Directory Structure
- `/backend/` — Source code for FastAPI backend and HF model service
- `/docker/` — Docker and Nginx setup
- `/documentation/` — Requirements, technical specs, API docs, validation criteria

## Quick Start
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Aid-al-Neo
   ```
2. **Set your Hugging Face token in docker-compose.yml:**
   ```yaml
   environment:
     - HF_TOKEN=your_huggingface_token_here
   ```
3. **Build and run with Docker Compose:**
   ```bash
   cd docker
   docker-compose up --build
   ```
4. **Access the API:**
   - Swagger UI: [https://cryptomaltese.com/docs](https://cryptomaltese.com/docs)
   - Health check: `/api/v1/health`
   - Chat endpoint: `/api/v1/chat`

## API Endpoints

### POST /api/v1/chat
Generate AI responses using the pre-loaded Pyzeur/Code-du-Travail-mistral-finetune model.

**Request:**
```json
{
  "message": "Your message here",
  "channel": "webapp",
  "user_id": "user123",
  "parameters": {
    "temperature": 0.7,
    "max_length": 150
  }
}
```

**Response:**
```json
{
  "response": "AI generated response",
  "model": "Pyzeur/Code-du-Travail-mistral-finetune",
  "timestamp": "2024-01-15T10:30:00Z",
  "parameters_used": {
    "temperature": 0.7,
    "max_length": 150,
    "top_k": 50,
    "top_p": 0.9
  }
}
```

### GET /api/v1/health
Check system health status.

**Response:**
```json
{
  "status": "ok"
}
```

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
- Hugging Face token (optional, for private models)

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
- `HF_TOKEN`: (Optional) Hugging Face token for private models
- `ALLOWED_ORIGINS`: CORS origins (default: https://cryptomaltese.com)

### 3. Model Pre-loading
The system automatically loads the Pyzeur/Code-du-Travail-mistral-finetune model when the container starts. You can see the loading progress in the container logs:
```bash
docker logs aidalneo-backend
```

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
- Use strong, unique API keys
- Restrict CORS in production (see `backend/main.py`)
- Monitor logs and resource usage
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

## Testing the API

### Test Chat Endpoint
```bash
curl -X POST "https://cryptomaltese.com/api/v1/chat" \
  -H "Authorization: Bearer changeme" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How are you?",
    "channel": "webapp",
    "user_id": "user123",
    "parameters": {
      "temperature": 0.7,
      "max_length": 150
    }
  }'
```

### Test Health Endpoint
```bash
curl -X GET "https://cryptomaltese.com/api/v1/health"
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
   docker compose up --build -d
   ```
3. Check that the model loaded successfully:
   ```bash
   docker logs aidalneo-backend
   ```
4. Test the chat endpoint as shown above.

## License
MIT 