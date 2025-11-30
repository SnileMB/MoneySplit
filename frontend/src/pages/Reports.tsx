import React, { useState, useEffect } from "react";
import { forecastApi, exportApi, visualizationApi, Forecast } from "../api/client";

const Reports: React.FC = () => {
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [showConfidenceInfo, setShowConfidenceInfo] = useState(false);
  const [showModelInfo, setShowModelInfo] = useState(false);

  useEffect(() => {
    loadForecast();
  }, []);

  const loadForecast = async () => {
    setLoading(true);
    try {
      const response = await forecastApi.getRevenueForecast(3);
      setForecast(response.data);
    } catch (error) {
      console.error("Error loading forecast:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>📊 Reports & Analytics</h2>
        <p>Advanced visualizations, AI predictions, and export options</p>
      </div>

      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)",
        border: "2px solid rgba(102, 126, 234, 0.4)",
      }}>
        <h3 style={{ marginBottom: "12px", display: "flex", alignItems: "center", gap: "16px" }}>
          <span style={{ fontSize: "40px" }}>📈</span>
          Interactive Visualizations
        </h3>
        <p style={{ marginBottom: "32px", color: "rgba(255, 255, 255, 0.8)", fontSize: "16px", fontWeight: 500 }}>
          Click any visualization to open it in a new tab with interactive charts
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
          <div
            onClick={() => window.open(visualizationApi.getRevenueSummary(), "_blank")}
            style={{
              cursor: "pointer",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "24px",
              padding: "32px",
              border: "2px solid rgba(102, 126, 234, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 30px 80px rgba(102, 126, 234, 0.5), 0 0 60px rgba(102, 126, 234, 0.4)";
              e.currentTarget.style.borderColor = "rgba(102, 126, 234, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(102, 126, 234, 0.3)";
            }}
          >
            <div style={{ fontSize: "56px", marginBottom: "16px", textAlign: "center" }}>📈</div>
            <h4 style={{ color: "white", fontSize: "20px", fontWeight: 700, textAlign: "center", marginBottom: "8px" }}>
              Revenue Summary
            </h4>
            <p style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px", textAlign: "center" }}>
              Year-over-year revenue analysis
            </p>
          </div>

          <div
            onClick={() => window.open(visualizationApi.getMonthlyTrends(), "_blank")}
            style={{
              cursor: "pointer",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "24px",
              padding: "32px",
              border: "2px solid rgba(118, 75, 162, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 30px 80px rgba(118, 75, 162, 0.5), 0 0 60px rgba(118, 75, 162, 0.4)";
              e.currentTarget.style.borderColor = "rgba(118, 75, 162, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(118, 75, 162, 0.3)";
            }}
          >
            <div style={{ fontSize: "56px", marginBottom: "16px", textAlign: "center" }}>📅</div>
            <h4 style={{ color: "white", fontSize: "20px", fontWeight: 700, textAlign: "center", marginBottom: "8px" }}>
              Monthly Trends
            </h4>
            <p style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px", textAlign: "center" }}>
              Performance over time
            </p>
          </div>

          <div
            onClick={() => window.open(visualizationApi.getWorkDistribution(), "_blank")}
            style={{
              cursor: "pointer",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "24px",
              padding: "32px",
              border: "2px solid rgba(240, 147, 251, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 30px 80px rgba(240, 147, 251, 0.5), 0 0 60px rgba(240, 147, 251, 0.4)";
              e.currentTarget.style.borderColor = "rgba(240, 147, 251, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(240, 147, 251, 0.3)";
            }}
          >
            <div style={{ fontSize: "56px", marginBottom: "16px", textAlign: "center" }}>🥧</div>
            <h4 style={{ color: "white", fontSize: "20px", fontWeight: 700, textAlign: "center", marginBottom: "8px" }}>
              Work Distribution
            </h4>
            <p style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px", textAlign: "center" }}>
              Team contribution breakdown
            </p>
          </div>

          <div
            onClick={() => window.open(visualizationApi.getTaxComparison(), "_blank")}
            style={{
              cursor: "pointer",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "24px",
              padding: "32px",
              border: "2px solid rgba(16, 185, 129, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 30px 80px rgba(16, 185, 129, 0.5), 0 0 60px rgba(16, 185, 129, 0.4)";
              e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.3)";
            }}
          >
            <div style={{ fontSize: "56px", marginBottom: "16px", textAlign: "center" }}>💰</div>
            <h4 style={{ color: "white", fontSize: "20px", fontWeight: 700, textAlign: "center", marginBottom: "8px" }}>
              Tax Comparison
            </h4>
            <p style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px", textAlign: "center" }}>
              Individual vs Business tax
            </p>
          </div>

          <div
            onClick={() => window.open(visualizationApi.getProjectProfitability(), "_blank")}
            style={{
              cursor: "pointer",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "24px",
              padding: "32px",
              border: "2px solid rgba(251, 191, 36, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 30px 80px rgba(251, 191, 36, 0.5), 0 0 60px rgba(251, 191, 36, 0.4)";
              e.currentTarget.style.borderColor = "rgba(251, 191, 36, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(251, 191, 36, 0.3)";
            }}
          >
            <div style={{ fontSize: "56px", marginBottom: "16px", textAlign: "center" }}>💵</div>
            <h4 style={{ color: "white", fontSize: "20px", fontWeight: 700, textAlign: "center", marginBottom: "8px" }}>
              Profitability
            </h4>
            <p style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px", textAlign: "center" }}>
              Project profit margins
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(118, 75, 162, 0.15) 0%, rgba(240, 147, 251, 0.15) 100%)",
        border: "2px solid rgba(118, 75, 162, 0.4)",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
          <h3 style={{ display: "flex", alignItems: "center", gap: "16px", margin: 0 }}>
            <span style={{ fontSize: "40px" }}>🔮</span>
            AI Revenue Forecast
          </h3>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button
              onClick={() => setShowConfidenceInfo(!showConfidenceInfo)}
              style={{
                padding: "10px 20px",
                borderRadius: "12px",
                border: "2px solid rgba(138, 116, 249, 0.4)",
                background: "rgba(138, 116, 249, 0.1)",
                color: "rgba(255, 255, 255, 0.9)",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: 600,
                transition: "all 0.3s ease",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(138, 116, 249, 0.2)";
                e.currentTarget.style.transform = "scale(1.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(138, 116, 249, 0.1)";
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              <span>{showConfidenceInfo ? "❌" : "ℹ️"}</span>
              {showConfidenceInfo ? "Close" : "What is Confidence?"}
            </button>
            <button
              onClick={() => setShowModelInfo(!showModelInfo)}
              style={{
                padding: "10px 20px",
                borderRadius: "12px",
                border: "2px solid rgba(240, 147, 251, 0.4)",
                background: "rgba(240, 147, 251, 0.1)",
                color: "rgba(255, 255, 255, 0.9)",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: 600,
                transition: "all 0.3s ease",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(240, 147, 251, 0.2)";
                e.currentTarget.style.transform = "scale(1.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(240, 147, 251, 0.1)";
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              <span>{showModelInfo ? "❌" : "🤖"}</span>
              {showModelInfo ? "Close" : "AI Models Explained"}
            </button>
          </div>
        </div>

        {showConfidenceInfo && (
          <div style={{
            padding: "20px",
            background: "rgba(138, 116, 249, 0.15)",
            borderRadius: "16px",
            border: "2px solid rgba(138, 116, 249, 0.3)",
            marginBottom: "24px",
          }}>
            <h4 style={{ color: "white", marginBottom: "12px", fontSize: "18px", fontWeight: 700 }}>
              📊 Understanding Confidence Levels
            </h4>
            <div style={{ color: "rgba(255, 255, 255, 0.85)", lineHeight: "1.6", fontSize: "15px" }}>
              <p style={{ marginBottom: "12px" }}>
                <strong style={{ color: "#10b981" }}>High Confidence:</strong> The AI has found strong, consistent patterns in your data (R² &gt; 0.7). Predictions are highly reliable.
              </p>
              <p style={{ marginBottom: "12px" }}>
                <strong style={{ color: "#f59e0b" }}>Medium Confidence:</strong> Moderate patterns detected (R² 0.4-0.7). Predictions are reasonably accurate but may vary.
              </p>
              <p style={{ marginBottom: "12px" }}>
                <strong style={{ color: "#ef4444" }}>Low Confidence:</strong> Limited or inconsistent data patterns (R² &lt; 0.4). Predictions should be taken as rough estimates.
              </p>
              <p style={{ marginTop: "16px", paddingTop: "16px", borderTop: "1px solid rgba(255, 255, 255, 0.2)" }}>
                💡 <strong>Tip:</strong> Confidence improves with more historical data. Add more projects over time for better predictions!
              </p>
            </div>
          </div>
        )}

        {showModelInfo && (
          <div style={{
            padding: "24px",
            background: "rgba(240, 147, 251, 0.15)",
            borderRadius: "16px",
            border: "2px solid rgba(240, 147, 251, 0.3)",
            marginBottom: "24px",
          }}>
            <h4 style={{ color: "white", marginBottom: "16px", fontSize: "18px", fontWeight: 700 }}>
              🤖 AI Forecasting Models Explained
            </h4>
            <div style={{ color: "rgba(255, 255, 255, 0.85)", lineHeight: "1.8", fontSize: "15px" }}>
              <div style={{ marginBottom: "20px", padding: "16px", background: "rgba(102, 126, 234, 0.1)", borderRadius: "12px", border: "1px solid rgba(102, 126, 234, 0.2)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
                  <span style={{ fontSize: "24px" }}>📈</span>
                  <strong style={{ color: "#667eea", fontSize: "16px" }}>Linear Regression (Straight Line)</strong>
                </div>
                <p style={{ marginBottom: "8px" }}>
                  <strong>When used:</strong> Automatically selected when you have 2-5 months of data
                </p>
                <p style={{ marginBottom: "8px" }}>
                  <strong>How it works:</strong> Fits a straight line through your historical revenue data (y = mx + b)
                </p>
                <p style={{ marginBottom: "8px" }}>
                  <strong>Best for:</strong> Businesses with steady, consistent growth or decline
                </p>
                <p>
                  <strong>Example:</strong> If revenue grows by $5,000 each month steadily
                </p>
              </div>

              <div style={{ marginBottom: "20px", padding: "16px", background: "rgba(240, 147, 251, 0.1)", borderRadius: "12px", border: "1px solid rgba(240, 147, 251, 0.2)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
                  <span style={{ fontSize: "24px" }}>📊</span>
                  <strong style={{ color: "#f093fb", fontSize: "16px" }}>Polynomial Regression (Curved Trend)</strong>
                </div>
                <p style={{ marginBottom: "8px" }}>
                  <strong>When used:</strong> Automatically selected when you have 6+ months of data
                </p>
                <p style={{ marginBottom: "8px" }}>
                  <strong>How it works:</strong> Fits a curved line (parabola) through your data (y = ax² + bx + c)
                </p>
                <p style={{ marginBottom: "8px" }}>
                  <strong>Best for:</strong> Businesses with accelerating/decelerating growth, seasonal patterns
                </p>
                <p>
                  <strong>Example:</strong> Revenue that grows slowly at first, then rapidly accelerates
                </p>
              </div>

              <div style={{ padding: "16px", background: "rgba(16, 185, 129, 0.1)", borderRadius: "12px", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
                <strong style={{ color: "#10b981" }}>🎯 Which model is better?</strong>
                <p style={{ marginTop: "8px" }}>
                  The AI automatically chooses the best model based on your data:
                </p>
                <ul style={{ marginTop: "8px", paddingLeft: "24px" }}>
                  <li><strong>More data = Polynomial</strong> - Can capture complex patterns like seasonal spikes or growth acceleration</li>
                  <li><strong>Less data = Linear</strong> - Simpler, more stable, less likely to over-predict</li>
                  <li><strong>Moving Average Smoothing</strong> - Applied to reduce noise in volatile data (4+ months)</li>
                </ul>
              </div>

              <p style={{ marginTop: "20px", paddingTop: "20px", borderTop: "1px solid rgba(255, 255, 255, 0.2)", fontSize: "14px" }}>
                💡 <strong>Pro Tip:</strong> Polynomial models are more accurate for long-term trends, but require at least 6 months of consistent data. The "Prediction Range" shows the uncertainty - wider ranges mean more volatility in your historical data.
              </p>
            </div>
          </div>
        )}
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : forecast?.success ? (
          <>
            {/* Key Metrics Grid - 6 stats instead of 3 */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
              marginBottom: "32px",
            }}>
              <div style={{
                padding: "20px",
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)",
                borderRadius: "16px",
                border: "2px solid rgba(102, 126, 234, 0.3)",
                boxShadow: "0 8px 32px rgba(102, 126, 234, 0.2)",
              }}>
                <div style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  📈 Trend
                </div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "white", marginBottom: "4px" }}>
                  {forecast.trend}
                </div>
                <div style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.6)" }}>
                  ${Math.floor(forecast.trend_strength).toLocaleString()}/month
                </div>
              </div>

              <div style={{
                padding: "20px",
                background: "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)",
                borderRadius: "16px",
                border: "2px solid rgba(16, 185, 129, 0.3)",
                boxShadow: "0 8px 32px rgba(16, 185, 129, 0.2)",
              }}>
                <div style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  🎯 Confidence
                </div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "white", marginBottom: "4px" }}>
                  {forecast.confidence}
                </div>
                <div style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.6)" }}>
                  {(forecast.r2_score * 100).toFixed(0)}% accuracy (R² = {forecast.r2_score.toFixed(2)})
                </div>
              </div>

              <div style={{
                padding: "20px",
                background: "linear-gradient(135deg, rgba(240, 147, 251, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%)",
                borderRadius: "16px",
                border: "2px solid rgba(240, 147, 251, 0.3)",
                boxShadow: "0 8px 32px rgba(240, 147, 251, 0.2)",
              }}>
                <div style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  💰 Historical Avg
                </div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "white" }}>
                  ${Math.floor(forecast.historical_avg).toLocaleString()}
                </div>
                <div style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.6)" }}>
                  per month
                </div>
              </div>

              <div style={{
                padding: "20px",
                background: "linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%)",
                borderRadius: "16px",
                border: "2px solid rgba(251, 191, 36, 0.3)",
                boxShadow: "0 8px 32px rgba(251, 191, 36, 0.2)",
              }}>
                <div style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  📊 Growth Rate
                </div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: forecast.growth_rate >= 0 ? "#10b981" : "#ef4444" }}>
                  {forecast.growth_rate > 0 ? "+" : ""}{forecast.growth_rate.toFixed(1)}%
                </div>
                <div style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.6)" }}>
                  overall growth
                </div>
              </div>

              <div style={{
                padding: "20px",
                background: "linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%)",
                borderRadius: "16px",
                border: "2px solid rgba(139, 92, 246, 0.3)",
                boxShadow: "0 8px 32px rgba(139, 92, 246, 0.2)",
              }}>
                <div style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  🤖 AI Model
                </div>
                <div style={{ fontSize: "18px", fontWeight: 700, color: "white", marginBottom: "4px" }}>
                  {forecast.model_type}
                </div>
                <div style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.6)" }}>
                  {forecast.data_quality} data
                </div>
              </div>

              <div style={{
                padding: "20px",
                background: "linear-gradient(135deg, rgba(236, 72, 153, 0.15) 0%, rgba(219, 39, 119, 0.15) 100%)",
                borderRadius: "16px",
                border: "2px solid rgba(236, 72, 153, 0.3)",
                boxShadow: "0 8px 32px rgba(236, 72, 153, 0.2)",
              }}>
                <div style={{ fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  🔮 Next Month
                </div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "white" }}>
                  ${Math.floor(forecast.predictions[0].revenue).toLocaleString()}
                </div>
                <div style={{ fontSize: "14px", color: "rgba(255, 255, 255, 0.6)" }}>
                  {forecast.predictions[0].month}
                </div>
              </div>
            </div>

            {/* AI Explanation Section */}
            <div style={{
              padding: "28px",
              background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
              borderRadius: "20px",
              border: "2px solid rgba(138, 116, 249, 0.35)",
              marginBottom: "32px",
              boxShadow: "0 12px 40px rgba(102, 126, 234, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
            }}>
              <h4 style={{
                color: "white",
                marginBottom: "20px",
                fontSize: "20px",
                fontWeight: 800,
                display: "flex",
                alignItems: "center",
                gap: "12px",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>
                <span style={{ fontSize: "28px", filter: "drop-shadow(0 2px 8px rgba(102, 126, 234, 0.5))" }}>💡</span>
                AI Analysis Summary
              </h4>
              <div style={{
                color: "rgba(255, 255, 255, 0.9)",
                lineHeight: "1.9",
                fontSize: "15px",
                whiteSpace: "pre-line",
                background: "rgba(15, 12, 41, 0.4)",
                padding: "20px",
                borderRadius: "12px",
                border: "1px solid rgba(102, 126, 234, 0.2)",
              }}>
                {forecast.explanation}
              </div>
              <div style={{
                marginTop: "20px",
                paddingTop: "20px",
                borderTop: "2px solid rgba(102, 126, 234, 0.2)",
                background: "rgba(102, 126, 234, 0.08)",
                padding: "16px",
                borderRadius: "12px",
              }}>
                <div style={{
                  fontSize: "14px",
                  color: "rgba(255, 255, 255, 0.8)",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                  marginBottom: "8px",
                }}>
                  📌 Confidence Description
                </div>
                <div style={{
                  fontSize: "16px",
                  color: "white",
                  fontWeight: 600,
                  background: "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)",
                  padding: "12px",
                  borderRadius: "8px",
                  border: "1px solid rgba(16, 185, 129, 0.3)",
                }}>
                  {forecast.confidence_description}
                </div>
              </div>
            </div>

            {/* Predictions Table - Enhanced with ranges */}
            <div style={{ overflowX: "auto" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Predicted Revenue</th>
                    <th>Prediction Range (95% CI)</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.predictions.map((pred) => (
                    <tr key={pred.month}>
                      <td style={{
                        fontWeight: 700,
                        fontSize: "16px",
                        background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                        padding: "12px",
                        borderRadius: "8px",
                        border: "1px solid rgba(102, 126, 234, 0.25)",
                        color: "#a78bfa",
                      }}>{pred.month}</td>
                      <td style={{
                        fontWeight: 700,
                        fontSize: "18px",
                        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                      }}>
                        ${Math.floor(pred.revenue).toLocaleString()}
                      </td>
                      <td style={{
                        fontSize: "15px",
                        fontWeight: 600,
                        color: "#f59e0b",
                        background: "rgba(251, 191, 36, 0.1)",
                        padding: "12px",
                        borderRadius: "8px",
                      }}>
                        {pred.range || "N/A"}
                      </td>
                      <td style={{
                        background: pred.confidence === "High" || pred.confidence === "Medium-High"
                          ? "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%)"
                          : pred.confidence === "Medium"
                            ? "linear-gradient(135deg, rgba(251, 191, 36, 0.12) 0%, rgba(245, 158, 11, 0.12) 100%)"
                            : "linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.12) 100%)",
                        padding: "12px",
                        borderRadius: "8px",
                        border: pred.confidence === "High" || pred.confidence === "Medium-High"
                          ? "1px solid rgba(16, 185, 129, 0.25)"
                          : pred.confidence === "Medium"
                            ? "1px solid rgba(251, 191, 36, 0.25)"
                            : "1px solid rgba(239, 68, 68, 0.25)",
                      }}>
                        <span style={{
                          padding: "6px 14px",
                          borderRadius: "8px",
                          fontSize: "14px",
                          fontWeight: 700,
                          background: pred.confidence === "High" || pred.confidence === "Medium-High"
                            ? "rgba(16, 185, 129, 0.2)"
                            : pred.confidence === "Medium"
                              ? "rgba(251, 191, 36, 0.2)"
                              : "rgba(239, 68, 68, 0.2)",
                          color: pred.confidence === "High" || pred.confidence === "Medium-High"
                            ? "#10b981"
                            : pred.confidence === "Medium"
                              ? "#f59e0b"
                              : "#ef4444",
                          border: `2px solid ${pred.confidence === "High" || pred.confidence === "Medium-High"
                            ? "rgba(16, 185, 129, 0.4)"
                            : pred.confidence === "Medium"
                              ? "rgba(251, 191, 36, 0.4)"
                              : "rgba(239, 68, 68, 0.4)"}`,
                        }}>
                          {pred.confidence}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div style={{
            textAlign: "center",
            padding: "48px 24px",
            color: "#718096",
          }}>
            <div style={{ fontSize: "64px", marginBottom: "16px" }}>🔮</div>
            <p style={{ fontSize: "18px", fontWeight: 500 }}>Not enough data for forecasting</p>
            <p style={{ fontSize: "14px", marginTop: "8px" }}>Create at least 2 projects to enable ML predictions</p>
          </div>
        )}
      </div>

      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)",
        border: "2px solid rgba(16, 185, 129, 0.4)",
      }}>
        <h3 style={{ marginBottom: "16px", display: "flex", alignItems: "center", gap: "16px" }}>
          <span style={{ fontSize: "40px" }}>📄</span>
          Professional PDF Exports
        </h3>
        <p style={{ marginBottom: "32px", color: "rgba(255, 255, 255, 0.8)", fontSize: "16px", fontWeight: 500 }}>
          Download beautifully formatted PDF reports with charts, tables, and analytics
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>
          <a
            href={exportApi.exportSummaryPDF()}
            download
            style={{
              textDecoration: "none",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "20px",
              padding: "28px",
              border: "2px solid rgba(16, 185, 129, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "16px",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-8px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 25px 60px rgba(16, 185, 129, 0.5), 0 0 60px rgba(16, 185, 129, 0.3)";
              e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.3)";
            }}
          >
            <span style={{ fontSize: "56px" }}>📊</span>
            <div style={{ textAlign: "center" }}>
              <div style={{ color: "white", fontSize: "20px", fontWeight: 700, marginBottom: "8px" }}>
                Summary Report
              </div>
              <div style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px" }}>
                Complete business overview
              </div>
            </div>
          </a>
          <a
            href={exportApi.exportForecastPDF()}
            download
            style={{
              textDecoration: "none",
              background: "rgba(15, 12, 41, 0.8)",
              borderRadius: "20px",
              padding: "28px",
              border: "2px solid rgba(16, 185, 129, 0.3)",
              transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "16px",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-8px) scale(1.03)";
              e.currentTarget.style.boxShadow = "0 25px 60px rgba(16, 185, 129, 0.5), 0 0 60px rgba(16, 185, 129, 0.3)";
              e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.6)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "none";
              e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.3)";
            }}
          >
            <span style={{ fontSize: "56px" }}>🔮</span>
            <div style={{ textAlign: "center" }}>
              <div style={{ color: "white", fontSize: "20px", fontWeight: 700, marginBottom: "8px" }}>
                Forecast Report
              </div>
              <div style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "14px" }}>
                AI predictions & trends
              </div>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Reports;
