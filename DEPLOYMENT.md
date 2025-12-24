# Quick Deployment Guide - Free Tier

## 🚀 Deploy in 5 Minutes!

### Prerequisites
- GitHub account
- Vercel account (free): https://vercel.com
- Render account (free): https://render.com

---

## Step 1: Deploy Backend to Render

### Option A: One-Click Deploy (Easiest)
1. Fork this repository to your GitHub account
2. Go to https://render.com/deploy
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Select `TS-ErrorsAnalysis` repo
6. Click "Apply" - Render will read `render.yaml` and deploy automatically!

### Option B: Manual Deploy
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: `ts-errors-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt -r api/requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Add Environment Variable:
   - `DATABASE_URL`: (will set up database next)
6. Click "Create Web Service"

### Add PostgreSQL Database (Optional - or use SQLite)
1. In Render Dashboard, click "New +" → "PostgreSQL"
2. Name: `ts-errors-db`
3. Plan: Free
4. Create Database
5. Copy the "Internal Database URL"
6. Go back to your Web Service → Environment
7. Set `DATABASE_URL` to the database URL
8. Your API will restart automatically

### Get Your Backend URL
- After deployment: `https://ts-errors-api.onrender.com`
- Test it: `https://ts-errors-api.onrender.com/health`
- API Docs: `https://ts-errors-api.onrender.com/docs`

**⚠️ Note**: Free tier sleeps after 15 min of inactivity. First request may take 30 seconds to wake up.

---

## Step 2: Deploy Frontend to Vercel

### Option A: One-Click Deploy
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Select `TS-ErrorsAnalysis` repo
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://ts-errors-api.onrender.com` (your Render backend URL)
6. Click "Deploy"

### Option B: Vercel CLI
```bash
cd frontend
npm install -g vercel
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: ts-errors-analysis
# - Directory: ./
# - Override settings? No

# Add environment variable
vercel env add VITE_API_URL production
# Enter: https://ts-errors-api.onrender.com
```

### Get Your Frontend URL
- Your app: `https://ts-errors-analysis.vercel.app`
- Custom domain available on free tier!

---

## Step 3: Test Your Deployment

1. Open your Vercel URL
2. Go to "Analyze" page
3. Enter test data:
   ```
   Predicted: 1, 2, 3, 4, 5
   Target: 1.1, 2.2, 2.9, 4.1, 4.8
   ```
4. Click "Analyze"
5. View results!

---

## 🎯 Your Live URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | `https://your-app.vercel.app` | Main web interface |
| **API** | `https://your-api.onrender.com` | Backend API |
| **API Docs** | `https://your-api.onrender.com/docs` | Interactive API docs |
| **Database** | (Internal) | PostgreSQL on Render |

---

## 🔧 Alternative: Railway (Another Free Option)

Railway is even easier than Render:

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `TS-ErrorsAnalysis`
5. Railway auto-detects everything!
6. Add environment variables in dashboard
7. Done!

Railway advantages:
- Faster wake-up (no sleep on free tier)
- Simpler interface
- Auto-deploys on git push

---

## 📝 Environment Variables Reference

### Backend (`render.yaml` or Railway)
```bash
DATABASE_URL=postgresql://user:pass@host/db  # Optional, uses SQLite if not set
PYTHONUNBUFFERED=1
PORT=8000  # Render/Railway set this automatically
```

### Frontend (Vercel)
```bash
VITE_API_URL=https://your-backend-url.onrender.com
```

---

## 🔄 Continuous Deployment

Both platforms auto-deploy when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin claude/add-claude-documentation-d60DI

# Vercel & Render automatically deploy!
```

---

## 💰 Cost Breakdown (All FREE!)

| Service | Plan | Limits |
|---------|------|--------|
| **Vercel** | Hobby (Free) | 100GB bandwidth, unlimited sites |
| **Render** | Free | 750 hours/month, sleeps after 15min |
| **Railway** | Trial | $5 credit/month (enough for small apps) |
| **Database** | Render Free | 1GB storage, 1 concurrent connection |

---

## 🚨 Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify `requirements.txt` paths are correct
- Ensure Python version is 3.11+

### Frontend can't connect to backend
- Verify `VITE_API_URL` environment variable
- Check CORS settings (already configured in our API)
- Try API directly: `https://your-api.onrender.com/health`

### Database connection issues
- Check `DATABASE_URL` format
- Falls back to SQLite if not set (works fine!)
- Free tier PostgreSQL is optional

---

## ✅ Success Checklist

- [ ] Backend deployed to Render
- [ ] Backend health check returns 200: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads in browser
- [ ] Can run analysis from frontend
- [ ] Statistics page shows data
- [ ] Tools page works

---

## 🎉 Next Steps

Once deployed:
1. Share your URL with colleagues
2. Run real hydrological analyses
3. Customize branding (Stage 6+)
4. Add custom domain (free on Vercel)
5. Monitor usage in dashboards

**Need help?** Check logs in Render/Vercel dashboards or ask for assistance!
