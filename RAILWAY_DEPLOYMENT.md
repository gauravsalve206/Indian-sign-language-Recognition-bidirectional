# Deploy to Railway - Step by Step Guide

Railway is the **BEST free hosting option** for your Sign Language Recognition app because:
- ✅ Full WebSocket support (for real-time sign recognition)
- ✅ No file size limits (perfect for ML models)
- ✅ Excellent Python/ML support
- ✅ Free tier with $5 credit monthly
- ✅ Easy deployment from GitHub
- ✅ Auto-detects Python projects

---

## 🚀 Quick Deployment Steps

### Step 1: Prepare Your Repository

1. **Make sure your code is on GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/sign-lang.git
   git push -u origin main
   ```

2. **Verify these files exist:**
   - ✅ `requirements.txt`
   - ✅ `railway.json` (already created)
   - ✅ `src/server.py`
   - ✅ `frontend/` directory
   - ✅ `models/isl_lstm.h5`
   - ✅ `text_to_sign/ISL_Gifs/`

### Step 2: Deploy on Railway

1. **Go to Railway**
   - Visit: https://railway.app
   - Click "Start a New Project"
   - Sign up with GitHub (free)

2. **Create New Project**
   - Click "Deploy from GitHub repo"
   - Select your `sign-lang` repository
   - Railway will auto-detect Python

3. **Configure Settings**
   - Railway auto-detects everything!
   - Start Command: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
   - Port: Railway sets `$PORT` automatically
   - Python Version: Auto-detected (3.10+)

4. **Deploy**
   - Click "Deploy"
   - Wait 5-10 minutes for build
   - Railway installs dependencies automatically

5. **Get Your URL**
   - Once deployed, Railway gives you a URL like:
   - `https://your-app-name.up.railway.app`
   - Click "Generate Domain" for a custom domain (optional)

### Step 3: Update Frontend URLs (if needed)

If your frontend hardcodes `localhost:8000`, update it:

**File: `frontend/sign-to-text.html`**
```javascript
// Change this line (around line 49):
const WS_URL = "ws://localhost:8000/ws";

// To:
const WS_URL = window.location.protocol === 'https:' 
  ? `wss://${window.location.host}/ws`
  : `ws://${window.location.host}/ws`;
```

Or use this dynamic approach:
```javascript
// Auto-detect WebSocket URL
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = `${protocol}//${window.location.host}/ws`;
```

### Step 4: Test Your Deployment

1. Visit your Railway URL: `https://your-app-name.up.railway.app`
2. Test homepage
3. Test sign-to-text (WebSocket should work!)
4. Test text-to-sign

---

## 📋 Railway Configuration

### railway.json
Already created! This file tells Railway:
- Use Nixpacks builder (auto-detects Python)
- Start command for your FastAPI app
- Restart policy

### Environment Variables (Optional)

Railway auto-sets:
- `PORT` - Port number (auto-set)
- `PYTHON_VERSION` - Auto-detected

You can add custom variables in Railway dashboard:
- Settings → Variables → New Variable

---

## 💰 Railway Pricing

### Free Tier
- **$5 credit per month** (free!)
- Perfect for testing and small projects
- Pay-as-you-go after credit runs out

### Usage Estimate
- Your app uses ~$2-4/month on free tier
- ML models load on startup (one-time cost per deploy)
- WebSocket connections are free

---

## 🔧 Troubleshooting

### Issue: Build fails
**Solution:**
- Check Railway logs (View Logs button)
- Verify `requirements.txt` has all dependencies
- Check Python version compatibility

### Issue: WebSocket not connecting
**Solution:**
- Make sure frontend uses `wss://` (secure WebSocket) for HTTPS
- Check Railway logs for errors
- Verify WebSocket endpoint is `/ws`

### Issue: Model not loading
**Solution:**
- Check model file path in `src/config.py`
- Verify `models/isl_lstm.h5` is in repository
- Check Railway logs for file not found errors

### Issue: Out of memory
**Solution:**
- Railway free tier has memory limits
- Consider optimizing model (TensorFlow Lite)
- Or upgrade Railway plan

---

## 🎯 Railway vs Other Platforms

| Feature | Railway | Render | Heroku | Vercel |
|---------|---------|--------|--------|--------|
| WebSocket | ✅ | ✅ | ✅ | ❌ |
| ML Support | ✅✅✅ | ✅✅ | ✅ | ❌ |
| Free Tier | ✅ | ✅ | ❌ | ✅ |
| File Size Limit | None | 100MB | 500MB | 50MB |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**Railway wins for ML apps!** 🏆

---

## 📝 Additional Tips

### 1. Custom Domain (Free)
- Railway → Settings → Generate Domain
- Or add your own domain
- SSL certificate auto-configured

### 2. Monitoring
- Railway dashboard shows:
  - CPU usage
  - Memory usage
  - Request logs
  - Deployment history

### 3. Auto-Deploy
- Railway auto-deploys on `git push`
- Or disable in Settings → Source

### 4. Database (if needed later)
- Railway offers PostgreSQL, MySQL, Redis
- Add from dashboard → New → Database

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project deployed from GitHub
- [ ] Build successful (check logs)
- [ ] App accessible via Railway URL
- [ ] Frontend URLs updated (if needed)
- [ ] WebSocket connection working
- [ ] Sign recognition working
- [ ] Text-to-sign working

---

## 🚀 Quick Commands

### Deploy via Railway CLI (Alternative)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

But **GitHub deployment is easier!** Just connect repo in dashboard.

---

## 🎉 You're Done!

Your app is now live on Railway! 

**Next Steps:**
1. Share your Railway URL
2. Test all features
3. Monitor usage in Railway dashboard
4. Consider custom domain

**Need Help?**
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check Railway logs for errors

Happy deploying! 🚀

