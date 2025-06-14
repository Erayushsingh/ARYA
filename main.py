from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
import os
from typing import Optional

from app.client.gemini_client import GeminiClient
from app.functions.function_registry import FunctionRegistry
from app.file_handler.file_manager import FileManager
from app.models.schemas import FunctionCallRequest, FunctionCallResponse

app = FastAPI(title="LLM Function Calling API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize components
gemini_client = GeminiClient()
function_registry = FunctionRegistry()
file_manager = FileManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface for the application"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_model=FunctionCallResponse)
async def process_request(
    request: Request,
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    """Process user prompt and files using LLM function calling"""
    try:
        # Save uploaded files
        file_paths = []
        for file in files:
            if file.filename:
                file_path = await file_manager.save_upload(file)
                file_paths.append(file_path)
        
        # Parse prompt and determine function to call
        function_call = await gemini_client.parse_prompt_for_function(prompt, file_paths)
        
        # Execute the determined function
        result = await function_registry.execute_function(
            function_call.function_name,
            function_call.parameters,
            file_paths
        )
        
        return FunctionCallResponse(
            success=True,
            message="Processing completed successfully",
            result_file_path=result.get("output_path"),
            function_used=function_call.function_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download processed file"""
    full_path = os.path.join("app/file_handler/outputs", file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    filename = os.path.basename(full_path)
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
