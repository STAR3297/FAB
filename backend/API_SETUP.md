# API Keys Setup Guide

This guide will help you obtain API keys for Twitter, Reddit, and YouTube to enable real-time data collection.

## 1. Twitter API (X) Setup

### Steps:
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter account
3. Create a new project/app
4. Navigate to "Keys and Tokens" tab
5. Generate a **Bearer Token**
6. Copy the token

### Add to `.env`:
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Note:** Free tier has rate limits. For production, consider upgrading.

---

## 2. Reddit API Setup

### Steps:
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Scroll down and click "create another app..." or "create app"
3. Fill in:
   - **Name**: FeedbackAnalysisBot (or any name)
   - **Type**: script
   - **Description**: (optional)
   - **About URL**: (optional)
   - **Redirect URI**: http://localhost:8000 (or any valid URL)
4. **Important**: Before clicking "create app":
   - Check the reCAPTCHA checkbox ("I'm not a robot")
   - Read and acknowledge Reddit's [Developer Terms](https://www.reddit.com/wiki/api) and [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy)
   - You must register to use the API (mentioned at the top of the form)
5. Click "create app"
6. Note the **client ID** (under the app name) and **secret** (labeled "secret")

### Add to `.env`:
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=FeedbackAnalysisBot/1.0
```

**Note:** Reddit API is free but has rate limits (60 requests per minute).

---

## 3. YouTube Data API v3 Setup

### Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key
   - (Optional) Restrict the key to YouTube Data API v3

### Add to `.env`:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**Note:** Free tier: 10,000 units per day. Each search = 100 units, each comment thread = 1 unit.

---

## 4. Setup Instructions

1. **Copy the example file:**
   ```bash
   cd backend
   copy .env.example .env
   # Or on Linux/Mac:
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   - Open `.env` in a text editor
   - Replace placeholder values with your actual API keys
   - Save the file

3. **Restart the backend:**
   ```bash
   flask --app app run --debug
   ```

4. **Test the connection:**
   - Visit `http://127.0.0.1:5000/health`
   - Should show `{"status": "ok", "mode": "live"}` if keys are detected

---

## Troubleshooting

### Twitter API Issues:
- **Error: "Invalid or expired token"**: Regenerate your Bearer Token
- **Rate limit exceeded**: Wait or upgrade your plan
- **403 Forbidden**: Check your app permissions in Twitter Developer Portal

### Reddit API Issues:
- **Error: "Invalid credentials"**: Double-check client ID and secret
- **403 Forbidden**: Ensure user_agent is set correctly
- **Rate limit**: Reddit limits to 60 requests/minute
- **Policy message when creating app**: Make sure you've:
  - Checked the reCAPTCHA checkbox
  - Read and acknowledged Reddit's Developer Terms and Responsible Builder Policy
  - Registered to use the API (if required)

### YouTube API Issues:
- **Error: "API key not valid"**: Regenerate API key in Google Cloud Console
- **Quota exceeded**: Check your daily quota (10,000 units/day)
- **403 Forbidden**: Ensure YouTube Data API v3 is enabled

---

## Testing Without API Keys

The system will automatically use mock data if API keys are not provided. This allows you to test the frontend and backend integration without setting up APIs first.

---

## Common Issues When Creating API Keys

### Reddit API Creation Problems:

**Issue: "Cannot create app" or form not submitting**
- **Solution 1**: Make sure your Reddit account is verified (check email)
- **Solution 2**: Try using a different browser or incognito mode
- **Solution 3**: Clear browser cache and cookies, then try again
- **Solution 4**: Wait a few minutes and try again (Reddit may have temporary restrictions)
- **Solution 5**: Make sure you're logged into Reddit with a verified account

**Issue: reCAPTCHA not working**
- Complete the reCAPTCHA challenge fully
- Try refreshing the page and completing it again
- Disable browser extensions that might interfere (ad blockers, privacy tools)

**Issue: "You must register to use the API"**
- Visit [Reddit API Registration](https://www.reddit.com/wiki/api) and complete registration
- Some accounts may need to verify their email first
- Wait 24 hours after account creation before creating apps

**Alternative: Try creating a "web app" instead of "script"**
- Sometimes "script" type has restrictions
- Use "web app" type with redirect URI: `http://localhost:8000`

### Twitter API Creation Problems:

**Issue: "Access denied" or "Application pending"**
- Twitter API access requires approval (can take days/weeks)
- Free tier may have limited availability
- Consider using mock data for development

**Issue: Cannot access Developer Portal**
- Twitter/X has restricted API access
- You may need to apply and wait for approval
- For development, use mock data instead

### YouTube API Creation Problems:

**Issue: "Billing account required"**
- YouTube API requires a Google Cloud billing account (even for free tier)
- However, free tier has $0 cost - you just need to add a payment method
- You can set a $0 budget limit to prevent charges

**Issue: "API not enabled"**
- Make sure you've enabled "YouTube Data API v3" in Google Cloud Console
- Go to: APIs & Services > Library > Search "YouTube Data API v3" > Enable

---

## Quick Start Without API Keys

If you're having trouble creating API keys, you can still develop and test your application:

1. **Create `.env` file** (even if empty):
   ```bash
   cd backend
   copy .env.example .env
   # Leave all values as placeholders or empty
   ```

2. **Run the backend**:
   ```bash
   flask --app app run --debug
   ```

3. **Test with mock data**:
   - Visit `http://127.0.0.1:5000/health`
   - Should show `{"mode": "mock"}` if no keys are configured
   - The `/analyze` endpoint will return mock data automatically

4. **Add API keys later** when you're able to create them - just update the `.env` file and restart the server.


