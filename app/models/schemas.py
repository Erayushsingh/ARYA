from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class FunctionCall(BaseModel):
    function_name: str
    parameters: Dict[str, Any]
    confidence: float

class FunctionCallRequest(BaseModel):
    prompt: str
    file_paths: List[str] = []

class FunctionCallResponse(BaseModel):
    success: bool
    message: str
    result_file_path: Optional[str] = None
    function_used: Optional[str] = None
    error_details: Optional[str] = None

class ImageCompressionParams(BaseModel):
    quality: int = 85
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    format: str = "JPEG"

class PdfConversionParams(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    margin: int = 50
