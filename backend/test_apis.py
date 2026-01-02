"""
Simple script to test API connections
Run this after setting up your .env file to verify API keys work
"""

import os
from dotenv import load_dotenv
from modules.data_collector import DataCollector

load_dotenv()

def test_apis():
    print("=" * 60)
    print("Testing API Connections")
    print("=" * 60)
    
    collector = DataCollector()
    
    # Check which APIs are configured
    print("\n📋 API Configuration Status:")
    print(f"  Twitter: {'✅ Configured' if collector.twitter_client else '❌ Not configured'}")
    print(f"  Reddit:  {'✅ Configured' if collector.reddit_client else '❌ Not configured'}")
    print(f"  YouTube: {'✅ Configured' if collector.youtube_client else '❌ Not configured'}")
    
    if not any([collector.twitter_client, collector.reddit_client, collector.youtube_client]):
        print("\n⚠️  No API keys found. The system will use mock data.")
        print("   See API_SETUP.md for instructions on obtaining API keys.")
        return
    
    # Test with a simple query
    test_query = "iPhone"
    print(f"\n🔍 Testing with query: '{test_query}'")
    print("-" * 60)
    
    # Test Twitter
    if collector.twitter_client:
        print("\n🐦 Testing Twitter API...")
        try:
            tweets = collector.collect_twitter(test_query)
            if tweets and len(tweets) > 0:
                print(f"  ✅ Success! Found {len(tweets)} tweets")
                print(f"  Sample: {tweets[0]['text'][:100]}...")
            else:
                print("  ⚠️  No tweets found (may be rate limited or no results)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test Reddit
    if collector.reddit_client:
        print("\n🔴 Testing Reddit API...")
        try:
            posts = collector.collect_reddit(test_query)
            if posts and len(posts) > 0:
                print(f"  ✅ Success! Found {len(posts)} posts")
                print(f"  Sample: {posts[0]['text'][:100]}...")
            else:
                print("  ⚠️  No posts found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test YouTube
    if collector.youtube_client:
        print("\n📺 Testing YouTube API...")
        try:
            comments = collector.collect_youtube(test_query)
            if comments and len(comments) > 0:
                print(f"  ✅ Success! Found {len(comments)} comments")
                print(f"  Sample: {comments[0]['text'][:100]}...")
            else:
                print("  ⚠️  No comments found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_apis()


