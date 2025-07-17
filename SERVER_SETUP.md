# Server Setup Guide - Direct Python Execution

This guide explains how to run the Aid-al-Neo API server directly on your server without Docker.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- At least 16GB RAM (recommended for model loading)
- At least 50GB free disk space for model cache

## Quick Start

### 1. Setup Environment

```bash
# Run the setup script
python setup_server.py
```

This will:
- Check Python version
- Install all required dependencies
- Create necessary directories
- Verify installation

### 2. Start the Server

```bash
# Start the API server
python test_server.py
```

The server will:
- Start on `http://localhost:8000`
- Pre-load the Pyzeur/Code-du-Travail-mistral-finetune model
- Enable auto-reload for development
- Show detailed logs

### 3. Test the API

In another terminal:

```bash
# Run the test suite
python test_api.py
```

Or test manually:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat endpoint (requires API key)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer test_api_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour, expliquez-moi les règles de licenciement en France",
    "channel": "test",
    "user_id": "test_user"
  }'
```

## API Endpoints

### Available Endpoints

- **Health Check**: `GET /api/v1/health`
- **Chat**: `POST /api/v1/chat`
- **Models List**: `GET /api/v1/models`
- **API Documentation**: `GET /docs` (Swagger UI)

### Authentication

Use the test API key: `test_api_key_123`

Example:
```bash
curl -H "Authorization: Bearer test_api_key_123" \
     http://localhost:8000/api/v1/models
```

## Configuration

### Environment Variables

The server uses these environment variables (set automatically by `test_server.py`):

- `API_KEY`: API key for authentication (default: `test_api_key_123`)
- `ADMIN_TOKEN`: Admin token (default: `test_admin_token_456`)
- `MODEL_CACHE_DIR`: Model cache directory (default: `./models/cache`)
- `LOG_DIR`: Log directory (default: `./logs`)
- `PARAMS_DIR`: Parameters directory (default: `./params`)
- `ENV`: Environment (default: `development`)
- `ALLOWED_ORIGINS`: CORS origins (default: `*`)

### Custom Configuration

To use custom settings, create a `.env` file:

```bash
# .env
API_KEY=your_custom_api_key
ADMIN_TOKEN=your_custom_admin_token
HF_TOKEN=your_huggingface_token  # Optional
MODEL_CACHE_DIR=/path/to/custom/cache
```

## Model Information

### Pre-loaded Model

The server automatically loads:
- **Base Model**: `mistralai/Mistral-7B-Instruct-v0.3`
- **Fine-tuned Model**: `Pyzeur/Code-du-Travail-mistral-finetune`
- **Purpose**: French labor law assistance

### Model Loading Process

1. Downloads base model from Hugging Face Hub
2. Loads fine-tuned adapter
3. Falls back to base model if adapter fails
4. Optimized for faster inference

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or use a different port
# Edit test_server.py and change port=8000 to port=8001
```

#### 2. Out of Memory
```bash
# Check available memory
free -h

# If less than 16GB, consider:
# - Using a smaller model
# - Increasing swap space
# - Using a machine with more RAM
```

#### 3. Model Download Issues
```bash
# Check internet connection
ping huggingface.co

# Check disk space
df -h

# Clear model cache if corrupted
rm -rf ./models/cache/*
```

#### 4. Permission Issues
```bash
# Make scripts executable
chmod +x test_server.py test_api.py setup_server.py

# Check directory permissions
ls -la
```

### Logs

Check logs in the `./logs` directory or server console output for detailed error information.

## Production Deployment

For production use:

1. **Security**: Change default API keys
2. **Environment**: Set `ENV=production`
3. **CORS**: Restrict `ALLOWED_ORIGINS`
4. **HTTPS**: Use a reverse proxy (Nginx) with SSL
5. **Process Management**: Use systemd or supervisor
6. **Monitoring**: Set up logging and monitoring

### Example Production Setup

```bash
# Create production environment file
cat > .env.production << EOF
ENV=production
API_KEY=your_secure_api_key_here
ADMIN_TOKEN=your_secure_admin_token_here
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
MODEL_CACHE_DIR=/opt/aidalneo/models/cache
LOG_DIR=/opt/aidalneo/logs
PARAMS_DIR=/opt/aidalneo/params
EOF

# Run with production settings
ENV_FILE=.env.production python test_server.py
```

## Performance Optimization

### For Better Performance

1. **GPU Acceleration**: Install CUDA-enabled PyTorch
2. **Model Quantization**: Use quantized models for faster inference
3. **Caching**: Implement response caching
4. **Load Balancing**: Use multiple server instances

### Memory Optimization

1. **Model Offloading**: Use CPU offloading for large models
2. **Batch Processing**: Process multiple requests in batches
3. **Garbage Collection**: Monitor and optimize memory usage

## Support

If you encounter issues:

1. Check the logs in `./logs` directory
2. Verify all dependencies are installed
3. Ensure sufficient system resources
4. Check network connectivity for model downloads

## Next Steps

After successful testing:

1. **Deploy to Production**: Follow production deployment guide
2. **Set up Monitoring**: Implement health checks and monitoring
3. **Configure SSL**: Set up HTTPS with proper certificates
4. **Scale**: Consider load balancing for high traffic 