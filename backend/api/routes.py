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
        logger.info(f"Received chat request: message='{request.message[:50]}...', channel='{request.channel}', user_id='{request.user_id}'")
        
        # Check if model is loaded
        if not hf_model_service.is_model_loaded():
            raise HTTPException(
                status_code=503, 
                detail="Model not loaded. The system is still initializing or the model failed to load."
            )
        
        # Default parameters - only include parameters that HF model service expects
        default_params = {
            "max_new_tokens": 300,
            "temperature": 1.0,
            "top_p": 0.9,
            "repetition_penalty": 1.0,
            "do_sample": True,
            "num_beams": 1,
            "num_return_sequences": 1
        }
        
        # Merge with request parameters if provided
        if request.parameters:
            # Only include parameters that the HF model service expects
            valid_params = {
                "max_new_tokens", "temperature", "top_p", "repetition_penalty", 
                "do_sample", "num_beams", "num_return_sequences", "pad_token_id"
            }
            filtered_params = {k: v for k, v in request.parameters.items() if k in valid_params}
            default_params.update(filtered_params)
        
        logger.info(f"Using parameters: {default_params}")
        
        # Use HFModelService for inference
        response_text = hf_model_service.generate_response(request.message, default_params)
        
        resp = ChatResponse(
            response=response_text,
            model="Pyzeur/Code-du-Travail-mistral-finetune",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            parameters_used=default_params
        )
        
        logger.info(f"Chat request processed successfully for user {request.user_id} on channel {request.channel}")
        return resp
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 