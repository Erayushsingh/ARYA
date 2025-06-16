#!/usr/bin/env python3
"""
Keep-Alive Script for ARYA on Render
This script pings your deployed app every 10 minutes to prevent cold starts.

Usage:
1. Replace YOUR_APP_URL with your actual Render app URL
2. Run: python keep_alive.py
3. Or set up a cron job to run this automatically

For better reliability, use UptimeRobot or similar monitoring service instead.
"""

import requests
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
APP_URL = "https://your-app-name.onrender.com"  # Replace with your actual URL
PING_INTERVAL = 600  # 10 minutes in seconds
TIMEOUT = 30  # Request timeout in seconds

def ping_app():
    """Ping the app to keep it alive"""
    try:
        # Try health check endpoint first
        health_url = f"{APP_URL}/health"
        response = requests.get(health_url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Health check successful - Status: {data.get('status', 'unknown')}")
            return True
        else:
            logger.warning(f"⚠️ Health check returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Health check failed: {e}")
    
    # Fallback to ping endpoint
    try:
        ping_url = f"{APP_URL}/ping"
        response = requests.get(ping_url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Ping successful - Message: {data.get('message', 'pong')}")
            return True
        else:
            logger.warning(f"⚠️ Ping returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ping failed: {e}")
    
    # Final fallback to home page
    try:
        response = requests.get(APP_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            logger.info("✅ Home page accessible")
            return True
        else:
            logger.error(f"❌ Home page returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Home page failed: {e}")
    
    return False

def main():
    """Main keep-alive loop"""
    if APP_URL == "https://your-app-name.onrender.com":
        logger.error("❌ Please update APP_URL with your actual Render app URL!")
        return
    
    logger.info(f"🚀 Starting keep-alive service for: {APP_URL}")
    logger.info(f"🕐 Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL//60} minutes)")
    logger.info("💡 Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"🏃 Keep-alive ping at {current_time}")
            
            success = ping_app()
            
            if success:
                logger.info(f"✅ App is alive and responding")
            else:
                logger.error("❌ All ping attempts failed - app may be down")
            
            logger.info(f"⏰ Next ping in {PING_INTERVAL//60} minutes...")
            print("-" * 40)
            
            time.sleep(PING_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("🛑 Keep-alive service stopped by user")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
