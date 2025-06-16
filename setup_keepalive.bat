@echo off
echo 🚀 ARYA Keep-Alive Setup
echo.
echo This script helps prevent cold starts on Render by pinging your app regularly.
echo.
echo STEP 1: Update your Render app URL
echo Open keep_alive.py and replace "https://your-app-name.onrender.com" with your actual URL
echo.
echo STEP 2: Test the script
echo Run: python keep_alive.py
echo.
echo STEP 3: For better reliability, use UptimeRobot instead:
echo 1. Go to https://uptimerobot.com (free tier available)
echo 2. Create a new HTTP monitor
echo 3. Set URL to: https://your-app-name.onrender.com/health
echo 4. Set monitoring interval to 5 minutes
echo 5. This will keep your app alive automatically!
echo.
echo CURRENT STATUS:
echo Checking if Python is available...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)
echo.
echo ✅ Python is available
echo.
echo To start keep-alive service, run:
echo python keep_alive.py
echo.
pause
