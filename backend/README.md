# Aid-al-Neo Backend

## Overview
This directory contains the FastAPI backend for the Aid-al-Neo AI model API platform. It implements all API endpoints, model management, authentication, logging, and system administration as defined in the technical specifications.

## Architecture
- **main.py**: FastAPI app entry point
- **api/**: API route definitions and endpoint logic
- **models/**: Pydantic schemas for requests and responses
- **services/**: Core service classes (model manager, AI runner, parameter manager, log manager, Hugging Face client)
- **core/**: (Reserved for future core utilities)
- **auth.py**: API key and admin token authentication dependencies
- **config.py**: Environment and settings management

## Key Modules
- **ModelManager**: Handles model listing, loading, unloading, and downloading
- **AIModelRunner**: Interfaces with AI model code for inference
- **ParameterManager**: Manages per-model parameter configuration and validation
- **LogManager**: Handles logging, log storage, and cleanup
- **HuggingFaceHubClient**: Downloads models from Hugging Face Hub

## Setup
1. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```
2. Run the backend locally:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. API docs available at `/docs` when running.

## API Endpoints
- `/api/v1/chat` — Generate AI response
- `/api/v1/health` — Health check
- `/api/v1/models` — List models
- `/api/v1/models/{model_id}/load` — Load model
- `/api/v1/models/{model_id}/unload` — Unload model
- `/api/v1/models/download` — Download model
- `/api/v1/models/{model_id}/parameters` — Get/update/reset parameters
- `/api/v1/admin/cleanup` — System cleanup (admin)
- `/api/v1/admin/purge-logs` — Purge logs (admin)
- `/api/v1/admin/system-status` — System status (admin)

## Usage
- Use API key or admin token in `Authorization: Bearer ...` header
- See [../documentation/api-documentation.md](../documentation/api-documentation.md) for full API details

## Notes
- All endpoints and modules are implemented according to [../documentation/technical-specs.md](../documentation/technical-specs.md)
- For deployment, see Docker and Nginx configs in `/docker/` 