@echo off
echo 🚀 Starting LLM Function Calling FastAPI Application...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing/updating dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "app\file_handler\uploads" mkdir "app\file_handler\uploads"
if not exist "app\file_handler\outputs" mkdir "app\file_handler\outputs"

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo Please make sure your .env file exists with your API keys.
    echo.
)

REM Start the server
echo 🌐 Starting server...
echo 💡 Press Ctrl+C to stop the server
echo.

python main.py

pause
