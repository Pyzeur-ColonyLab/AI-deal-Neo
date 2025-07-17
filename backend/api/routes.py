from fastapi import APIRouter, Depends, HTTPException, status
from backend.auth import get_api_key
from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.hf_model_service import HFModelService
import time
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Service singleton
hf_model_service = HFModelService()

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

# --- Chat Endpoint ---
@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
def chat(request: ChatRequest):
    try:
        logger.info(f"=== CHAT REQUEST START ===")
        logger.info(f"Received chat request: message='{request.message[:50]}...', channel='{request.channel}', user_id='{request.user_id}'")
        
        # Check if model is loaded
        logger.info(f"Checking if model is loaded...")
        model_loaded = hf_model_service.is_model_loaded()
        logger.info(f"Model loaded status: {model_loaded}")
        
        if not model_loaded:
            logger.error("Model not loaded - raising 503 error")
            raise HTTPException(
                status_code=503, 
                detail="Model not loaded. The system is still initializing or the model failed to load."
            )
        
        logger.info("Model is loaded, proceeding with request...")
        
        # Use HFModelService for inference with its own parameters
        logger.info(f"Calling HF model service with message: '{request.message[:50]}...'")
        response_text = hf_model_service.generate_response(request.message)
        
        logger.info(f"Got response from model, length: {len(response_text)}")
        logger.info(f"Response preview: '{response_text[:100]}...'")
        
        resp = ChatResponse(
            response=response_text,
            model="Pyzeur/Code-du-Travail-mistral-finetune",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            parameters_used=hf_model_service.get_parameters()
        )
        
        logger.info(f"Chat request processed successfully for user {request.user_id} on channel {request.channel}")
        logger.info(f"=== CHAT REQUEST END ===")
        return resp
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in chat endpoint: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e)) 