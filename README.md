# Social Media Feedback Analysis

A real-time social media feedback analysis application that collects and analyzes feedback from Twitter, Reddit, and YouTube.

## Features

- 🔍 **Multi-Platform Analysis**: Collect feedback from Twitter, Reddit, and YouTube
- 📊 **Sentiment Analysis**: VADER by default; optional Groq classification when `GROQ_API_KEY` is set
- 📈 **Visual Analytics**: Interactive charts and graphs
- 🎯 **Keyword Extraction**: Identify key topics and trends
- 🚀 **Real-time Data**: Live data collection from social media platforms
- 🎨 **Modern UI**: Beautiful, responsive React frontend

## Tech Stack

### Frontend
- React 19
- Chart.js for data visualization
- Modern CSS with animations

### Backend
- Flask (Python)
- VADER Sentiment Analysis
- Groq API (summary + optional sentiment)
- Twitter API (Tweepy)
- Reddit API (PRAW)
- YouTube Data API v3

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# Edit .env and add your API keys (optional - works with mock data)

# Run backend
flask --app app run --debug
```

Backend will run on `http://127.0.0.1:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on `http://localhost:3000`

## API keys

Copy `backend/.env.example` to `backend/.env` and fill in the keys you need. At minimum, set **`GROQ_API_KEY`** for the Analysis Summary and (optionally) AI sentiment. Reddit, YouTube, and Twitter keys enable live data; without them, the collector may use fallbacks or return fewer results depending on configuration.

## Deployment

Deploy the Flask app (e.g. `gunicorn app:app`) with the same environment variables as `.env`. Point your frontend `REACT_APP_API_BASE` at the deployed API URL.

## Project Structure

```
.
├── backend/
│   ├── app.py
│   ├── .env.example
│   ├── modules/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## API Endpoints

### Health Check
```
GET /health
```
Returns server status and API configuration.

### Analyze
```
GET /analyze?query=<keyword>
```
Analyzes feedback for the given keyword across all platforms.

Example: `http://127.0.0.1:5000/analyze?query=iPhone%2016`

## Development

### Smoke test
```bash
# Backend (with server running)
curl http://127.0.0.1:5000/health
curl "http://127.0.0.1:5000/analyze?query=test"
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
gunicorn app:app --bind 0.0.0.0:5000
```

## Environment Variables

### Backend (.env)

See `backend/.env.example` for the full list. Essentials:

```bash
GROQ_API_KEY=your_groq_key
# Optional: GROQ_SUMMARY_MODEL, GROQ_SENTIMENT_MODEL, GROQ_SENTIMENT_BATCH_SIZE, USE_AI_SENTIMENT

REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=FeedbackAnalysisBot/1.0
YOUTUBE_API_KEY=...
RESULT_LIMIT=150
```

### Frontend
```bash
REACT_APP_API_BASE=http://127.0.0.1:5000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

Use `backend/.env.example`, `/health`, and application logs to verify configuration.

---

Built with ❤️ for social media feedback analysis

