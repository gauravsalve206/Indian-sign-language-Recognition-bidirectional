# Quick Deployment Reference

## 🚀 Fastest Deployment Options

### Option 1: Railway (Recommended - Easiest)
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your repository
4. Railway auto-detects Python
5. Set start command: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
6. Deploy! ✅

### Option 2: Render
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
6. Deploy! ✅

### Option 3: Heroku
```bash
heroku create your-app-name
git push heroku main
heroku open
```

---

## 📋 Pre-Deployment Checklist

- [ ] Remove `myenv/` folder (virtual environment)
- [ ] Ensure `requirements.txt` is up to date
- [ ] Test locally: `uvicorn src.server:app --port 8000`
- [ ] Verify model files are included (`models/isl_lstm.h5`)
- [ ] Check frontend files are in `frontend/` directory
- [ ] Verify GIF files in `text_to_sign/ISL_Gifs/`

---

## 🔧 Required Files for Deployment

```
sign_lang/
├── src/                    ✅ Include
├── frontend/              ✅ Include
├── models/                ✅ Include
├── text_to_sign/          ✅ Include
├── requirements.txt       ✅ Include
├── Procfile              ✅ Include (for Heroku)
├── runtime.txt           ✅ Include (for Heroku)
└── myenv/                ❌ EXCLUDE (virtual env)
```

---

## 🌐 Production URLs

After deployment, your app will be available at:
- Railway: `https://your-app-name.up.railway.app`
- Render: `https://your-app-name.onrender.com`
- Heroku: `https://your-app-name.herokuapp.com`

---

## ⚠️ Important Notes

1. **HTTPS Required**: Browsers need HTTPS for camera access
2. **WebSocket Support**: Ensure platform supports WebSocket
3. **File Size Limits**: Some platforms limit file sizes (models can be large)
4. **Environment Variables**: Set `PORT` if needed (usually auto-set)

---

## 🧪 Test After Deployment

1. Visit homepage: `https://your-domain.com`
2. Test sign-to-text: `/sign-to-text.html`
3. Test text-to-sign: `/text-to-sign.html`
4. Check browser console for errors

---

## 📞 Common Issues

**Server won't start?**
- Check Python version (needs 3.10+)
- Verify all dependencies in requirements.txt

**WebSocket not working?**
- Platform must support WebSocket
- Check CORS settings

**Camera not accessing?**
- Must use HTTPS (not HTTP)
- Check browser permissions

---

For detailed instructions, see `DEPLOYMENT_GUIDE.md`

