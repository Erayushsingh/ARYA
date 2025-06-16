# Railway Deployment Guide for ARYA

## Quick Deploy to Railway:

1. **Create Railway Account:** https://railway.app
2. **Connect GitHub:** Link your repository
3. **Deploy:** Railway auto-detects Python and uses nixpacks.toml
4. **Environment Variables:** Add your API keys in Railway dashboard

## Required Environment Variables:
- `GOOGLE_GEMINI_KEY` = your_gemini_api_key
- `SARVAM_API_KEY` = your_sarvam_api_key  
- `PORT` = $PORT (Railway sets this automatically)

## Benefits:
- ✅ No cold starts
- ✅ $5 free monthly credits
- ✅ Fast deployment
- ✅ Automatic HTTPS
- ✅ Custom domains
