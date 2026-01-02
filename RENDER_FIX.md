# Fix Render Frontend Deployment Error

## The Problem

Error: `npm error enoent Could not read package.json: Error: ENOENT: no such file or directory, open '/opt/render/project/src/frontend/package.json'`

This happens because Render is looking in the wrong directory.

## The Solution

You need to update your **FAB-frontend** service settings on Render:

### Step 1: Go to Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click on your **FAB-frontend** service
3. Click on **"Settings"** tab (in the left sidebar)

### Step 2: Update Settings

Find and update these settings:

#### ✅ Root Directory
- **Current**: (probably empty or wrong)
- **Change to**: `frontend`
- **This tells Render**: "Use the `frontend` folder as the base directory"

#### ✅ Build Command  
- **Current**: `cd frontend && npm install && npm run build`
- **Change to**: `npm install && npm run build`
- **Why**: Root Directory already puts you in the `frontend` folder, so no need for `cd frontend`

#### ✅ Publish Directory
- **Current**: (probably `frontend/build` or wrong)
- **Change to**: `build`
- **Why**: Since Root Directory is `frontend`, the build folder is just `build`, not `frontend/build`

#### ✅ Environment Variables
Make sure you have:
- `REACT_APP_API_BASE=https://your-backend-url.onrender.com`
  (Replace with your actual backend URL)

### Step 3: Save and Redeploy

1. Click **"Save Changes"** at the bottom
2. Render will automatically trigger a new deployment
3. Wait for it to build (2-5 minutes)
4. Check the logs to see if it succeeds

## Summary of Correct Settings

```
Root Directory: frontend
Build Command: npm install && npm run build  
Publish Directory: build
Environment Variable: REACT_APP_API_BASE=https://your-backend.onrender.com
```

## Why This Works

- **Root Directory = `frontend`**: Render treats `frontend/` as the root
- **Build Command = `npm install && npm run build`**: Runs from within `frontend/`, so it finds `package.json`
- **Publish Directory = `build`**: After build, the output is in `frontend/build/`, but since root is `frontend`, you just say `build`

---

**Still having issues?** Check the deployment logs for any new errors after making these changes.

