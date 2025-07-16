from fastapi import APIRouter, Depends, HTTPException, status
from backend.auth import get_api_key, require_admin_token
from backend.models.schemas import (
    ChatRequest, ChatResponse, ModelInfo, LoadModelRequest, LoadModelResponse, UnloadModelResponse,
    DownloadModelRequest, DownloadModelResponse, CleanupRequest, CleanupResponse, PurgeLogsRequest, PurgeLogsResponse,
    SystemStatusResponse, GetParametersResponse, UpdateParametersRequest, UpdateParametersResponse, ResetParametersResponse
)

# Service singletons (to be replaced with DI/factory if needed)
from backend.services.model_manager import ModelManager
from backend.services.parameter_manager import ParameterManager
from backend.services.log_manager import LogManager
from backend.services.ai_model_runner import AIModelRunner
import time
import os

model_manager = ModelManager()
parameter_manager = ParameterManager()
log_manager = LogManager()
ai_runner = AIModelRunner()

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

# --- Chat Endpoint ---
@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(get_api_key)])
def chat(request: ChatRequest):
    log_manager.log_request(request.dict())
    loaded_model = model_manager.get_loaded_model()
    if not loaded_model:
        raise HTTPException(status_code=503, detail="No model loaded")
    params = parameter_manager.get_parameters(loaded_model.id).dict()
    if request.parameters:
        params.update(request.parameters)
    try:
        response_text = ai_runner.generate_response(request.message, params)
    except Exception as e:
        log_manager.log_response({"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
    resp = ChatResponse(
        response=response_text,
        model=loaded_model.name,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        parameters_used=params
    )
    log_manager.log_response(resp.dict())
    return resp

# --- Health Endpoint (already present) ---

# --- Model Management ---
@router.get("/models", response_model=list[ModelInfo], dependencies=[Depends(get_api_key)])
def list_models():
    return model_manager.list_models()

@router.post("/models/{model_id}/load", response_model=LoadModelResponse, dependencies=[Depends(get_api_key)])
def load_model(model_id: str, req: LoadModelRequest):
    try:
        model = model_manager.load_model(model_id, req.config)
        model_path = os.path.join(model_manager.model_cache_dir, model.id)
        ai_runner.load(model_path, model.format, req.config)
        resp = LoadModelResponse(
            status="success",
            message=f"Model {model_id} loaded",
            model_id=model_id,
            loaded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/models/{model_id}/unload", response_model=UnloadModelResponse, dependencies=[Depends(get_api_key)])
def unload_model(model_id: str):
    try:
        ok = model_manager.unload_model(model_id)
        if ok:
            ai_runner.unload()
            resp = UnloadModelResponse(
                status="success",
                message=f"Model {model_id} unloaded",
                model_id=model_id,
                unloaded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            )
            return resp
        else:
            raise Exception("Model not loaded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/models/download", response_model=DownloadModelResponse, dependencies=[Depends(get_api_key)])
def download_model(req: DownloadModelRequest):
    try:
        model_id = model_manager.download_model(req.model_name, req.model_format, req.auth_token)
        resp = DownloadModelResponse(
            status="success",
            message=f"Model {req.model_name} downloaded as {model_id}",
            model_id=model_id,
            download_progress=100.0,
            estimated_time="0s"
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Admin Endpoints ---
@router.post("/admin/cleanup", response_model=CleanupResponse, dependencies=[Depends(require_admin_token)])
def admin_cleanup(req: CleanupRequest):
    # For now, only log cleanup is implemented
    result = log_manager.cleanup_logs()
    return CleanupResponse(
        status="success",
        message="Cleanup completed",
        operations_completed=["clean_logs"],
        space_freed=result["space_freed"],
        started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@router.post("/admin/purge-logs", response_model=PurgeLogsResponse, dependencies=[Depends(require_admin_token)])
def admin_purge_logs(req: PurgeLogsRequest):
    result = log_manager.cleanup_logs(req.older_than_days, req.keep_latest_files, req.log_levels)
    return PurgeLogsResponse(
        status="success",
        message="Logs purged",
        files_removed=result["files_removed"],
        space_freed=result["space_freed"],
        purged_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@router.get("/admin/system-status", response_model=SystemStatusResponse, dependencies=[Depends(require_admin_token)])
def admin_system_status():
    # Simulate system status
    disk = os.statvfs("/")
    total = disk.f_frsize * disk.f_blocks
    free = disk.f_frsize * disk.f_bfree
    used = total - free
    mem = dict(total=0, used=0, free=0, usage_percent=0)  # Placeholder
    model_status = {
        "loaded_model": model_manager.loaded_model_id,
        "model_memory_usage": 0  # Placeholder
    }
    return SystemStatusResponse(
        status="healthy",
        disk_usage={"total": total, "used": used, "free": free, "usage_percent": round(used/total*100, 2) if total else 0},
        memory_usage=mem,
        model_status=model_status,
        last_cleanup=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

# --- Model Parameter Management ---
@router.get("/models/{model_id}/parameters", response_model=GetParametersResponse, dependencies=[Depends(get_api_key)])
def get_model_parameters(model_id: str):
    params = parameter_manager.get_parameters(model_id)
    return GetParametersResponse(
        model_id=model_id,
        parameters=params,
        last_updated=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@router.put("/models/{model_id}/parameters", response_model=UpdateParametersResponse, dependencies=[Depends(get_api_key)])
def update_model_parameters(model_id: str, req: UpdateParametersRequest):
    params = parameter_manager.update_parameters(model_id, req.parameters)
    return UpdateParametersResponse(
        status="success",
        message="Parameters updated",
        model_id=model_id,
        updated_parameters=req.parameters,
        updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@router.post("/models/{model_id}/parameters/reset", response_model=ResetParametersResponse, dependencies=[Depends(get_api_key)])
def reset_model_parameters(model_id: str):
    params = parameter_manager.reset_parameters(model_id)
    return ResetParametersResponse(
        status="success",
        message="Parameters reset to default",
        model_id=model_id,
        default_parameters=params,
        reset_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ) 