from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS - allow all origins in production, or specific domain
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, origins=allowed_origins, supports_credentials=True)

# Import modules
from modules.data_collector import DataCollector
from modules.nlp_processor import NLPProcessor

# Initialize modules
data_collector = DataCollector()
nlp_processor = NLPProcessor()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with API status"""
    twitter_key = os.getenv('TWITTER_BEARER_TOKEN')
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    
    api_status = {
        'twitter': bool(twitter_key),
        'reddit': bool(reddit_id and reddit_secret),
        'youtube': bool(youtube_key)
    }
    
    # Determine mode: 'live' if at least one API is configured, 'mock' otherwise
    mode = 'live' if any(api_status.values()) else 'mock'
    
    return jsonify({
        'status': 'ok',
        'mode': mode,
        'apis': api_status,
        'message': 'All systems operational'
    })


@app.route('/analyze', methods=['GET'])
def analyze():
    """Main analysis endpoint"""
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        # Collect data from all platforms
        data = data_collector.collect_all(query)
        
        # Process with NLP
        results = nlp_processor.process(data, query)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Development mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)



