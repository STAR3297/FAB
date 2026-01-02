import { useState } from "react";
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

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:5000";

const popularKeywords = ["iPhone 16", "Poco F7", "MacBook Air", "Samsung S24", "Nothing CMF"];
const bgImages = [
  "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1527443224154-dc6d412cda3f?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1511396275275-2a9e52a534dd?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1502877828070-33dc21c7be1c?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=60",
  "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=900&q=60",
];

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [selectedKeyword, setSelectedKeyword] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResults(null);
    setSelectedKeyword(null); // Reset selected keyword on new search
    
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

  // Filter data by selected keyword
  const getFilteredData = () => {
    if (!selectedKeyword || !results) return null;

    const filtered = {
      keyword: selectedKeyword,
      platforms: {},
      totalItems: 0,
      items: []
    };

    // Search through all platforms for items containing the keyword
    Object.entries(results.platforms).forEach(([platform, data]) => {
      const platformItems = [];
      
      // Use all_items if available, otherwise fall back to sample_items
      const itemsToSearch = data.all_items || data.sample_items || [];
      
      itemsToSearch.forEach(item => {
        if (item.text && item.text.toLowerCase().includes(selectedKeyword.toLowerCase())) {
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

  const filteredData = getFilteredData();

  return (
    <>
      <div className="bg-marquee">
        <div className="marquee-track">
          {bgImages.concat(bgImages).map((src, i) => (
            <div key={`bg-a-${i}`} className="marquee-img" style={{ backgroundImage: `url(${src})` }} />
          ))}
        </div>
        <div className="marquee-track reverse">
          {bgImages.concat(bgImages).map((src, i) => (
            <div key={`bg-b-${i}`} className="marquee-img" style={{ backgroundImage: `url(${src})` }} />
          ))}
        </div>
      </div>

      <div className="page">
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
          <p className="error-hint">Make sure the backend is running on {API_BASE}</p>
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
          {/* Summary Section - Displayed First */}
          <section className="card summary-card fade-in">
            <div className="summary-header">
              <h2>Analysis Summary</h2>
              <span className="query-badge">{results.query}</span>
            </div>
            <div className="summary-content">
              <p className="summary-paragraph">{results.combined.summary}</p>
            </div>
          </section>

          {/* Detailed Results Section - Displayed Below */}
          <section className="card results fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="results-header">
              <h3>Detailed Analysis</h3>
            </div>

            <div className="stats-grid">
            <div className="stat-card animate-in" style={{ animationDelay: '0.1s' }}>
              <div className="stat-icon">📊</div>
              <div className="stat-label">Total Items</div>
              <div className="stat-value">{results.combined.total_items}</div>
            </div>
            <div className="stat-card positive animate-in" style={{ animationDelay: '0.2s' }}>
              <div className="stat-icon">👍</div>
              <div className="stat-label">Positive</div>
              <div className="stat-value">{results.combined.sentiment_counts.positive}</div>
              <div className="stat-percentage">
                {results.combined.total_items > 0
                  ? Math.round((results.combined.sentiment_counts.positive / results.combined.total_items) * 100)
                  : 0}%
              </div>
            </div>
            <div className="stat-card neutral animate-in" style={{ animationDelay: '0.3s' }}>
              <div className="stat-icon">😐</div>
              <div className="stat-label">Neutral</div>
              <div className="stat-value">{results.combined.sentiment_counts.neutral}</div>
              <div className="stat-percentage">
                {results.combined.total_items > 0
                  ? Math.round((results.combined.sentiment_counts.neutral / results.combined.total_items) * 100)
                  : 0}%
              </div>
            </div>
            <div className="stat-card negative animate-in" style={{ animationDelay: '0.4s' }}>
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
                </div>
              ))}
            </div>
          </div>

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

          {/* Filtered Results Section */}
          {filteredData && (
            <div className="filtered-results-section fade-in">
              <div className="filtered-header">
                <h3>
                  <span className="filter-icon">🔍</span>
                  Results for "{filteredData.keyword}"
                </h3>
                <span className="filter-count">{filteredData.totalItems} items found</span>
              </div>
              
              <div className="filtered-items">
                {Object.entries(filteredData.platforms).map(([platform, platformData]) => (
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
