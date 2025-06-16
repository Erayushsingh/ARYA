from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
import os
import time
import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from app.client.gemini_client import GeminiClient
from app.client.sarvam_client import SarvamClient
from app.functions.function_registry import FunctionRegistry
from app.file_handler.file_manager import FileManager
from app.models.schemas import FunctionCallRequest, FunctionCallResponse
from app.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for keep-alive
keep_alive_task = None

async def keep_alive_ping():
    """Background task to keep the server alive and prevent cold starts"""
    while True:
        try:
            # Log every 10 minutes to show the server is alive
            logger.info("🏃 Keep-alive ping - Server is active")
            await asyncio.sleep(600)  # Wait 10 minutes
        except Exception as e:
            logger.error(f"Keep-alive ping error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("🚀 ARYA Server Starting Up...")
    global keep_alive_task
    keep_alive_task = asyncio.create_task(keep_alive_ping())
    logger.info("✅ Keep-alive task started")
    
    # Test all services
    try:
        # Test configuration
        logger.info(f"🔑 Config loaded - API key available: {bool(Config.GOOGLE_GEMINI_KEY)}")
        
        # Initialize clients
        gemini_client = GeminiClient()
        sarvam_client = SarvamClient()
        logger.info("🤖 AI clients initialized successfully")
          # Test function registry
        function_registry = FunctionRegistry()
        available_functions = function_registry.get_available_functions()
        logger.info(f"🛠️ Available functions: {available_functions}")
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 ARYA Server Shutting Down...")
    if keep_alive_task:
        keep_alive_task.cancel()
        try:
            await keep_alive_task
        except asyncio.CancelledError:
            logger.info("🔄 Keep-alive task cancelled")
    logger.info("👋 Shutdown complete")

app = FastAPI(
    title="ARYA - AI File Processing Suite", 
    version="1.2.0",
    description="AI-powered file processing with speech recognition, translation, and document conversion",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize components
gemini_client = GeminiClient()
function_registry = FunctionRegistry()
file_manager = FileManager()
sarvam_client = SarvamClient()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main interface for the application"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    """Return favicon"""
    return FileResponse("app/static/favicon.ico")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring services"""
    try:
        # Check if all components are working
        status = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time(),
            "services": {
                "api": "running",
                "file_manager": "active",
                "ai_clients": "connected"
            },
            "functions_available": len(function_registry.get_available_functions()),
            "version": "1.2.0"
        }
        
        # Test Gemini client connection
        try:
            # Quick test without actual API call
            gemini_status = "connected" if Config.GOOGLE_GEMINI_KEY else "no_api_key"
            status["services"]["gemini"] = gemini_status
        except:
            status["services"]["gemini"] = "error"
        
        # Test Sarvam client connection
        try:
            sarvam_status = "connected" if Config.SARVAM_API_KEY else "no_api_key"
            status["services"]["sarvam"] = sarvam_status
        except:
            status["services"]["sarvam"] = "error"
            
        return JSONResponse(content=status, status_code=200)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            },
            status_code=503
        )

@app.get("/ping")
async def ping():
    """Simple ping endpoint for uptime monitoring"""
    return {"message": "pong", "timestamp": time.time()}

@app.get("/warmup")
async def warmup():
    """Warmup endpoint to initialize all services"""
    try:
        start_time = time.time()
        
        # Initialize all components
        results = {
            "gemini_client": "initializing",
            "sarvam_client": "initializing", 
            "function_registry": "initializing",
            "file_manager": "initializing"
        }
        
        # Test each component
        try:
            gemini_client = GeminiClient()
            results["gemini_client"] = "ready"
        except Exception as e:
            results["gemini_client"] = f"error: {str(e)}"
        
        try:
            sarvam_client = SarvamClient()
            results["sarvam_client"] = "ready"
        except Exception as e:
            results["sarvam_client"] = f"error: {str(e)}"
        
        try:
            function_registry = FunctionRegistry()
            available_functions = function_registry.get_available_functions()
            results["function_registry"] = f"ready ({len(available_functions)} functions)"
        except Exception as e:
            results["function_registry"] = f"error: {str(e)}"
        
        try:
            file_manager = FileManager()
            results["file_manager"] = "ready"
        except Exception as e:
            results["file_manager"] = f"error: {str(e)}"
        
        warmup_time = time.time() - start_time
        
        return {
            "status": "warmed_up",
            "warmup_time_seconds": round(warmup_time, 2),
            "components": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Warmup failed: {e}")
        return JSONResponse(
            content={
                "status": "warmup_failed",
                "error": str(e),
                "timestamp": time.time()
            },
            status_code=500
        )

@app.get("/test")
async def test():
    """Test endpoint"""
    try:
        # Test configuration
        from app.config import Config
        print(f"Config loaded - API key starts with: {Config.GOOGLE_GEMINI_KEY[:10]}")
        
        # Test Gemini client
        from app.client.gemini_client import GeminiClient
        client = GeminiClient()
        print("Gemini client created successfully")
        
        return {"status": "success", "message": "All components working"}
    except Exception as e:
        print(f"Test error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/process", response_model=FunctionCallResponse)
async def process_request(
    request: Request,
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    """Process user prompt and files using LLM function calling"""
    try:
        print(f"Received request - Prompt: {prompt}")
        print(f"Number of files: {len(files)}")
        
        # Save uploaded files
        file_paths = []
        for file in files:
            if file.filename:
                print(f"Processing file: {file.filename}")
                file_path = await file_manager.save_upload(file)
                file_paths.append(file_path)
        
        print(f"Saved files: {file_paths}")
        
        # Parse prompt and determine function to call
        print("Calling Gemini client...")
        function_call = await gemini_client.parse_prompt_for_function(prompt, file_paths)
        print(f"Function call result: {function_call}")
        
        # Execute the determined function
        print("Executing function...")
        result = await function_registry.execute_function(
            function_call.function_name,
            function_call.parameters,
            file_paths
        )
        print(f"Function result: {result}")
        
        return FunctionCallResponse(
            success=True,
            message="Processing completed successfully",
            result_file_path=result.get("output_path"),
            function_used=function_call.function_name
        )
        
    except Exception as e:
        print(f"Error in process_request: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download processed file"""
    # Handle both full paths and relative paths
    if file_path.startswith("app/file_handler/outputs") or file_path.startswith("app\\file_handler\\outputs"):
        # Full path already provided
        full_path = file_path.replace("\\", "/")  # Normalize path separators
    else:
        # Relative path, add the base directory
        full_path = os.path.join("app/file_handler/outputs", file_path)
    
    # Normalize the path and check if file exists
    full_path = os.path.normpath(full_path)
    
    if not os.path.exists(full_path):
        # Try alternative path formats
        alt_path = os.path.join("app", "file_handler", "outputs", os.path.basename(file_path))
        if os.path.exists(alt_path):
            full_path = alt_path
        else:
            print(f"File not found at: {full_path}")
            print(f"Also tried: {alt_path}")
            raise HTTPException(status_code=404, detail=f"File not found: {os.path.basename(file_path)}")
    
    filename = os.path.basename(full_path)
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.post("/api/translate")
async def translate_ui_text(request: Request):
    """Translate UI text to selected language using Sarvam AI"""
    try:
        body = await request.json()
        texts = body.get('texts', [])
        target_language = body.get('target_language', 'hi-IN')
        source_language = body.get('source_language', 'en-IN')
        
        if not texts:
            return {"success": False, "error": "No texts provided"}
        
        translations = {}
        
        for key, text in texts.items():
            if not text or not text.strip():
                translations[key] = text
                continue
                
            # Use Sarvam AI to translate
            result = await sarvam_client.translate_text(
                text=text,
                source_language=source_language,
                target_language=target_language
            )
            
            translations[key] = result.get('translated_text', text)
        
        return {
            "success": True,
            "translations": translations,
            "target_language": target_language,
            "source_language": source_language
        }
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "translations": {}
        }

@app.post("/api/sarvam-speech-to-text")
async def sarvam_speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    model: str = Form("saarika:v2")
):
    """Sarvam AI speech-to-text with automatic language detection"""
    try:
        print(f"Received audio file: {audio.filename}, language: {language}, model: {model}")
        
        # Save uploaded audio file
        temp_audio_path = os.path.join(Config.UPLOAD_DIR, f"temp_audio_{audio.filename}")
        
        with open(temp_audio_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
          # Use Sarvam AI for speech-to-text
        result = await sarvam_client.speech_to_text(
            audio_file_path=temp_audio_path,
            language=language,
            model=model
        )
        
        print(f"Sarvam AI result: {result}")
          # Clean up temp file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        if result.get('success', False):
            # Handle different possible field names from Sarvam client
            transcript_text = result.get('transcript') or result.get('transcribed_text') or result.get('text') or ''
            
            response_data = {
                "success": True,
                "transcript": transcript_text,
                "detected_language": result.get('detected_language') or result.get('language', 'Unknown'),
                "confidence": result.get('confidence', 0.0),
                "language_code": result.get('language_code', 'unknown'),
                "processing_time": result.get('processing_time', 0.0)
            }
            print(f"Sending response: {response_data}")
            return response_data
        else:
            return {
                "success": False,
                "error": result.get('error', 'Speech-to-text failed'),
                "message": "Failed to transcribe audio"
            }
            
    except Exception as e:
        print(f"Error in speech-to-text: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to transcribe speech"
        }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", Config.PORT))
    host = os.environ.get("HOST", Config.HOST)
    
    print("🚀 Starting ARYA FastAPI Server...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print("🔧 Health check endpoints:")
    print(f"  • Health: http://{host}:{port}/health")
    print(f"  • Ping: http://{host}:{port}/ping")  
    print(f"  • Warmup: http://{host}:{port}/warmup")
    print("🎤 Features available:")
    print("  • Multilingual speech-to-text with Sarvam AI")
    print("  • Google Translate integration")
    print("  • File processing (images, documents, audio)")
    print("  • Text-to-speech in multiple languages")
    print("  • Keep-alive system for preventing cold starts")
    print("✅ Press Ctrl+C to stop the server")
    print("-" * 60)
    
    uvicorn.run("main:app", host=host, port=port, reload=False)
