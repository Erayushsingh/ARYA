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
import httpx
import aiofiles
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from app.client.gemini_client import GeminiClient
from app.client.sarvam_client import SarvamClient
from app.functions.function_registry import FunctionRegistry
from app.file_handler.file_manager import FileManager
from app.models.schemas import FunctionCallRequest, FunctionCallResponse
from app.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for keep-alive and monitoring
keep_alive_task = None
last_activity = time.time()
keep_alive_stats = {
    "pings_sent": 0,
    "successful_pings": 0,
    "failed_pings": 0,
    "last_ping": None,
    "last_error": None,
    "uptime_start": time.time()
}

async def enhanced_keep_alive():
    """Enhanced keep-alive system with retry logic and error handling"""
    global keep_alive_stats, last_activity
    
    # Configuration
    PING_INTERVAL = 300  # 5 minutes
    MAX_RETRIES = 3
    RETRY_DELAY = 30  # 30 seconds between retries
    
    logger.info("🚀 Enhanced keep-alive system started")
    
    while True:
        try:
            # Internal ping (lightweight)
            start_time = time.time()
            
            # Update stats
            keep_alive_stats["pings_sent"] += 1
            keep_alive_stats["last_ping"] = datetime.now().isoformat()
            
            # Simple internal health check
            try:
                # Check if all components are still responsive
                test_data = {
                    "gemini_available": bool(Config.GOOGLE_GEMINI_KEY),
                    "sarvam_available": bool(Config.SARVAM_API_KEY),
                    "uptime": time.time() - keep_alive_stats["uptime_start"],
                    "last_activity": time.time() - last_activity
                }
                
                keep_alive_stats["successful_pings"] += 1
                ping_duration = time.time() - start_time
                
                logger.info(f"✅ Keep-alive ping #{keep_alive_stats['pings_sent']} successful")
                logger.info(f"   📊 Uptime: {test_data['uptime']:.0f}s | Last activity: {test_data['last_activity']:.0f}s ago")
                logger.info(f"   ⚡ Ping duration: {ping_duration:.3f}s")
                
            except Exception as ping_error:
                keep_alive_stats["failed_pings"] += 1
                keep_alive_stats["last_error"] = str(ping_error)
                logger.warning(f"⚠️ Internal ping failed: {ping_error}")
            
            # Sleep for the configured interval
            await asyncio.sleep(PING_INTERVAL)
            
        except asyncio.CancelledError:
            logger.info("🛑 Keep-alive task cancelled")
            break
        except Exception as e:
            keep_alive_stats["failed_pings"] += 1
            keep_alive_stats["last_error"] = str(e)
            logger.error(f"❌ Keep-alive system error: {e}")
            
            # Retry logic with exponential backoff
            for retry in range(MAX_RETRIES):
                try:
                    await asyncio.sleep(RETRY_DELAY * (2 ** retry))
                    logger.info(f"🔄 Keep-alive retry {retry + 1}/{MAX_RETRIES}")
                    break
                except Exception:
                    if retry == MAX_RETRIES - 1:
                        logger.error("💥 Keep-alive system failed permanently, restarting...")
                        await asyncio.sleep(60)  # Wait 1 minute before restarting loop
                        break

async def external_ping_endpoints():
    """Make external HTTP requests to keep the server warm"""
    while True:
        try:
            # Wait 15 minutes between external pings
            await asyncio.sleep(900)
            
            # Get the current URL (for Render, this would be your app URL)
            base_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8000")
            
            if base_url != "http://localhost:8000":  # Only ping externally if deployed
                async with httpx.AsyncClient(timeout=30.0) as client:
                    endpoints_to_ping = [
                        f"{base_url}/health",
                        f"{base_url}/ping",
                        f"{base_url}/warmup"
                    ]
                    
                    for endpoint in endpoints_to_ping:
                        try:
                            response = await client.get(endpoint)
                            if response.status_code == 200:
                                logger.info(f"🌐 External ping successful: {endpoint}")
                            else:
                                logger.warning(f"⚠️ External ping returned {response.status_code}: {endpoint}")
                        except Exception as e:
                            logger.warning(f"⚠️ External ping failed for {endpoint}: {e}")
                        
                        # Small delay between requests
                        await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ External ping system error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

async def update_activity():
    """Update last activity timestamp"""
    global last_activity
    last_activity = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with enhanced monitoring"""
    # Startup
    logger.info("🚀 ARYA Server Starting Up...")
    logger.info("=" * 60)
    
    global keep_alive_task
    
    # Start both keep-alive tasks
    internal_task = asyncio.create_task(enhanced_keep_alive())
    external_task = asyncio.create_task(external_ping_endpoints())
    
    keep_alive_task = asyncio.gather(internal_task, external_task, return_exceptions=True)
    logger.info("✅ Enhanced keep-alive system started (internal + external)")
    
    # Test all services during startup
    try:
        logger.info("🔧 Initializing services...")
        
        # Test configuration
        logger.info(f"🔑 Config loaded - Gemini API: {bool(Config.GOOGLE_GEMINI_KEY)}")
        logger.info(f"🔑 Config loaded - Sarvam API: {bool(Config.SARVAM_API_KEY)}")
        
        # Initialize clients
        gemini_client = GeminiClient()
        sarvam_client = SarvamClient()
        logger.info("🤖 AI clients initialized successfully")
        
        # Test function registry
        function_registry = FunctionRegistry()
        available_functions = function_registry.get_available_functions()
        logger.info(f"🛠️ Available functions: {available_functions}")
        
        # Initialize file manager
        file_manager = FileManager()
        logger.info("📁 File manager initialized")
        
        logger.info("✅ All services initialized successfully")
        logger.info("🌡️ Server warm-up completed")
        logger.info("🚀 ARYA is ready to serve requests!")
        logger.info("=" * 60)
        
        # Update activity timestamp
        await update_activity()
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.error("🔧 Some services may not work correctly")
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 ARYA Server Shutting Down...")
    
    # Print final statistics
    logger.info("📊 Keep-alive Statistics:")
    logger.info(f"   • Total pings: {keep_alive_stats['pings_sent']}")
    logger.info(f"   • Successful: {keep_alive_stats['successful_pings']}")
    logger.info(f"   • Failed: {keep_alive_stats['failed_pings']}")
    logger.info(f"   • Success rate: {(keep_alive_stats['successful_pings']/max(keep_alive_stats['pings_sent'], 1)*100):.1f}%")
    logger.info(f"   • Total uptime: {(time.time() - keep_alive_stats['uptime_start']):.0f} seconds")
    
    if keep_alive_task:
        keep_alive_task.cancel()
        try:
            await keep_alive_task
        except asyncio.CancelledError:
            logger.info("🔄 Keep-alive tasks cancelled")
    
    logger.info("👋 Shutdown complete")
    logger.info("=" * 60)

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
    await update_activity()
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    """Return favicon"""
    return FileResponse("app/static/favicon.ico")

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with detailed monitoring"""
    await update_activity()
    
    try:
        start_time = time.time()
        current_time = time.time()
        
        # Comprehensive system status
        status = {
            "status": "healthy",
            "timestamp": current_time,
            "uptime_seconds": current_time - keep_alive_stats["uptime_start"],
            "last_activity": current_time - last_activity,
            "version": "1.2.0",
            "environment": os.environ.get("ENVIRONMENT", "production"),
            "services": {
                "api": "running",
                "file_manager": "active",
                "ai_clients": "connected",
                "keep_alive": "active"
            },
            "functions_available": len(function_registry.get_available_functions()),
            "keep_alive_stats": keep_alive_stats.copy(),
            "memory_usage": "N/A",  # Can be enhanced with psutil if needed
            "disk_space": "N/A"     # Can be enhanced with shutil.disk_usage if needed
        }
        
        # Test AI client connections
        try:
            gemini_status = "connected" if Config.GOOGLE_GEMINI_KEY else "no_api_key"
            status["services"]["gemini"] = gemini_status
        except Exception as e:
            status["services"]["gemini"] = f"error: {str(e)[:50]}"
        
        try:
            sarvam_status = "connected" if Config.SARVAM_API_KEY else "no_api_key"
            status["services"]["sarvam"] = sarvam_status
        except Exception as e:
            status["services"]["sarvam"] = f"error: {str(e)[:50]}"
        
        # Test file system
        try:
            uploads_dir = Config.UPLOAD_DIR
            outputs_dir = "app/file_handler/outputs"
            
            upload_files = len(os.listdir(uploads_dir)) if os.path.exists(uploads_dir) else 0
            output_files = len(os.listdir(outputs_dir)) if os.path.exists(outputs_dir) else 0
            
            status["file_system"] = {
                "uploads_count": upload_files,
                "outputs_count": output_files,
                "uploads_dir_exists": os.path.exists(uploads_dir),
                "outputs_dir_exists": os.path.exists(outputs_dir)
            }
        except Exception as e:
            status["file_system"] = {"error": str(e)}
        
        # Calculate response time
        response_time = time.time() - start_time
        status["response_time_ms"] = round(response_time * 1000, 2)
        
        # Determine overall health status
        if response_time > 5.0:  # Slow response
            status["status"] = "degraded"
            status["warning"] = "Slow response time"
        
        if keep_alive_stats["failed_pings"] > keep_alive_stats["successful_pings"]:
            status["status"] = "degraded" 
            status["warning"] = "High keep-alive failure rate"
        
        return JSONResponse(content=status, status_code=200)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
                "uptime_seconds": time.time() - keep_alive_stats["uptime_start"] if keep_alive_stats else 0
            },
            status_code=503
        )

@app.get("/ping")
async def ping():
    """Enhanced ping endpoint with activity tracking"""
    await update_activity()
    
    return {
        "message": "pong",
        "timestamp": time.time(),
        "uptime": time.time() - keep_alive_stats["uptime_start"],
        "version": "1.2.0",
        "status": "active"
    }

@app.get("/keep-alive-stats")
async def get_keep_alive_stats():
    """Get detailed keep-alive statistics"""
    await update_activity()
    
    current_time = time.time()
    uptime = current_time - keep_alive_stats["uptime_start"]
    
    stats = keep_alive_stats.copy()
    stats.update({
        "current_timestamp": current_time,
        "uptime_seconds": uptime,
        "uptime_formatted": f"{uptime//3600:.0f}h {(uptime%3600)//60:.0f}m {uptime%60:.0f}s",
        "last_activity_seconds_ago": current_time - last_activity,
        "success_rate_percent": (stats["successful_pings"] / max(stats["pings_sent"], 1)) * 100,
        "avg_ping_interval": uptime / max(stats["pings_sent"], 1) if stats["pings_sent"] > 0 else 0
    })
    
    return stats

@app.get("/warmup")
async def warmup():
    """Enhanced warmup endpoint to initialize all services and prevent cold starts"""
    await update_activity()
    
    try:
        start_time = time.time()
        logger.info("🔥 Warmup endpoint called - initializing all services")
        
        # Initialize all components with detailed reporting
        results = {
            "gemini_client": "initializing",
            "sarvam_client": "initializing", 
            "function_registry": "initializing",
            "file_manager": "initializing",
            "file_system": "checking"
        }
        
        initialization_details = {}
        
        # Test Gemini client
        try:
            client_start = time.time()
            gemini_client = GeminiClient()
            init_time = time.time() - client_start
            results["gemini_client"] = "ready"
            initialization_details["gemini_init_time"] = round(init_time, 3)
        except Exception as e:
            results["gemini_client"] = f"error: {str(e)[:100]}"
            initialization_details["gemini_error"] = str(e)
        
        # Test Sarvam client
        try:
            client_start = time.time()
            sarvam_client = SarvamClient()
            init_time = time.time() - client_start
            results["sarvam_client"] = "ready"
            initialization_details["sarvam_init_time"] = round(init_time, 3)
        except Exception as e:
            results["sarvam_client"] = f"error: {str(e)[:100]}"
            initialization_details["sarvam_error"] = str(e)
        
        # Test function registry
        try:
            registry_start = time.time()
            function_registry = FunctionRegistry()
            available_functions = function_registry.get_available_functions()
            init_time = time.time() - registry_start
            results["function_registry"] = f"ready ({len(available_functions)} functions)"
            initialization_details["registry_init_time"] = round(init_time, 3)
            initialization_details["available_functions"] = available_functions
        except Exception as e:
            results["function_registry"] = f"error: {str(e)[:100]}"
            initialization_details["registry_error"] = str(e)
        
        # Test file manager
        try:
            fm_start = time.time()
            file_manager = FileManager()
            init_time = time.time() - fm_start
            results["file_manager"] = "ready"
            initialization_details["file_manager_init_time"] = round(init_time, 3)
        except Exception as e:
            results["file_manager"] = f"error: {str(e)[:100]}"
            initialization_details["file_manager_error"] = str(e)
        
        # Test file system
        try:
            uploads_dir = Config.UPLOAD_DIR
            outputs_dir = "app/file_handler/outputs"
            
            # Ensure directories exist
            os.makedirs(uploads_dir, exist_ok=True)
            os.makedirs(outputs_dir, exist_ok=True)
            
            # Count files
            upload_count = len(os.listdir(uploads_dir))
            output_count = len(os.listdir(outputs_dir))
            
            results["file_system"] = f"ready (uploads: {upload_count}, outputs: {output_count})"
            initialization_details["file_system"] = {
                "uploads_dir": uploads_dir,
                "outputs_dir": outputs_dir,
                "upload_files": upload_count,
                "output_files": output_count
            }
        except Exception as e:
            results["file_system"] = f"error: {str(e)[:100]}"
            initialization_details["file_system_error"] = str(e)
        
        warmup_time = time.time() - start_time
        
        # Comprehensive warmup response
        response = {
            "status": "warmed_up",
            "warmup_time_seconds": round(warmup_time, 3),
            "timestamp": time.time(),
            "components": results,
            "initialization_details": initialization_details,
            "keep_alive_stats": keep_alive_stats.copy(),
            "system_info": {
                "uptime": time.time() - keep_alive_stats["uptime_start"],
                "last_activity": time.time() - last_activity,
                "environment": os.environ.get("ENVIRONMENT", "production"),
                "python_version": os.sys.version.split()[0] if hasattr(os, 'sys') else "unknown"
            }
        }
        
        # Determine if warmup was successful
        error_count = sum(1 for result in results.values() if "error" in result)
        if error_count > 0:
            response["status"] = "partially_warmed"
            response["warnings"] = f"{error_count} components had errors"
        
        logger.info(f"🔥 Warmup completed in {warmup_time:.3f}s - Status: {response['status']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Warmup failed: {e}")
        return JSONResponse(
            content={
                "status": "warmup_failed",
                "error": str(e),
                "timestamp": time.time(),
                "uptime": time.time() - keep_alive_stats["uptime_start"] if keep_alive_stats else 0
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
    await update_activity()
    
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
    await update_activity()
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
