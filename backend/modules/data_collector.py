import os
import random
from typing import Dict, List

class DataCollector:
    """Collects data from Twitter, Reddit, and YouTube"""
    
    def __init__(self):
        self.twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'FeedbackAnalysisBot/1.0')
        self.youtube_key = os.getenv('YOUTUBE_API_KEY')
        self.result_limit = int(os.getenv('RESULT_LIMIT', 50))
        
        # Initialize API clients if keys are available
        self.twitter_client = None
        self.reddit_client = None
        self.youtube_client = None
        
        self._init_clients()
    
    def _init_clients(self):
        """Initialize API clients if credentials are available"""
        # Twitter
        if self.twitter_token:
            try:
                import tweepy
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_token)
            except Exception as e:
                print(f"Twitter client init failed: {e}")
        
        # Reddit
        if self.reddit_client_id and self.reddit_client_secret:
            try:
                import praw
                self.reddit_client = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_client_secret,
                    user_agent=self.reddit_user_agent
                )
            except Exception as e:
                print(f"Reddit client init failed: {e}")
        
        # YouTube
        if self.youtube_key:
            try:
                from googleapiclient.discovery import build
                self.youtube_client = build('youtube', 'v3', developerKey=self.youtube_key)
            except Exception as e:
                print(f"YouTube client init failed: {e}")
    
    def collect_all(self, query: str) -> Dict[str, List[Dict]]:
        """Collect data from all platforms"""
        return {
            'twitter': self.collect_twitter(query),
            'reddit': self.collect_reddit(query),
            'youtube': self.collect_youtube(query)
        }
    
    def collect_twitter(self, query: str) -> List[Dict]:
        """Collect tweets from Twitter/X"""
        if self.twitter_client:
            try:
                # Search for recent tweets
                tweets = self.twitter_client.search_recent_tweets(
                    query=query,
                    max_results=min(self.result_limit, 100),
                    tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang']
                )
                if tweets.data:
                    return [
                        {
                            'text': tweet.text,
                            'created_at': str(tweet.created_at),
                            'id': str(tweet.id),
                            'lang': getattr(tweet, 'lang', 'en'),
                            'retweet_count': getattr(tweet.public_metrics, 'retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                            'like_count': getattr(tweet.public_metrics, 'like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                        }
                        for tweet in tweets.data
                    ]
                else:
                    print(f"Twitter API: No tweets found for query '{query}'")
            except Exception as e:
                print(f"Twitter API error: {e}")
                print("Falling back to mock data")
        
        # Mock data fallback
        return self._mock_twitter_data(query)
    
    def collect_reddit(self, query: str) -> List[Dict]:
        """Collect posts from Reddit"""
        if self.reddit_client:
            try:
                posts = []
                # Search across all subreddits
                search_results = self.reddit_client.subreddit('all').search(
                    query, 
                    limit=self.result_limit,
                    sort='relevance',
                    time_filter='week'  # Get posts from last week
                )
                
                for submission in search_results:
                    # Combine title and selftext
                    text = f"{submission.title}"
                    if submission.selftext:
                        text += f" {submission.selftext}"
                    
                    posts.append({
                        'text': text[:500],  # Limit text length
                        'created_at': str(submission.created_utc),
                        'id': submission.id,
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'url': f"https://reddit.com{submission.permalink}"
                    })
                    
                    if len(posts) >= self.result_limit:
                        break
                
                if posts:
                    print(f"Reddit API: Found {len(posts)} posts for query '{query}'")
                    return posts
                else:
                    print(f"Reddit API: No posts found for query '{query}'")
            except Exception as e:
                print(f"Reddit API error: {e}")
                print("Falling back to mock data")
        
        # Mock data fallback
        return self._mock_reddit_data(query)
    
    def collect_youtube(self, query: str) -> List[Dict]:
        """Collect comments from YouTube videos"""
        if self.youtube_client:
            try:
                # First, search for videos
                search_response = self.youtube_client.search().list(
                    q=query,
                    part='id,snippet',
                    type='video',
                    maxResults=min(10, self.result_limit // 5),  # Get more videos for more comments
                    order='relevance'
                ).execute()
                
                comments = []
                videos_found = search_response.get('items', [])
                
                if not videos_found:
                    print(f"YouTube API: No videos found for query '{query}'")
                else:
                    print(f"YouTube API: Found {len(videos_found)} videos for query '{query}'")
                
                for item in videos_found:
                    video_id = item['id']['videoId']
                    video_title = item['snippet']['title']
                    
                    try:
                        # Get comments for each video
                        comment_response = self.youtube_client.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=min(20, self.result_limit // len(videos_found) if videos_found else 10),
                            order='relevance'
                        ).execute()
                        
                        for comment_item in comment_response.get('items', []):
                            comment = comment_item['snippet']['topLevelComment']['snippet']
                            comments.append({
                                'text': comment['textDisplay'],
                                'created_at': comment['publishedAt'],
                                'id': comment_item['id'],
                                'video_id': video_id,
                                'video_title': video_title,
                                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                                'like_count': comment.get('likeCount', 0)
                            })
                    except Exception as e:
                        # Some videos may have comments disabled
                        print(f"YouTube API: Could not fetch comments for video {video_id}: {e}")
                        continue
                    
                    # Stop if we have enough comments
                    if len(comments) >= self.result_limit:
                        break
                
                if comments:
                    print(f"YouTube API: Collected {len(comments)} comments")
                    return comments[:self.result_limit]
                else:
                    print(f"YouTube API: No comments found for query '{query}'")
            except Exception as e:
                print(f"YouTube API error: {e}")
                print("Falling back to mock data")
        
        # Mock data fallback
        return self._mock_youtube_data(query)
    
    def _mock_twitter_data(self, query: str) -> List[Dict]:
        """Generate mock Twitter data"""
        mock_texts = [
            f"Just got my {query}! Loving it so far 🎉",
            f"{query} is amazing, highly recommend!",
            f"Not impressed with {query}, battery life is poor",
            f"{query} review: Great camera but expensive",
            f"Anyone else having issues with {query}?",
            f"{query} is the best purchase I've made this year",
            f"Mixed feelings about {query}, some features are missing",
            f"{query} - worth the hype? I think so!",
        ]
        return [
            {'text': text, 'created_at': '2024-01-01', 'id': f'tw_{i}'}
            for i, text in enumerate(random.sample(mock_texts, min(8, len(mock_texts))))
        ]
    
    def _mock_reddit_data(self, query: str) -> List[Dict]:
        """Generate mock Reddit data"""
        mock_texts = [
            f"Just bought {query} - AMA",
            f"{query} review after 1 month of use",
            f"Is {query} worth it in 2024?",
            f"{query} vs competitors - detailed comparison",
            f"Having problems with {query}, need help",
            f"{query} is overrated in my opinion",
            f"Best settings for {query}?",
            f"{query} - pros and cons",
        ]
        return [
            {
                'text': text,
                'created_at': '2024-01-01',
                'id': f'rd_{i}',
                'subreddit': 'technology',
                'score': random.randint(10, 500)
            }
            for i, text in enumerate(random.sample(mock_texts, min(8, len(mock_texts))))
        ]
    
    def _mock_youtube_data(self, query: str) -> List[Dict]:
        """Generate mock YouTube data"""
        mock_texts = [
            f"Great review of {query}! Very helpful",
            f"{query} looks amazing, might buy it",
            f"Not sure about {query}, seems expensive",
            f"{query} has great features but poor battery",
            f"Best {query} review I've seen!",
            f"{query} is definitely worth checking out",
            f"Disappointed with {query}, expected more",
            f"{query} - solid choice for the price",
        ]
        return [
            {
                'text': text,
                'created_at': '2024-01-01',
                'id': f'yt_{i}',
                'video_id': 'dQw4w9WgXcQ',
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            }
            for i, text in enumerate(random.sample(mock_texts, min(8, len(mock_texts))))
        ]



