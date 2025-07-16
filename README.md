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

## License
MIT 