# Quick Start Guide

## For Local Development

### 1. Backend Setup (5 minutes)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
flask --app app run --debug
```

### 2. Frontend Setup (3 minutes)

```bash
cd frontend
npm install
npm start
```

### 3. Test It

- Open `http://localhost:3000`
- Enter a keyword (e.g., "iPhone 16")
- Click "Analyze"

---

## For Production Deployment (15-20 minutes)

### Option 1: Render.com (Easiest)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/repo.git
   git push -u origin main
   ```

2. **Deploy Backend**
   - Go to [Render.com](https://render.com)
   - New → Web Service
   - Connect GitHub repo
   - Settings:
     - Build: `pip install -r backend/requirements.txt`
     - Start: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
   - Add environment variables (see DEPLOYMENT.md)
   - Deploy!

3. **Deploy Frontend**
   - New → Static Site
   - Connect GitHub repo
   - Settings:
     - Build: `cd frontend && npm install && npm run build`
     - Publish: `frontend/build`
   - Add env: `REACT_APP_API_BASE=https://your-backend.onrender.com`
   - Deploy!

4. **Update CORS**
   - Backend → Environment → `ALLOWED_ORIGINS=https://your-frontend.onrender.com`
   - Redeploy backend

### Option 2: Railway.app

1. Go to [Railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Add backend service (auto-detects Python)
4. Add frontend service (Static Site)
5. Add environment variables
6. Done!

---

## Environment Variables Quick Reference

### Backend (.env or hosting platform)
```bash
TWITTER_BEARER_TOKEN=optional
REDDIT_CLIENT_ID=optional
REDDIT_CLIENT_SECRET=optional
YOUTUBE_API_KEY=optional
REDDIT_USER_AGENT=FeedbackAnalysisBot/1.0
ALLOWED_ORIGINS=https://your-frontend-domain.com
FLASK_ENV=production
```

### Frontend (hosting platform)
```bash
REACT_APP_API_BASE=https://your-backend-domain.com
```

**Note:** Works with mock data if API keys are not provided!

---

## Need Help?

- **Deployment Issues**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **API Setup**: See [backend/API_SETUP.md](./backend/API_SETUP.md)
- **General Info**: See [README.md](./README.md)

---

## Cleanup Scripts

Run these to remove cache files:

**Windows:**
```powershell
.\cleanup.ps1
```

**Linux/Mac:**
```bash
chmod +x cleanup.sh
./cleanup.sh
```

