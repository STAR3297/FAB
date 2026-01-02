# Deployment Guide

This guide will help you deploy your Social Media Feedback Analysis application to a live domain.

## Table of Contents
1. [Quick Deploy Options](#quick-deploy-options)
2. [Render.com Deployment](#rendercom-deployment-recommended)
3. [Railway.app Deployment](#railwayapp-deployment)
4. [VPS Deployment (DigitalOcean, AWS, etc.)](#vps-deployment)
5. [Domain Configuration](#domain-configuration)
6. [Environment Variables Setup](#environment-variables-setup)

---

## Quick Deploy Options

### Option 1: Render.com (Recommended - Free Tier Available)
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy domain connection
- ✅ Auto-deploy from GitHub
- ⏱️ Setup time: 15-20 minutes

### Option 2: Railway.app
- ✅ Simple deployment
- ✅ Good free tier
- ✅ Automatic HTTPS
- ⏱️ Setup time: 10-15 minutes

### Option 3: VPS (DigitalOcean, AWS EC2, etc.)
- ✅ Full control
- ✅ More customization
- ⚠️ Requires server management
- ⏱️ Setup time: 30-60 minutes

---

## Render.com Deployment (Recommended)

### Prerequisites
- GitHub account
- Render.com account (free)

### Step 1: Push Code to GitHub

1. Initialize git (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Create a new repository on GitHub

3. Push your code:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy Backend on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `feedback-analysis-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Root Directory**: Leave empty (or set to `backend` if deploying separately)

5. Add Environment Variables:
   - `TWITTER_BEARER_TOKEN` (if you have it)
   - `REDDIT_CLIENT_ID` (if you have it)
   - `REDDIT_CLIENT_SECRET` (if you have it)
   - `YOUTUBE_API_KEY` (if you have it)
   - `REDDIT_USER_AGENT=FeedbackAnalysisBot/1.0`
   - `FLASK_ENV=production`
   - `ALLOWED_ORIGINS=https://your-frontend-domain.com` (update after frontend deploy)

6. Click **"Create Web Service"**
7. Wait for deployment (5-10 minutes)
8. Note your backend URL: `https://your-backend-name.onrender.com`

### Step 3: Deploy Frontend on Render

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `feedback-analysis-frontend`
   - **Root Directory**: `frontend` ⚠️ **IMPORTANT: Set this to `frontend`**
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build` (not `frontend/build`)

4. Add Environment Variable:
   - `REACT_APP_API_BASE=https://your-backend-name.onrender.com`

5. Click **"Create Static Site"**
6. Wait for deployment
7. Note your frontend URL: `https://your-frontend-name.onrender.com`

**Important Notes:**
- **Root Directory must be set to `frontend`** - This tells Render to use the `frontend` folder as the base
- Build command should NOT include `cd frontend` because Root Directory already does that
- Publish Directory should be just `build`, not `frontend/build`

### Step 4: Update CORS Settings

1. Go back to your backend service on Render
2. Update environment variable:
   - `ALLOWED_ORIGINS=https://your-frontend-name.onrender.com`
3. Redeploy the backend

### Step 5: Connect Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click **"Settings"** → **"Custom Domains"**
3. Add your domain
4. Follow DNS configuration instructions
5. Render will automatically provision SSL certificate

---

## Railway.app Deployment

### Step 1: Deploy Backend

1. Go to [Railway.app](https://railway.app/)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python
5. Set Root Directory to `backend`
6. Add environment variables (same as Render)
7. Railway will automatically deploy

### Step 2: Deploy Frontend

1. Create a new service in the same project
2. Select **"Static Site"**
3. Set Root Directory to `frontend`
4. Add build command: `npm install && npm run build`
5. Add environment variable: `REACT_APP_API_BASE=https://your-backend-url.railway.app`

---

## VPS Deployment

### Prerequisites
- VPS with Ubuntu 20.04+ (DigitalOcean, AWS EC2, etc.)
- Domain name (optional but recommended)
- SSH access to your server

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Node.js
sudo apt install python3-pip python3-venv nginx -y
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 for process management
sudo npm install -g pm2
```

### Step 2: Deploy Backend

```bash
# Clone your repository
cd /var/www
sudo git clone https://github.com/yourusername/your-repo.git
cd your-repo/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
sudo nano .env
# Add your environment variables here

# Test the application
gunicorn app:app --bind 0.0.0.0:5000
```

### Step 3: Setup Backend with Systemd

```bash
# Create systemd service
sudo nano /etc/systemd/system/feedback-backend.service
```

Add this content:
```ini
[Unit]
Description=Feedback Analysis Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/your-repo/backend
Environment="PATH=/var/www/your-repo/backend/venv/bin"
ExecStart=/var/www/your-repo/backend/venv/bin/gunicorn app:app --bind 127.0.0.1:5000 --workers 2

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable feedback-backend
sudo systemctl start feedback-backend
```

### Step 4: Setup Nginx for Backend

```bash
sudo nano /etc/nginx/sites-available/backend
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Deploy Frontend

```bash
cd /var/www/your-repo/frontend

# Install dependencies
npm install

# Build for production
REACT_APP_API_BASE=https://api.yourdomain.com npm run build

# Setup Nginx for frontend
sudo nano /etc/nginx/sites-available/frontend
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/your-repo/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /static {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal is set up automatically
```

---

## Domain Configuration

### DNS Settings

For your domain, add these DNS records:

**Option 1: Using Render/Railway subdomain**
- Type: `CNAME`
- Name: `@` or `www`
- Value: `your-app.onrender.com` (or `.railway.app`)

**Option 2: Using VPS with IP**
- Type: `A`
- Name: `@`
- Value: `your-server-ip`
- Type: `CNAME`
- Name: `www`
- Value: `yourdomain.com`

**For API subdomain (if separate):**
- Type: `CNAME`
- Name: `api`
- Value: `your-backend.onrender.com` (or your VPS IP)

### DNS Propagation
- Changes can take 24-48 hours to propagate
- Use [whatsmydns.net](https://www.whatsmydns.net/) to check status

---

## Environment Variables Setup

### Backend Environment Variables

Add these in your hosting platform's environment variables section:

```bash
# API Keys (optional - system works with mock data if not provided)
TWITTER_BEARER_TOKEN=your_token_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
YOUTUBE_API_KEY=your_key

# Required
REDDIT_USER_AGENT=FeedbackAnalysisBot/1.0
FLASK_ENV=production
ALLOWED_ORIGINS=https://your-frontend-domain.com

# Optional
RESULT_LIMIT=50
PORT=5000
```

### Frontend Environment Variables

```bash
REACT_APP_API_BASE=https://your-backend-url.com
```

**Important:** For React apps, environment variables must start with `REACT_APP_` to be accessible in the browser.

---

## Post-Deployment Checklist

- [ ] Backend health check: `https://your-backend-url.com/health`
- [ ] Frontend loads correctly
- [ ] API calls work from frontend
- [ ] CORS is configured correctly
- [ ] SSL certificate is active (HTTPS)
- [ ] Environment variables are set
- [ ] Custom domain is connected (if applicable)

---

## Troubleshooting

### Backend Issues

**502 Bad Gateway:**
- Check if backend service is running
- Verify PORT environment variable
- Check application logs

**CORS Errors:**
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check that frontend URL matches exactly (including https://)

**API Not Working:**
- Verify environment variables are set correctly
- Check API keys are valid
- Review application logs for errors

### Frontend Issues

**Blank Page:**
- Check browser console for errors
- Verify `REACT_APP_API_BASE` is set correctly
- Ensure build completed successfully

**API Connection Failed:**
- Verify backend URL is correct
- Check CORS settings on backend
- Ensure backend is accessible

---

## Cost Estimates

### Free Tier Options:
- **Render.com**: Free tier with limitations (spins down after inactivity)
- **Railway.app**: $5/month free credit
- **Vercel/Netlify**: Free for frontend static sites

### Paid Options:
- **Render.com**: $7/month for always-on backend
- **DigitalOcean**: $6/month for basic VPS
- **AWS EC2**: ~$5-10/month for t2.micro

---

## Support

If you encounter issues:
1. Check application logs in your hosting platform
2. Verify all environment variables are set
3. Test backend endpoints directly
4. Check browser console for frontend errors

For more help, refer to:
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Nginx Documentation](https://nginx.org/en/docs/)

