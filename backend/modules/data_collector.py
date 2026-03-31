import os
import html
from typing import Dict, List
from urllib.parse import quote_plus
import time
import re

class DataCollector:
    """Collects data from Reddit and YouTube using real data only (no mock fallbacks)"""
    
    def __init__(self):
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'FeedbackAnalysisBot/1.0')
        # If true, allow a lightweight, no-auth fetch via reddit.com public JSON endpoints.
        # This is useful when you can't obtain API keys, but it can be rate-limited.
        self.reddit_public_scrape = os.getenv('REDDIT_PUBLIC_SCRAPE', 'true').lower() == 'true'
        self.reddit_public_delay_s = float(os.getenv('REDDIT_PUBLIC_DELAY_S', '0.0'))
        self.youtube_key = os.getenv('YOUTUBE_API_KEY')
        self.result_limit = int(os.getenv('RESULT_LIMIT', 100))
        # Number of top videos (passing duration etc.) to use for comment aggregation
        self.youtube_video_count = max(2, min(10, int(os.getenv('YOUTUBE_VIDEO_COUNT', '10'))))
        
        # Initialize API clients if keys are available
        self.reddit_client = None
        self.youtube_client = None
        
        self._init_clients()
    
    def _init_clients(self):
        """Initialize API clients if credentials are available"""
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
    
    def _is_english(self, text: str) -> bool:
        """Return True if text appears to be English; otherwise False. Short or empty text is kept."""
        text = (text or '').strip()
        if len(text) < 15:
            return True  # Too short to detect; keep to avoid dropping valid snippets
        try:
            from langdetect import detect
            return detect(text) == 'en'
        except Exception:
            return True  # On detection failure, keep the item

    def _filter_english_only(self, items: List[Dict]) -> List[Dict]:
        """Keep only items whose 'text' field is detected as English."""
        if not items:
            return items
        out = [i for i in items if self._is_english(i.get('text', ''))]
        dropped = len(items) - len(out)
        if dropped:
            print(f"Filtered out {dropped} non-English item(s); {len(out)} remaining.")
        return out

    def collect_all(self, query: str) -> Dict[str, List[Dict]]:
        """Collect data from all platforms (English-only)."""
        reddit = self._filter_english_only(self.collect_reddit(query))
        youtube = self._filter_english_only(self.collect_youtube(query))
        return {'reddit': reddit, 'youtube': youtube}

    def _build_reddit_search_query(self, query: str) -> str:
        """
        Reddit treats space as AND; short tokens (e.g. '16') match unrelated posts.
        Multi-word queries use phrase-style quoting so results stay on-topic.
        """
        q = (query or "").strip()
        if not q:
            return q
        words = q.split()
        if len(words) >= 2:
            return f'"{q}"'
        return q

    def _decode_reddit_text(self, title: str, selftext: str) -> str:
        """Unescape entities like &gt; &amp; from Reddit JSON."""
        title = html.unescape((title or "").strip())
        body = html.unescape((selftext or "").strip())
        text = (title + (" " + body if body else "")).strip()
        return text

    def _reddit_post_matches_query(self, text: str, original_query: str) -> bool:
        """Drop search noise: multi-word queries must contain the full phrase (not just '16', etc.)."""
        if not text or not original_query:
            return False
        t = re.sub(r"\s+", " ", text.lower().strip())
        oq = re.sub(r"\s+", " ", original_query.lower().strip())
        if not oq:
            return False
        if oq in t:
            return True
        if len(original_query.split()) >= 2:
            # Phrase required; token-AND would keep unrelated posts that only share a number
            return False
        tokens = re.findall(r"[a-z0-9]+", oq, re.I)
        tokens = [x for x in tokens if len(x) >= 2]
        if not tokens:
            return False
        return all(tok in t for tok in tokens)

    def _reddit_praw_collect(self, search_term: str, original_query: str) -> List[Dict]:
        """Run one PRAW /r/all search and keep only posts that match original_query."""
        posts: List[Dict] = []
        # Scan up to 100 so we still fill result_limit after relevance filtering
        search_results = self.reddit_client.subreddit("all").search(
            search_term,
            limit=min(100, max(self.result_limit * 3, 40)),
            sort="relevance",
            time_filter="month",
        )
        for submission in search_results:
            text = self._decode_reddit_text(submission.title, submission.selftext or "")
            if not self._reddit_post_matches_query(text, original_query):
                continue
            posts.append({
                "text": text[:500],
                "created_at": str(submission.created_utc),
                "id": submission.id,
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "url": f"https://reddit.com{submission.permalink}",
            })
            if len(posts) >= self.result_limit:
                break
        return posts

    def collect_reddit(self, query: str) -> List[Dict]:
        """Collect posts from Reddit"""
        search_q = self._build_reddit_search_query(query)
        raw_q = (query or "").strip()

        if self.reddit_client:
            try:
                try_terms = [search_q]
                if search_q != raw_q:
                    try_terms.append(raw_q)

                for term in try_terms:
                    posts = self._reddit_praw_collect(term, query)
                    if posts:
                        print(f"Reddit API: Found {len(posts)} posts for query '{query}'")
                        return posts
                print(f"Reddit API: No posts found for query '{query}'")
            except Exception as e:
                print(f"Reddit API error: {e}")

        # No-key fallback via public Reddit JSON (best-effort; may be rate-limited)
        if self.reddit_public_scrape:
            try:
                try_terms = [search_q]
                if search_q != raw_q:
                    try_terms.append(raw_q)
                for term in try_terms:
                    posts = self._collect_reddit_public_json(query, term)
                    if posts:
                        print(f"Reddit public JSON: Found {len(posts)} posts for query '{query}'")
                        return posts
                print(f"Reddit public JSON: No posts found for query '{query}'")
            except Exception as e:
                print(f"Reddit public JSON error: {e}")
        
        # No data available
        return []

    def _collect_reddit_public_json(self, query: str, search_q: str) -> List[Dict]:
        """
        Best-effort, no-auth Reddit collection using public JSON endpoints.
        Notes:
        - Uses reddit.com/search.json intended for browser clients
        - Can be rate-limited (429) or blocked; we fall back gracefully
        """
        import requests

        if self.reddit_public_delay_s > 0:
            time.sleep(self.reddit_public_delay_s)

        # Max page size; we filter to the user's query locally
        limit = min(100, max(int(self.result_limit), 25))
        q_enc = quote_plus(search_q)

        # type=link = posts only; global search (not subreddit-specific)
        url = (
            f"https://www.reddit.com/search.json?q={q_enc}&type=link"
            f"&sort=relevance&t=month&limit={limit}&include_over_18=1"
        )
        headers = {
            "User-Agent": self.reddit_user_agent or "FeedbackAnalysisBot/1.0",
            "Accept": "application/json",
        }

        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 429:
            raise RuntimeError("Rate limited by Reddit (HTTP 429). Try lowering RESULT_LIMIT or adding REDDIT_PUBLIC_DELAY_S.")
        resp.raise_for_status()

        payload = resp.json() or {}
        children = (((payload.get("data") or {}).get("children")) or [])

        posts: List[Dict] = []
        for child in children:
            data = (child or {}).get("data") or {}
            title = data.get("title") or ""
            selftext = data.get("selftext") or ""
            text = self._decode_reddit_text(title, selftext)
            if not text or not self._reddit_post_matches_query(text, query):
                continue

            permalink = data.get("permalink") or ""
            posts.append({
                "text": text[:500],
                "created_at": str(data.get("created_utc") or ""),
                "id": str(data.get("id") or ""),
                "subreddit": str(data.get("subreddit") or ""),
                "score": int(data.get("score") or 0),
                "url": f"https://reddit.com{permalink}" if permalink else "",
            })

            if len(posts) >= self.result_limit:
                break

        return posts
    
    def _parse_youtube_comment(
        self,
        comment_item: Dict,
        video_id: str,
        video_title: str,
    ) -> Dict | None:
        """Parse and filter a single comment. Returns comment dict or None if filtered out."""
        comment = comment_item["snippet"]["topLevelComment"]["snippet"]
        raw_text = comment.get("textDisplay", "")
        text_plain = re.sub(r"<.*?>", "", raw_text).strip()
        text_plain = html.unescape(text_plain).strip()
        if len(text_plain) < 10:
            return None
        lowered = text_plain.lower()
        words = re.findall(r"[a-zA-Z]+", lowered)
        greeting_words = {
            "hi", "hii", "hiii", "hello", "hey", "nice", "cool", "wow",
            "ok", "okay", "love", "awesome", "superb",
        }
        if words and len(words) <= 3 and all(w in greeting_words for w in words):
            return None

        spec_keywords = {
            "camera", "battery", "screen", "display", "refresh", "hz",
            "processor", "chip", "snapdragon", "dimensity", "ram", "storage",
            "charging", "charge", "fast charge", "charging speed", "performance",
            "lag", "lags", "laggy", "frame drop", "fps", "heating", "overheat",
            "temperature", "speaker", "audio", "mic", "microphone", "build quality",
            "durability", "fingerprint", "face unlock", "sensor", "5g", "network",
            "signal", "display quality", "brightness", "outdoor visibility",
            "standby", "sot", "backup",
        }
        experience_keywords = {
            "experience", "using", "usage", "daily use", "day to day", "gaming",
            "pubg", "bgmi", "genshin", "multitasking", "smooth", "stutter",
            "bug", "issue", "problem", "update", "ui", "software", "oneui",
            "miui", "hyperos", "oxygenos", "coloros",
        }
        opinion_keywords = {
            "good", "bad", "better", "best", "worth", "value", "satisfied",
            "disappointed", "awesome", "terrible", "amazing", "poor", "average",
            "ok", "okay", "fine",
        }
        lowered_text = text_plain.lower()
        has_spec = any(k in lowered_text for k in spec_keywords)
        has_experience = any(k in lowered_text for k in experience_keywords)
        has_opinion = any(k in lowered_text for k in opinion_keywords)
        if not ((has_spec or has_experience) and has_opinion):
            return None

        return {
            "text": text_plain,
            "created_at": comment["publishedAt"],
            "id": comment_item["id"],
            "video_id": video_id,
            "video_title": video_title,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "like_count": comment.get("likeCount", 0),
        }

    def _fetch_comments_for_video(
        self,
        video_id: str,
        video_title: str,
        max_comments: int,
    ) -> List[Dict]:
        """Fetch and filter comments for one video, up to max_comments."""
        comments: List[Dict] = []
        page_token = None
        per_page = min(100, max(50, max_comments))

        while len(comments) < max_comments:
            comment_response = self.youtube_client.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=per_page,
                order="relevance",
                pageToken=page_token,
            ).execute()

            for comment_item in comment_response.get("items", []):
                if len(comments) >= max_comments:
                    break
                parsed = self._parse_youtube_comment(comment_item, video_id, video_title)
                if parsed:
                    comments.append(parsed)

            page_token = comment_response.get("nextPageToken")
            if not page_token:
                break

        return comments

    def collect_youtube(self, query: str) -> List[Dict]:
        """Collect the most-liked comments from the top N highest-viewed videos for the query.

        Strategy:
        - Search YouTube with order=viewCount so we get the highest-viewed videos for the query
        - Filter to videos longer than 180 seconds (proper reviews, not shorts)
        - Take the top N by view count (default 10, set via YOUTUBE_VIDEO_COUNT)
        - Fetch comments from each of those 10 videos
        - Aggregate all comments, sort by like_count (most liked first), return top result_limit
        """
        if self.youtube_client:
            try:
                # Search by VIEW COUNT so we get the actual top highest-viewed videos for the query
                search_response = self.youtube_client.search().list(
                    q=query,
                    part='id,snippet',
                    type='video',
                    maxResults=50,
                    order='viewCount'
                ).execute()

                videos_found = search_response.get('items', [])
                if not videos_found:
                    print(f"YouTube API: No videos found for query '{query}'")
                    return []

                video_ids = [item["id"]["videoId"] for item in videos_found if "videoId" in item["id"]]
                details_resp = self.youtube_client.videos().list(
                    part="contentDetails,statistics,snippet",
                    id=",".join(video_ids),
                    maxResults=len(video_ids),
                ).execute()

                # Build list with duration and view count; keep only videos >= 180s
                candidates = []
                for v in details_resp.get("items", []):
                    vid = v["id"]
                    stats = v.get("statistics", {}) or {}
                    content = v.get("contentDetails", {}) or {}
                    duration_iso = content.get("duration", "PT0S")
                    duration_sec = self._parse_duration_seconds(duration_iso)
                    view_count = int(stats.get("viewCount", 0))
                    comment_count = int(stats.get("commentCount", 0)) if "commentCount" in stats else 0
                    if duration_sec < 180:
                        continue
                    candidates.append({
                        "id": vid,
                        "title": (v.get("snippet") or {}).get("title", ""),
                        "views": view_count,
                        "comments": comment_count,
                    })

                if not candidates:
                    print(f"YouTube API: No videos longer than 180s for query '{query}'")
                    return []

                # Already from viewCount search; sort by views desc and take top N
                candidates.sort(key=lambda c: c["views"], reverse=True)
                top_videos = candidates[: self.youtube_video_count]
                print(
                    f"YouTube API: Using top {len(top_videos)} videos for query '{query}' "
                    f"(views range {top_videos[-1]['views']}–{top_videos[0]['views']})"
                )

                # Per-video comment cap so we get a mix from all videos
                per_video = max(15, (self.result_limit * 2) // len(top_videos))
                all_comments: List[Dict] = []

                for rank, vid_info in enumerate(top_videos, 1):
                    video_id = vid_info["id"]
                    video_title = vid_info["title"]
                    try:
                        video_comments = self._fetch_comments_for_video(
                            video_id, video_title, per_video
                        )
                        all_comments.extend(video_comments)
                        if video_comments:
                            print(
                                f"  Video {rank}: '{video_title[:50]}...' "
                                f"-> {len(video_comments)} comments"
                            )
                    except Exception as e:
                        print(f"  Video {rank} ({video_id}): fetch error: {e}")

                if all_comments:
                    all_comments.sort(key=lambda c: c.get("like_count", 0), reverse=True)
                    top_n = min(self.result_limit, len(all_comments))
                    print(
                        f"YouTube API: Returning top {top_n} comments from "
                        f"{len(all_comments)} across {len(top_videos)} videos"
                    )
                    return all_comments[:top_n]
                print(f"YouTube API: No comments found for query '{query}'")
            except Exception as e:
                print(f"YouTube API error: {e}")

        return []

    def _parse_duration_seconds(self, iso_duration: str) -> int:
        """
        Convert ISO 8601 duration (e.g. 'PT5M30S') to total seconds.
        Handles hours, minutes, seconds; ignores days/months/years for this use case.
        """
        if not iso_duration or not iso_duration.startswith("PT"):
            return 0

        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        match = re.match(pattern, iso_duration)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds



