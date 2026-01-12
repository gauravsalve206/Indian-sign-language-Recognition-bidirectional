# Deployment Guide for ISL Sign Language Recognition Project

## Project Analysis

### Project Structure
This is a **Sign Language Recognition Web Application** with the following components:

1. **Backend**: FastAPI server (`src/server.py` and `src/server_cnn.py`)
   - Real-time sign recognition using MediaPipe and TensorFlow
   - WebSocket support for live video processing
   - REST API endpoints for text-to-sign translation

2. **Frontend**: HTML/CSS/JavaScript (`frontend/`)
   - `index.html` - Landing page
   - `sign-to-text.html` - Real-time sign recognition
   - `text-to-sign.html` - Text to sign language conversion

3. **ML Models**: 
   - `models/isl_lstm.h5` - LSTM model for sequence recognition
   - `models/label_map.json` - Label mappings

4. **Assets**:
   - `text_to_sign/ISL_Gifs/` - Sign language GIF files
   - `dataset/` - Training data (.npy files)

5. **Dependencies**: Listed in `requirements.txt`

### Key Technologies
- **FastAPI** - Web framework
- **TensorFlow** - ML model inference
- **MediaPipe** - Hand/face/pose tracking
- **OpenCV** - Image processing
- **Uvicorn** - ASGI server

---

## Deployment Options

### Option 1: Cloud Platform (Recommended)
- **Heroku** - Easy deployment, free tier available
- **Railway** - Simple deployment, good for ML apps
- **Render** - Free tier, supports Python apps
- **AWS EC2** - Full control, scalable
- **Google Cloud Platform** - Good ML support
- **DigitalOcean** - Simple VPS option

### Option 2: VPS/Server
- **DigitalOcean Droplet**
- **Linode**
- **Vultr**
- **Any Linux VPS**

---

## Pre-Deployment Checklist

### Files to Include ✅
- `src/` - All Python source files
- `frontend/` - All HTML/CSS files
- `models/` - ML model files (.h5, .json)
- `text_to_sign/` - GIF assets
- `requirements.txt` - Python dependencies
- `config.py` - Configuration (if needed)

### Files to EXCLUDE ❌
- `myenv/` - Virtual environment (DO NOT UPLOAD)
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files
- `.git/` - Git repository (unless using Git deployment)
- `dataset/` - Training data (optional, large files)
- `video_dataset/` - Video files (optional)

---

## Deployment Steps

### Method 1: Deploy to Heroku (Easiest)

#### Step 1: Prepare Files
1. Create a `.gitignore` file:
```
myenv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist/
build/
.env
.venv
venv/
ENV/
```

2. Create `Procfile`:
```
web: uvicorn src.server:app --host 0.0.0.0 --port $PORT
```

3. Create `runtime.txt`:
```
python-3.10.18
```

#### Step 2: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

#### Step 3: Deploy
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Set buildpack (if needed)
heroku buildpacks:set heroku/python

# Deploy
git init
git add .
git commit -m "Initial deployment"
git push heroku main

# Open app
heroku open
```

**Note**: Heroku has file size limits. Large model files may need external storage (AWS S3, etc.)

---

### Method 2: Deploy to Railway

#### Step 1: Prepare Files
1. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Step 2: Deploy
1. Go to [railway.app](https://railway.app)
2. Create new project
3. Connect GitHub repository (or upload files)
4. Railway auto-detects Python and installs dependencies
5. Set start command: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`

---

### Method 3: Deploy to VPS (DigitalOcean/Linode/etc.)

#### Step 1: Server Setup
```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python 3.10 and pip
apt install python3.10 python3-pip python3-venv -y

# Install Nginx (for reverse proxy)
apt install nginx -y

# Install Supervisor (for process management)
apt install supervisor -y
```

#### Step 2: Upload Project Files
```bash
# Option A: Using Git
git clone your-repo-url
cd sign_lang

# Option B: Using SCP (from local machine)
scp -r /path/to/sign_lang root@your-server-ip:/var/www/
```

#### Step 3: Setup Python Environment
```bash
cd /var/www/sign_lang

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Test Server Locally
```bash
# Run server
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Test in browser: http://your-server-ip:8000
```

#### Step 5: Setup Supervisor (Process Manager)
Create `/etc/supervisor/conf.d/isl-app.conf`:
```ini
[program:isl-app]
command=/var/www/sign_lang/venv/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000
directory=/var/www/sign_lang
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/isl-app.err.log
stdout_logfile=/var/log/isl-app.out.log
environment=PATH="/var/www/sign_lang/venv/bin"
```

```bash
# Reload supervisor
supervisorctl reread
supervisorctl update
supervisorctl start isl-app
```

#### Step 6: Setup Nginx Reverse Proxy
Create `/etc/nginx/sites-available/isl-app`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/isl-app /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### Step 7: Setup SSL (Let's Encrypt)
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
certbot renew --dry-run
```

---

### Method 4: Deploy to Render

#### Step 1: Prepare Files
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: isl-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.18
```

#### Step 2: Deploy
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Render auto-detects settings
5. Deploy!

---

## Environment Variables (Optional)

Create `.env` file for sensitive configs:
```bash
# .env
PORT=8000
ENVIRONMENT=production
```

Update `src/server.py` to load env vars if needed:
```python
import os
from dotenv import load_dotenv
load_dotenv()
```

---

## Important Notes

### 1. Model File Size
- ML models can be large (100MB+)
- Some platforms have file size limits
- Consider using cloud storage (S3, GCS) for large files

### 2. WebSocket Support
- Ensure your hosting platform supports WebSocket
- Nginx config must include WebSocket headers (shown above)

### 3. Camera Access
- Users need HTTPS for camera access in browsers
- Always use SSL certificate in production

### 4. Performance
- MediaPipe and TensorFlow are resource-intensive
- Minimum recommended: 2GB RAM, 2 CPU cores
- Consider GPU instances for better performance

### 5. CORS Configuration
- Current config allows all origins (`allow_origins=["*"]`)
- For production, restrict to your domain:
```python
allow_origins=["https://your-domain.com"]
```

---

## Testing Deployment

### Local Testing
```bash
# Test server
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/labels
```

### Production Testing
1. Check homepage loads: `https://your-domain.com`
2. Test sign-to-text: Navigate to `/sign-to-text.html`
3. Test text-to-sign: Navigate to `/text-to-sign.html`
4. Check WebSocket connection in browser console

---

## Troubleshooting

### Issue: Server won't start
- Check Python version (needs 3.10+)
- Verify all dependencies installed
- Check port availability

### Issue: WebSocket not working
- Verify Nginx WebSocket config
- Check firewall rules
- Ensure HTTPS is enabled

### Issue: Model not loading
- Verify model file path
- Check file permissions
- Ensure model file uploaded correctly

### Issue: Camera not accessing
- Must use HTTPS (not HTTP)
- Check browser permissions
- Verify CORS settings

---

## Quick Start Commands

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.server:app --reload --port 8000
```

### Production Server
```bash
# Run with production settings
uvicorn src.server:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Recommended Hosting Platforms Comparison

| Platform | Ease | Cost | ML Support | Best For |
|----------|------|------|------------|----------|
| Heroku | ⭐⭐⭐⭐⭐ | $$$ | ⭐⭐⭐ | Quick deployment |
| Railway | ⭐⭐⭐⭐ | $$ | ⭐⭐⭐⭐ | ML apps |
| Render | ⭐⭐⭐⭐ | $ | ⭐⭐⭐ | Budget-friendly |
| VPS | ⭐⭐ | $ | ⭐⭐⭐⭐⭐ | Full control |
| AWS/GCP | ⭐⭐ | $$$ | ⭐⭐⭐⭐⭐ | Enterprise |

---

## Next Steps

1. Choose deployment method
2. Prepare files (create .gitignore, Procfile, etc.)
3. Deploy to chosen platform
4. Test all features
5. Setup monitoring (optional)
6. Configure domain name
7. Enable SSL certificate

---

## Support

For issues:
1. Check server logs
2. Verify file paths
3. Test endpoints individually
4. Check browser console for frontend errors

Good luck with your deployment! 🚀

