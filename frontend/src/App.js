import { useState, useEffect, useRef } from "react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import "./App.css";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

// In development, use same-origin paths so CRA `proxy` forwards to Flask (avoids CORS issues).
// Set REACT_APP_API_BASE when the API is on another host (e.g. production).
const API_BASE = (() => {
  const env = process.env.REACT_APP_API_BASE;
  if (env && env.trim()) return env.replace(/\/$/, "");
  if (process.env.NODE_ENV === "development") return "";
  return "http://127.0.0.1:5000";
})();

const popularKeywords = ["iPhone 16", "Poco F7", "MacBook Air", "Samsung S24", "Nothing CMF"];

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [selectedSentiment, setSelectedSentiment] = useState(null);

  const youtubeSectionRef = useRef(null);
  const redditSectionRef = useRef(null);
  const filteredSectionRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResults(null);
    setSelectedKeyword(null); 
    
    try {
      const response = await fetch(`${API_BASE}/analyze?query=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
      console.error("API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const uniqueByText = (items) => {
    const seen = new Set();
    return (items || []).filter((item) => {
      if (!item || !item.text) return false;
      const key = item.text.trim().toLowerCase();
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  };

  const getFilteredData = () => {
    if (!selectedKeyword || !results) return null;

    const filtered = {
      keyword: selectedKeyword,
      platforms: {},
      totalItems: 0,
      items: []
    };

    const seenTexts = new Set();

    Object.entries(results.platforms).forEach(([platform, data]) => {
      const platformItems = [];
      
     
      const itemsToSearch = data.all_items || data.sample_items || [];
      
      itemsToSearch.forEach(item => {
        if (!item || !item.text) return;
        const normalizedText = item.text.trim().toLowerCase();
        if (!normalizedText || seenTexts.has(normalizedText)) return;
        if (item.text.toLowerCase().includes(selectedKeyword.toLowerCase())) {
          seenTexts.add(normalizedText);
          platformItems.push({
            ...item,
            platform: platform
          });
        }
      });

      if (platformItems.length > 0) {
        filtered.platforms[platform] = {
          items: platformItems,
          count: platformItems.length
        };
        filtered.items.push(...platformItems);
        filtered.totalItems += platformItems.length;
      }
    });

    return filtered.totalItems > 0 ? filtered : null;
  };

  const getSentimentFilteredData = (sentiment) => {
    if (!results || !results.platforms) return null;

    const filtered = {
      sentiment,
      platforms: {},
      totalItems: 0,
      items: [],
    };

    const seenTexts = new Set();

    Object.entries(results.platforms).forEach(([platform, data]) => {
      const itemsToSearch = data.all_items || data.sample_items || [];

      const platformItems = itemsToSearch
        .filter((item) => {
          if (!item || !item.text) return false;
          const normalizedText = item.text.trim().toLowerCase();
          if (!normalizedText || seenTexts.has(normalizedText)) return false;
          if (sentiment !== "all" && item.sentiment !== sentiment) return false;
          seenTexts.add(normalizedText);
          return true;
        })
        .map((item) => ({
          ...item,
          platform,
        }));

      if (platformItems.length > 0) {
        filtered.platforms[platform] = {
          items: platformItems,
          count: platformItems.length,
        };
        filtered.items.push(...platformItems);
        filtered.totalItems += platformItems.length;
      }
    });

    return filtered.totalItems > 0 ? filtered : null;
  };

  const filteredData = getFilteredData();
  const sentimentFilteredData = selectedSentiment
    ? getSentimentFilteredData(selectedSentiment)
    : null;
  const activeFilterData = filteredData || sentimentFilteredData;

  const handleSentimentClick = (sentiment) => {
    setSelectedSentiment((prev) => (prev === sentiment ? null : sentiment));
    // when using sentiment filter, clear any keyword filter
    setSelectedKeyword(null);
  };

  let mood = "mood-neutral";
  if (results && results.combined && results.combined.sentiment_counts) {
    const { positive = 0, negative = 0 } = results.combined.sentiment_counts;
    if (positive > negative) {
      mood = "mood-positive";
    } else if (negative > positive) {
      mood = "mood-negative";
    }
  }

  useEffect(() => {
    if (selectedPlatform === 'youtube' && youtubeSectionRef.current) {
      youtubeSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (selectedPlatform === 'reddit' && redditSectionRef.current) {
      redditSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [selectedPlatform]);

  useEffect(() => {
    if (selectedSentiment && filteredSectionRef.current && activeFilterData) {
      filteredSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [selectedSentiment, activeFilterData]);

  return (
    <>
      <div className={`bg-system ${mood}`}>
        <div className="bg-grid" />
        <div className="bg-orbit bg-orbit-1" />
        <div className="bg-orbit bg-orbit-2" />
        <div className="bg-orbit bg-orbit-3" />
      </div>

      <div className={`page ${mood}`}>
      <header className="hero">
        <div className="badge">Real-time feedback</div>
        <h1>Search product buzz across platforms</h1>
        <p>Enter a keyword to explore what people are saying right now.</p>
        <form className="search" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder='Try "Poco F7" or "AirPods Pro"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              "Search"
            )}
          </button>
        </form>
        <div className="ticker">
          <div className="ticker-track">
            {["Electronics", "Stocks", "Cars", "Bikes", "Laptops", "Phones", "Cameras", "Headphones"].map((item, i) => (
              <span key={i} className="ticker-item">
                ● {item}
              </span>
            ))}
            {["Electronics", "Stocks", "Cars", "Bikes", "Laptops", "Phones", "Cameras", "Headphones"].map((item, i) => (
              <span key={`dup-${i}`} className="ticker-item">
                ● {item}
              </span>
            ))}
          </div>
        </div>
      </header>

      {error && (
        <section className="card error">
          <p className="error-message">⚠️ {error}</p>
          <p className="error-hint">
            {API_BASE
              ? `Start the Flask backend at ${API_BASE} (e.g. cd backend && flask --app app run --debug).`
              : "Start the Flask backend on port 5000 (e.g. cd backend && flask --app app run --debug), then restart npm start if you just added proxy."}
          </p>
        </section>
      )}

      {loading && (
        <section className="card loading-card">
          <div className="loading-content">
            <div className="loading-spinner-large"></div>
            <p>Analyzing feedback across platforms...</p>
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </section>
      )}

      {results && (
        <>
          {}
          <section className="card summary-card fade-in">
            <div className="summary-header">
              <h2>Analysis Summary</h2>
              <span className="query-badge">{results.query}</span>
            </div>
            <div className="summary-content">
              <p className="summary-paragraph">{results.combined.summary}</p>
            </div>
          </section>

          {}
          <section className="card results fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="results-header">
              <h3>Detailed Analysis</h3>
            </div>

            <div className="stats-grid">
            <div
              className={`stat-card animate-in filterable ${selectedSentiment === 'all' ? 'active' : ''}`}
              style={{ animationDelay: '0.1s' }}
              onClick={() => handleSentimentClick('all')}
            >
              <div className="stat-icon">📊</div>
              <div className="stat-label">Total Items</div>
              <div className="stat-value">{results.combined.total_items}</div>
            </div>
            <div
              className={`stat-card positive animate-in filterable ${selectedSentiment === 'positive' ? 'active' : ''}`}
              style={{ animationDelay: '0.2s' }}
              onClick={() => handleSentimentClick('positive')}
            >
              <div className="stat-icon">👍</div>
              <div className="stat-label">Positive</div>
              <div className="stat-value">{results.combined.sentiment_counts.positive}</div>
              <div className="stat-percentage">
                {results.combined.total_items > 0
                  ? Math.round((results.combined.sentiment_counts.positive / results.combined.total_items) * 100)
                  : 0}%
              </div>
            </div>
            <div
              className={`stat-card neutral animate-in filterable ${selectedSentiment === 'neutral' ? 'active' : ''}`}
              style={{ animationDelay: '0.3s' }}
              onClick={() => handleSentimentClick('neutral')}
            >
              <div className="stat-icon">😐</div>
              <div className="stat-label">Neutral</div>
              <div className="stat-value">{results.combined.sentiment_counts.neutral}</div>
              <div className="stat-percentage">
                {results.combined.total_items > 0
                  ? Math.round((results.combined.sentiment_counts.neutral / results.combined.total_items) * 100)
                  : 0}%
              </div>
            </div>
            <div
              className={`stat-card negative animate-in filterable ${selectedSentiment === 'negative' ? 'active' : ''}`}
              style={{ animationDelay: '0.4s' }}
              onClick={() => handleSentimentClick('negative')}
            >
              <div className="stat-icon">👎</div>
              <div className="stat-label">Negative</div>
              <div className="stat-value">{results.combined.sentiment_counts.negative}</div>
              <div className="stat-percentage">
                {results.combined.total_items > 0
                  ? Math.round((results.combined.sentiment_counts.negative / results.combined.total_items) * 100)
                  : 0}%
              </div>
            </div>
          </div>

          <div className="charts-section">
            <div className="chart-container">
              <h3>Sentiment Distribution</h3>
              <Doughnut
                data={{
                  labels: ['Positive', 'Neutral', 'Negative'],
                  datasets: [
                    {
                      data: [
                        results.combined.sentiment_counts.positive,
                        results.combined.sentiment_counts.neutral,
                        results.combined.sentiment_counts.negative,
                      ],
                      backgroundColor: ['#22c55e', '#eab308', '#ef4444'],
                      borderWidth: 0,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        padding: 15,
                        font: {
                          size: 13,
                          weight: '600',
                        },
                      },
                    },
                    tooltip: {
                      backgroundColor: 'rgba(0, 0, 0, 0.8)',
                      padding: 12,
                      titleFont: { size: 14 },
                      bodyFont: { size: 13 },
                    },
                  },
                }}
              />
            </div>
            <div className="chart-container">
              <h3>Platform Comparison</h3>
              <Bar
                data={{
                  labels: Object.keys(results.platforms).map(p => p.charAt(0).toUpperCase() + p.slice(1)),
                  datasets: [
                    {
                      label: 'Positive',
                      data: Object.values(results.platforms).map(p => p.sentiment_counts.positive),
                      backgroundColor: '#22c55e',
                    },
                    {
                      label: 'Neutral',
                      data: Object.values(results.platforms).map(p => p.sentiment_counts.neutral),
                      backgroundColor: '#eab308',
                    },
                    {
                      label: 'Negative',
                      data: Object.values(results.platforms).map(p => p.sentiment_counts.negative),
                      backgroundColor: '#ef4444',
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        padding: 15,
                        font: {
                          size: 13,
                          weight: '600',
                        },
                      },
                    },
                    tooltip: {
                      backgroundColor: 'rgba(0, 0, 0, 0.8)',
                      padding: 12,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        stepSize: 1,
                      },
                    },
                  },
                }}
              />
            </div>
          </div>

          <div className="platforms-section">
            <h3>Platform Breakdown</h3>
            <div className="platforms-grid">
              {Object.entries(results.platforms).map(([platform, data], idx) => (
                <div key={platform} className="platform-card animate-in" style={{ animationDelay: `${0.5 + idx * 0.1}s` }}>
                  <div className="platform-header">
                    <div className="platform-title">
                      <span className="platform-icon">
                        {platform === 'twitter' ? '🐦' : platform === 'reddit' ? '🔴' : '📺'}
                      </span>
                      <h4>{platform.charAt(0).toUpperCase() + platform.slice(1)}</h4>
                    </div>
                    <span className="platform-count">{data.total} items</span>
                  </div>
                  <div className="platform-stats">
                    <span className="sentiment-badge positive">
                      👍 {data.sentiment_counts.positive}
                    </span>
                    <span className="sentiment-badge neutral">
                      😐 {data.sentiment_counts.neutral}
                    </span>
                    <span className="sentiment-badge negative">
                      👎 {data.sentiment_counts.negative}
                    </span>
                  </div>
                  {data.top_keywords.length > 0 && (
                    <div className="keywords">
                      <strong>Top keywords:</strong> {data.top_keywords.slice(0, 5).join(", ")}
                    </div>
                  )}
                  {(platform === 'youtube' || platform === 'reddit') && (data.all_items || data.sample_items)?.length > 0 && (
                    <button
                      type="button"
                      className="view-comments-btn"
                      onClick={() =>
                        setSelectedPlatform(
                          selectedPlatform === platform ? null : platform
                        )
                      }
                    >
                      {selectedPlatform === platform
                        ? (platform === 'youtube' ? 'Hide comments' : 'Hide posts')
                        : (platform === 'youtube' ? 'View comments' : 'View posts')}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {selectedPlatform === 'youtube' && results.platforms.youtube && (
            <div
              className="youtube-comments-section platform-items-section"
              ref={youtubeSectionRef}
            >
              <h3>Top YouTube Comments</h3>
              <div className="filtered-items-list">
                {uniqueByText(results.platforms.youtube.all_items || results.platforms.youtube.sample_items || []).map(
                  (item, idx) => (
                    <div key={idx} className="filtered-item-card">
                      <div className="item-sentiment-badge">
                        <span className={`sentiment-indicator ${item.sentiment}`}>
                          {item.sentiment === 'positive'
                            ? '👍'
                            : item.sentiment === 'negative'
                            ? '👎'
                            : '😐'}
                        </span>
                        <span className="sentiment-label">{item.sentiment}</span>
                      </div>
                      <p className="item-text">{item.text}</p>
                      {item.video_url && (
                        <a
                          href={item.video_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="video-link"
                        >
                          Watch Video →
                        </a>
                      )}
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {selectedPlatform === 'reddit' && results.platforms.reddit && (
            <div
              className="reddit-posts-section platform-items-section"
              ref={redditSectionRef}
            >
              <h3>Reddit Posts</h3>
              <div className="filtered-items-list">
                {uniqueByText(results.platforms.reddit.all_items || results.platforms.reddit.sample_items || []).map(
                  (item, idx) => (
                    <div key={idx} className="filtered-item-card">
                      <div className="item-sentiment-badge">
                        <span className={`sentiment-indicator ${item.sentiment}`}>
                          {item.sentiment === 'positive'
                            ? '👍'
                            : item.sentiment === 'negative'
                            ? '👎'
                            : '😐'}
                        </span>
                        <span className="sentiment-label">{item.sentiment}</span>
                      </div>
                      {item.subreddit && (
                        <span className="item-meta">r/{item.subreddit}</span>
                      )}
                      <p className="item-text">{item.text}</p>
                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="video-link"
                        >
                          View on Reddit →
                        </a>
                      )}
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {results.combined.top_keywords.length > 0 && (
            <div className="keywords-section">
              <h3>Top Keywords Overall</h3>
              <div className="keywords-list">
                {results.combined.top_keywords.map((keyword, i) => (
                  <span
                    key={i}
                    className={`keyword-tag ${selectedKeyword === keyword ? 'active' : ''}`}
                    onClick={() => setSelectedKeyword(selectedKeyword === keyword ? null : keyword)}
                    style={{ cursor: 'pointer' }}
                  >
                    {keyword}
                  </span>
                ))}
              </div>
              {selectedKeyword && (
                <button
                  className="clear-filter-btn"
                  onClick={() => setSelectedKeyword(null)}
                >
                  Clear filter
                </button>
              )}
            </div>
          )}

          {}
          {activeFilterData && (
            <div
              className="filtered-results-section fade-in"
              ref={filteredSectionRef}
            >
              <div className="filtered-header">
                <h3>
                  <span className="filter-icon">🔍</span>
                  {filteredData
                    ? `Results for "${activeFilterData.keyword}"`
                    : selectedSentiment === 'all'
                    ? 'All items'
                    : `Showing ${selectedSentiment} items`}
                </h3>
                <span className="filter-count">{activeFilterData.totalItems} items found</span>
              </div>
              
              <div className="filtered-items">
                {Object.entries(activeFilterData.platforms).map(([platform, platformData]) => (
                  <div key={platform} className="filtered-platform">
                    <div className="filtered-platform-header">
                      <span className="platform-icon">
                        {platform === 'twitter' ? '🐦' : platform === 'reddit' ? '🔴' : '📺'}
                      </span>
                      <h4>{platform.charAt(0).toUpperCase() + platform.slice(1)}</h4>
                      <span className="platform-item-count">{platformData.count} items</span>
                    </div>
                    <div className="filtered-items-list">
                      {platformData.items.map((item, idx) => (
                        <div key={idx} className="filtered-item-card">
                          <div className="item-sentiment-badge">
                            <span className={`sentiment-indicator ${item.sentiment}`}>
                              {item.sentiment === 'positive' ? '👍' : item.sentiment === 'negative' ? '👎' : '😐'}
                            </span>
                            <span className="sentiment-label">{item.sentiment}</span>
                          </div>
                          <p className="item-text">{item.text}</p>
                          {item.video_url && (
                            <a
                              href={item.video_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="video-link"
                            >
                              Watch Video →
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          </section>
        </>
      )}

      {!results && (
        <section className="card popular">
          <div className="card-header">
            <h2>Popular searches</h2>
            <p>Tap to autofill</p>
          </div>
          <div className="chips">
            {popularKeywords.map((item) => (
              <button
                key={item}
                className="chip"
                type="button"
                onClick={() => setQuery(item)}
                disabled={loading}
              >
                {item}
              </button>
            ))}
          </div>
        </section>
      )}
      </div>
    </>
  );
}

export default App;
