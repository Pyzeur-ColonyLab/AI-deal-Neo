# Requirements Document

**Version:** v1.0.0
**Approval Status:** Approved

## 1. Functional Requirements

### FR1: API Server
- The system shall expose a RESTful API to receive requests from external services (Telegram, webapp, mail server, etc.).
- The API shall accept input messages and return AI-generated responses.

### FR2: AI Model Integration
- The system shall use the existing AI model runner from the current repo to generate responses.
- The system shall support at least one custom AI chatbot model.

### FR3: Multi-Channel Support
- The API shall be designed to support requests from multiple channels (Telegram, webapp, mail server).
- The system shall log the source of each request for traceability.

### FR4: Response Handling
- The system shall return responses in a standardized JSON format.
- The system shall handle and report errors gracefully.

### FR5: Security
- The API shall require authentication (e.g., API keys or OAuth2).
- The system shall validate and sanitize all inputs.

### FR6: Monitoring & Logging
- The system shall log all requests and responses.
- The system shall provide basic health and status endpoints.

### FR7: Model Management
- The system shall provide an endpoint to list all available AI models.
- The system shall provide an endpoint to load a specific AI model into memory.
- The system shall provide an endpoint to unload a specific AI model from memory.
- The system shall support only one model loaded at a time.
- The system shall automatically unload the current model when loading a new one.
- The system shall support downloading models from Hugging Face Hub.
- The system shall support multiple model formats including Safetensors, GGUF, and other standard formats.

### FR8: API Documentation and Access
- The system shall provide Swagger UI interface for API documentation and testing.
- The system shall be accessible via the domain name cryptomaltese.com.
- The system shall enforce HTTPS communication with valid SSL certificates.
- The system shall redirect all HTTP traffic to HTTPS.

### FR9: System Administration
- The system shall provide an endpoint to trigger system cleanup operations (logs, cache, models, temp files).
- The system shall provide an endpoint to purge old log files to free disk space.
- The system shall provide an endpoint to monitor system status and resource usage.
- The system shall support forced cleanup operations even when the system is busy.
- The system shall track and report the amount of space freed during cleanup operations.
- The system shall provide detailed system health monitoring (disk usage, memory usage, model status).

### FR10: Model Parameter Management
- The system shall provide an endpoint to retrieve current parameter configuration for any model.
- The system shall provide an endpoint to update parameter configuration for any model.
- The system shall provide an endpoint to reset model parameters to default values.
- The system shall support common AI model parameters (temperature, top_k, top_p, max_length, etc.).
- The system shall validate parameter values within acceptable ranges.
- The system shall track parameter changes with timestamps.
- The system shall allow partial parameter updates (update only specific parameters).

## 2. Non-Functional Requirements

- NFR1: Performance: The API shall respond within 60 seconds for 99% of requests.
- NFR2: Scalability: The system shall support concurrent requests (minimum 50 QPS).
- NFR3: Reliability: The system shall have >99% uptime.
- NFR4: Maintainability: The codebase shall follow established coding standards and be well-documented.
- NFR5: Security: The system shall comply with GDPR and data privacy best practices.

## 3. Business Rules & Constraints

- BR1: Only authorized services may access the API.
- BR2: The AI model must be loaded and ready before serving requests.
- BR3: The system must be deployable on both local Mac OS and the target server (Infomaniak instance).
- BR4: The system may delay responses up to 60 seconds to optimize server resource usage and cost.

## 4. Acceptance Criteria

- AC1: API returns valid AI responses for all supported channels.
- AC2: Unauthorized requests are rejected.
- AC3: System passes all functional and non-functional tests.
- AC4: The system does not exceed the 60-second response time for any request.
- AC5: Model listing endpoint returns all available models with correct status information.
- AC6: Model loading endpoint successfully loads the specified model and unloads any previously loaded model.
- AC7: Model unloading endpoint successfully unloads the specified model.
- AC8: Only one model can be loaded at any given time.
- AC9: Model downloading from Hugging Face Hub works correctly for public and private models.
- AC10: System correctly handles multiple model formats (Safetensors, GGUF, PyTorch, ONNX).
- AC11: Model download progress is tracked and reported accurately.
- AC12: Swagger UI interface is accessible and functional at the designated endpoint.
- AC13: System is accessible via cryptomaltese.com domain.
- AC14: SSL certificate is valid and HTTPS communication is enforced.
- AC15: HTTP traffic is properly redirected to HTTPS.
- AC16: System cleanup operations successfully free disk space and clean specified resources.
- AC17: Log purging operations remove old log files and report freed space accurately.
- AC18: System status endpoint provides accurate resource usage information.
- AC19: Forced cleanup operations work even when the system is busy.
- AC20: System health monitoring provides real-time status updates.
- AC21: Model parameter retrieval endpoint returns current configuration for any model.
- AC22: Model parameter update endpoint successfully modifies specified parameters.
- AC23: Model parameter reset endpoint restores default values correctly.
- AC24: Parameter validation ensures values are within acceptable ranges.
- AC25: Parameter changes are tracked with accurate timestamps.
- AC26: Partial parameter updates work correctly (only specified parameters are modified).

## 5. Priority Levels

- Must have: API server, AI model integration, security, logging.
- Should have: Multi-channel support, monitoring endpoints.
- Could have: Advanced analytics, rate limiting.

---

**Change Log:**
- v1.0.0: Initial requirements document created. 