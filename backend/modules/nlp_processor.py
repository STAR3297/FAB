from typing import Dict, List
from collections import Counter
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class NLPProcessor:
    """Processes text data with NLP: sentiment analysis and keyword extraction"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def process(self, data: Dict[str, List[Dict]], query: str) -> Dict:
        """Process all collected data and return analysis results"""
        results = {
            'query': query,
            'platforms': {},
            'combined': {
                'total_items': 0,
                'sentiment_counts': {'positive': 0, 'neutral': 0, 'negative': 0},
                'sentiment_scores': {'positive': 0.0, 'neutral': 0.0, 'negative': 0.0},
                'top_keywords': [],
                'summary': ''
            },
            'timestamp': None
        }
        
        # Process each platform
        for platform, items in data.items():
            if items:
                platform_result = self._process_platform(platform, items)
                results['platforms'][platform] = platform_result
                results['combined']['total_items'] += len(items)
        
        # Calculate combined statistics
        self._calculate_combined(results)
        
        # Generate summary
        results['combined']['summary'] = self._generate_summary(results, query)
        
        return results
    
    def _process_platform(self, platform: str, items: List[Dict]) -> Dict:
        """Process data from a single platform"""
        sentiments = []
        all_text = []
        
        for item in items:
            text = item.get('text', '')
            if text:
                all_text.append(text)
                sentiment = self.analyzer.polarity_scores(text)
                sentiments.append(sentiment)
        
        # Count sentiments
        pos_count = sum(1 for s in sentiments if s['compound'] > 0.05)
        neu_count = sum(1 for s in sentiments if -0.05 <= s['compound'] <= 0.05)
        neg_count = sum(1 for s in sentiments if s['compound'] < -0.05)
        
        # Calculate average scores
        avg_positive = sum(s['pos'] for s in sentiments) / len(sentiments) if sentiments else 0
        avg_neutral = sum(s['neu'] for s in sentiments) / len(sentiments) if sentiments else 0
        avg_negative = sum(s['neg'] for s in sentiments) / len(sentiments) if sentiments else 0
        
        # Extract keywords
        keywords = self._extract_keywords(' '.join(all_text))
        
        # Get sample items with sentiment (for display)
        sample_items = []
        for i, item in enumerate(items[:5]):  # Top 5 samples
            if i < len(sentiments):
                sentiment_label = self._get_sentiment_label(sentiments[i]['compound'])
                sample_items.append({
                    'text': item.get('text', '')[:200],  # Truncate long text
                    'sentiment': sentiment_label,
                    'score': sentiments[i]['compound'],
                    **{k: v for k, v in item.items() if k != 'text'}
                })
        
        # Get all items with sentiment (for keyword filtering)
        all_items = []
        for i, item in enumerate(items):
            if i < len(sentiments):
                sentiment_label = self._get_sentiment_label(sentiments[i]['compound'])
                all_items.append({
                    'text': item.get('text', ''),
                    'sentiment': sentiment_label,
                    'score': sentiments[i]['compound'],
                    **{k: v for k, v in item.items() if k != 'text'}
                })
        
        return {
            'total': len(items),
            'sentiment_counts': {
                'positive': pos_count,
                'neutral': neu_count,
                'negative': neg_count
            },
            'sentiment_scores': {
                'positive': round(avg_positive, 3),
                'neutral': round(avg_neutral, 3),
                'negative': round(avg_negative, 3)
            },
            'top_keywords': keywords[:10],
            'sample_items': sample_items,
            'all_items': all_items  # Include all items for filtering
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction: remove common words and get frequent terms
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her',
            'its', 'our', 'their', 'me', 'him', 'us', 'them', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
        }
        
        # Split into words and filter
        words = [w for w in text.split() if len(w) > 3 and w not in stop_words]
        
        # Count frequency
        word_counts = Counter(words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(20)]
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Get sentiment label from compound score"""
        if compound_score > 0.05:
            return 'positive'
        elif compound_score < -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_combined(self, results: Dict):
        """Calculate combined statistics across all platforms"""
        total_pos = sum(p['sentiment_counts']['positive'] for p in results['platforms'].values())
        total_neu = sum(p['sentiment_counts']['neutral'] for p in results['platforms'].values())
        total_neg = sum(p['sentiment_counts']['negative'] for p in results['platforms'].values())
        
        results['combined']['sentiment_counts'] = {
            'positive': total_pos,
            'neutral': total_neu,
            'negative': total_neg
        }
        
        # Calculate weighted average scores
        total_items = results['combined']['total_items']
        if total_items > 0:
            avg_pos = sum(
                p['sentiment_scores']['positive'] * p['total']
                for p in results['platforms'].values()
            ) / total_items
            
            avg_neu = sum(
                p['sentiment_scores']['neutral'] * p['total']
                for p in results['platforms'].values()
            ) / total_items
            
            avg_neg = sum(
                p['sentiment_scores']['negative'] * p['total']
                for p in results['platforms'].values()
            ) / total_items
            
            results['combined']['sentiment_scores'] = {
                'positive': round(avg_pos, 3),
                'neutral': round(avg_neu, 3),
                'negative': round(avg_neg, 3)
            }
        
        # Combine keywords from all platforms
        all_keywords = []
        for platform_data in results['platforms'].values():
            all_keywords.extend(platform_data.get('top_keywords', []))
        
        keyword_counts = Counter(all_keywords)
        results['combined']['top_keywords'] = [
            word for word, count in keyword_counts.most_common(15)
        ]
    
    def _generate_summary(self, results: Dict, query: str) -> str:
        """Generate a text summary of the analysis"""
        combined = results['combined']
        counts = combined['sentiment_counts']
        total = combined['total_items']
        
        if total == 0:
            return f"No data found for '{query}'."
        
        pos_pct = (counts['positive'] / total * 100) if total > 0 else 0
        neg_pct = (counts['negative'] / total * 100) if total > 0 else 0
        
        summary = f"Analysis of {total} items across {len(results['platforms'])} platforms for '{query}': "
        
        if pos_pct > 50:
            summary += f"Overall sentiment is positive ({pos_pct:.1f}% positive). "
        elif neg_pct > 50:
            summary += f"Overall sentiment is negative ({neg_pct:.1f}% negative). "
        else:
            summary += f"Overall sentiment is mixed ({pos_pct:.1f}% positive, {neg_pct:.1f}% negative). "
        
        if combined['top_keywords']:
            top_3 = ', '.join(combined['top_keywords'][:3])
            summary += f"Key topics discussed: {top_3}."
        
        return summary



