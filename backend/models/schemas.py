from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# --- Chat ---
class ChatRequest(BaseModel):
    message: str
    channel: str
    user_id: str
    parameters: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str
    parameters_used: Dict[str, Any]

# --- Model Management ---
class ModelParameters(BaseModel):
    temperature: Optional[float] = 1.0
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.9
    max_length: Optional[int] = 100
    repetition_penalty: Optional[float] = 1.0
    do_sample: Optional[bool] = True
    num_beams: Optional[int] = 1
    length_penalty: Optional[float] = 1.0
    early_stopping: Optional[bool] = False
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None

class ModelInfo(BaseModel):
    id: str
    name: str
    status: str
    description: Optional[str] = None
    format: Optional[str] = None
    size: Optional[int] = None
    source: Optional[str] = None
    parameters: Optional[ModelParameters] = None

class LoadModelRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None

class LoadModelResponse(BaseModel):
    status: str
    message: str
    model_id: str
    loaded_at: str

class UnloadModelResponse(BaseModel):
    status: str
    message: str
    model_id: str
    unloaded_at: str

class DownloadModelRequest(BaseModel):
    model_name: str
    model_format: Optional[str] = None
    auth_token: Optional[str] = None

class DownloadModelResponse(BaseModel):
    status: str
    message: str
    model_id: str
    download_progress: Optional[float] = None
    estimated_time: Optional[str] = None

# --- System Administration ---
class CleanupRequest(BaseModel):
    operations: List[str]
    force: Optional[bool] = False

class CleanupResponse(BaseModel):
    status: str
    message: str
    operations_completed: List[str]
    space_freed: int
    started_at: str

class PurgeLogsRequest(BaseModel):
    older_than_days: Optional[int] = 30
    keep_latest_files: Optional[int] = 100
    log_levels: Optional[List[str]] = None

class PurgeLogsResponse(BaseModel):
    status: str
    message: str
    files_removed: int
    space_freed: int
    purged_at: str

class SystemStatusResponse(BaseModel):
    status: str
    disk_usage: Dict[str, Any]
    memory_usage: Dict[str, Any]
    model_status: Dict[str, Any]
    last_cleanup: str

# --- Parameter Management ---
class GetParametersResponse(BaseModel):
    model_id: str
    parameters: ModelParameters
    last_updated: str

class UpdateParametersRequest(BaseModel):
    parameters: Dict[str, Any]

class UpdateParametersResponse(BaseModel):
    status: str
    message: str
    model_id: str
    updated_parameters: Dict[str, Any]
    updated_at: str

class ResetParametersResponse(BaseModel):
    status: str
    message: str
    model_id: str
    default_parameters: ModelParameters
    reset_at: str 