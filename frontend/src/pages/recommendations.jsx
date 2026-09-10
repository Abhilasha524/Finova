import { useEffect, useState } from "react";
import { getRecommendations } from "../api/recommendations";

function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadRecommendations() {
      try {
        const data = await getRecommendations();
        setRecommendations(data.recommendations || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadRecommendations();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          padding: "3rem",
          fontFamily: "sans-serif",
          maxWidth: 900,
          margin: "0 auto",
        }}
      >
        <h1 style={{ marginBottom: "1rem" }}>
          Saving Recommendations
        </h1>

        <p>Analyzing your spending...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          padding: "3rem",
          fontFamily: "sans-serif",
          maxWidth: 900,
          margin: "0 auto",
        }}
      >
        <h1 style={{ marginBottom: "1rem" }}>
          Saving Recommendations
        </h1>

        <p style={{ color: "red" }}>
          Error: {error}
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "3rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 900,
        margin: "0 auto",
      }}
    >
      <div
        style={{
          marginBottom: "2rem",
          textAlign: "center",
        }}
      >
        <h1
          style={{
            margin: 0,
            marginBottom: "0.75rem",
            fontSize: "2.2rem",
            lineHeight: 1.2,
          }}
        >
          Personalized Saving Recommendations
        </h1>

        <p
          style={{
            margin: 0,
            fontSize: "1rem",
            opacity: 0.8,
          }}
        >
          Recommendations based on your actual spending behaviour.
        </p>
      </div>

      {recommendations.length === 0 ? (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "1.5rem",
            textAlign: "center",
          }}
        >
          <p style={{ margin: 0 }}>
            No recommendations available yet.
          </p>
        </div>
      ) : (
        recommendations.map((recommendation, index) => (
          <div
            key={index}
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: "1.5rem",
              marginBottom: "1rem",
              boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
            }}
          >
            <h3
              style={{
                marginTop: 0,
                marginBottom: "0.75rem",
              }}
            >
              Recommendation {index + 1}
            </h3>

            <p
              style={{
                margin: 0,
                lineHeight: 1.6,
              }}
            >
              {recommendation}
            </p>
          </div>
        ))
      )}
    </div>
  );
}

export default Recommendations;