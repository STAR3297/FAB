from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

# Browsers reject credentialed CORS with Origin: *; React dev (localhost:3000) must be allowed explicitly.
_raw = os.getenv('ALLOWED_ORIGINS', 'http://127.0.0.1:3000,http://localhost:3000').strip()
if _raw == '*':
    CORS(app, resources={r'/*': {'origins': '*'}})
else:
    _origins = [o.strip() for o in _raw.split(',') if o.strip()]
    CORS(app, origins=_origins or ['http://127.0.0.1:3000', 'http://localhost:3000'])


from modules.data_collector import DataCollector
from modules.nlp_processor import NLPProcessor


data_collector = DataCollector()
nlp_processor = NLPProcessor()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint with API status"""
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    reddit_public = os.getenv('REDDIT_PUBLIC_SCRAPE', 'true').lower() == 'true'
    
    groq_key = (os.getenv('GROQ_API_KEY') or '').strip()
    api_status = {
        'reddit': bool((reddit_id and reddit_secret) or reddit_public),
        'youtube': bool(youtube_key),
        'groq_ai': bool(groq_key),
    }

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
        
        data = data_collector.collect_all(query)
        
        
        results = nlp_processor.process(data, query)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)



