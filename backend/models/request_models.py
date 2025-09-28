# models/request_models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class NavigationOptions(BaseModel):
    headless: bool = True
    timeout: int = 30000
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None

class NavigationRequest(BaseModel):
    instruction: str
    session_id: Optional[str] = None
    options: Optional[NavigationOptions] = NavigationOptions()

class NavigationResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str
    execution_time: float
    session_id: Optional[str] = None

