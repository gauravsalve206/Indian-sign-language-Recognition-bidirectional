# 🚀 Quick Start: Deploy to Railway (FREE)

## Why Railway?
- ✅ **FREE** - $5 credit monthly (perfect for your app)
- ✅ **WebSocket Support** - Real-time sign recognition works!
- ✅ **No File Limits** - ML models upload fine
- ✅ **Easy** - Deploy in 5 minutes
- ✅ **Auto-Deploy** - Updates on every git push

---

## ⚡ 3-Step Deployment

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/sign-lang.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select your repository
5. **Done!** Railway auto-detects everything

### Step 3: Get Your URL
- Railway gives you a URL like: `https://your-app.up.railway.app`
- Click **"Generate Domain"** for custom domain (optional)

---

## ✅ That's It!

Your app is live! Test it:
- Homepage: `https://your-app.up.railway.app`
- Sign to Text: `/sign-to-text.html`
- Text to Sign: `/text-to-sign.html`

---

## 📝 Files Already Configured

✅ `railway.json` - Railway config (already created)
✅ `requirements.txt` - Dependencies
✅ `frontend/` - Updated for production URLs
✅ `.gitignore` - Excludes virtual env

---

## 🐛 Troubleshooting

**Build fails?**
- Check Railway logs (click "View Logs")
- Verify all files are in GitHub repo

**WebSocket not working?**
- Frontend auto-detects URLs (already fixed!)
- Make sure you're using HTTPS

**Model not loading?**
- Check `models/isl_lstm.h5` is in repo
- Check Railway logs for errors

---

## 💰 Cost

**FREE TIER:**
- $5 credit/month
- Your app uses ~$2-4/month
- Perfect for testing!

**After free credit:**
- Pay only for what you use
- Very affordable (~$5-10/month)

---

## 🎯 Next Steps

1. ✅ Deploy to Railway (5 minutes)
2. ✅ Test all features
3. ✅ Share your URL
4. ✅ Monitor in Railway dashboard

**Need help?** See `RAILWAY_DEPLOYMENT.md` for detailed guide.

---

**Ready?** Go to https://railway.app and deploy! 🚀

