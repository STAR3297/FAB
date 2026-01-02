# Social Media Feedback Analysis

A real-time social media feedback analysis application that collects and analyzes feedback from Twitter, Reddit, and YouTube.

## Features

- 🔍 **Multi-Platform Analysis**: Collect feedback from Twitter, Reddit, and YouTube
- 📊 **Sentiment Analysis**: Analyze sentiment using VADER sentiment analysis
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

## API Keys Setup

See [backend/API_SETUP.md](./backend/API_SETUP.md) for detailed instructions on obtaining API keys.

**Note:** The application works with mock data if API keys are not provided, allowing you to test without setting up APIs first.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions.

### Quick Deploy Options:
- **Render.com** (Recommended - Free tier available)
- **Railway.app** (Simple deployment)
- **VPS** (DigitalOcean, AWS, etc.)

## Project Structure

```
.
├── backend/           # Flask API backend
│   ├── app.py        # Main Flask application
│   ├── modules/      # Data collection and NLP modules
│   ├── requirements.txt
│   └── API_SETUP.md  # API keys setup guide
├── frontend/          # React frontend
│   ├── src/          # React source code
│   ├── public/       # Static files
│   └── package.json
├── DEPLOYMENT.md      # Deployment guide
└── README.md          # This file
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

### Running Tests
```bash
# Backend API testing
cd backend
python test_apis.py

# Frontend (if tests are added)
cd frontend
npm test
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
```bash
TWITTER_BEARER_TOKEN=your_token
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
YOUTUBE_API_KEY=your_key
REDDIT_USER_AGENT=FeedbackAnalysisBot/1.0
RESULT_LIMIT=50
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

For issues and questions:
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment help
- Check [backend/API_SETUP.md](./backend/API_SETUP.md) for API setup
- Review application logs for errors

---

Built with ❤️ for social media feedback analysis

