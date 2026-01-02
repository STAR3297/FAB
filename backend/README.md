# Backend - Real-Time Social Media Feedback Analysis

Flask REST API for collecting and analyzing social media feedback from Twitter, Reddit, and YouTube.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   # Create .env file from example
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # Linux/Mac
   ```
   
   Then edit `.env` and add your API keys. See [API_SETUP.md](./API_SETUP.md) for detailed instructions on obtaining API keys.
   
   **Note:** The system works with mock data if API keys are not provided, but you'll need real keys for live data.

## Running

```bash
flask --app app run --debug
```

The API will run on `http://127.0.0.1:5000`

## Endpoints

- `GET /health` - Health check with API status
  - Returns: `{"status": "ok", "mode": "live|mock", "apis": {"twitter": true/false, "reddit": true/false, "youtube": true/false}}`
  
- `GET /analyze?query=<keyword>` - Analyze feedback for a keyword
  - Example: `http://127.0.0.1:5000/analyze?query=iPhone%2016`
  - Returns: JSON with sentiment analysis, keywords, and platform breakdown

## API Keys Setup

**For detailed step-by-step instructions, see [API_SETUP.md](./API_SETUP.md)**

Quick summary:
- **Twitter**: Bearer Token from [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- **Reddit**: Client ID & Secret from [Reddit Apps](https://www.reddit.com/prefs/apps)
- **YouTube**: API Key from [Google Cloud Console](https://console.cloud.google.com/)

## Testing

1. **Check API status:**
   ```bash
   curl http://127.0.0.1:5000/health
   ```

2. **Test analysis (with or without API keys):**
   ```bash
   curl "http://127.0.0.1:5000/analyze?query=iPhone%2016"
   ```

3. **Mode detection:**
   - If all API keys are missing: Uses mock data (mode: "mock")
   - If at least one API key is present: Uses live data for configured APIs (mode: "live")



