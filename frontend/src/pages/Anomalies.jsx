import { useEffect, useState } from "react";

import { detectAnomalies, listAnomalies } from "../api/anomalies";
import { formatCurrency } from "../utils/format";

function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  async function loadAnomalies() {
    try {
      setLoading(true);
      setError("");

      const data = await listAnomalies();
      setAnomalies(data.anomalies || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load anomalies.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRunAnalysis() {
    try {
      setRunning(true);
      setError("");

      await detectAnomalies();
      await loadAnomalies();
    } catch (err) {
      console.error(err);
      setError("Failed to run anomaly analysis.");
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    loadAnomalies();
  }, []);

  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1250,
        margin: "0 auto",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <h1
          style={{
            margin: 0,
            marginBottom: "0.5rem",
            fontSize: "2.2rem",
          }}
        >
          Anomaly Detection
        </h1>

        <p
          style={{
            margin: 0,
            opacity: 0.75,
          }}
        >
          Identify unusual transactions using machine learning-based
          anomaly detection.
        </p>
      </div>

      {/* Analysis Control */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <h3 style={{ marginTop: 0, marginBottom: "0.5rem" }}>
          Run Anomaly Analysis
        </h3>

        <p
          style={{
            marginTop: 0,
            marginBottom: "1rem",
            opacity: 0.75,
          }}
        >
          Run a fresh analysis to check your transactions for unusual
          spending patterns.
        </p>

        <button
          onClick={handleRunAnalysis}
          disabled={running}
          style={{
            padding: "0.7rem 1.2rem",
            cursor: running ? "not-allowed" : "pointer",
          }}
        >
          {running ? "Running Analysis..." : "Run Fresh Analysis"}
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "3rem 2rem",
            textAlign: "center",
          }}
        >
          <h3 style={{ marginBottom: "0.5rem" }}>
            Loading anomaly results...
          </h3>

          <p style={{ margin: 0, opacity: 0.7 }}>
            Please wait while your analysis results are loaded.
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            padding: "1rem",
            marginBottom: "1.5rem",
            color: "red",
            border: "1px solid #fca5a5",
            borderRadius: 10,
          }}
        >
          Error: {error}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && anomalies.length === 0 && (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "3.5rem 2rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "3rem",
              marginBottom: "1rem",
            }}
          >
            ✓
          </div>

          <h2
            style={{
              marginBottom: "0.75rem",
            }}
          >
            No anomalies detected
          </h2>

          <p
            style={{
              maxWidth: 600,
              margin: "0 auto",
              lineHeight: 1.6,
              opacity: 0.75,
            }}
          >
            Your current transaction data does not contain any transactions
            that have been flagged as unusual by the anomaly detection
            model.
          </p>

          <p
            style={{
              marginTop: "1rem",
              fontSize: "0.9rem",
              opacity: 0.65,
            }}
          >
            You can run a fresh analysis whenever you upload new transactions.
          </p>
        </div>
      )}

      {/* Results */}
      {!loading && !error && anomalies.length > 0 && (
        <>
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: "1rem 1.25rem",
              marginBottom: "1.5rem",
            }}
          >
            <strong>{anomalies.length}</strong>{" "}
            unusual transactions were detected.
          </div>

          <div
            style={{
              overflowX: "auto",
              border: "1px solid #ddd",
              borderRadius: 12,
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
              }}
            >
              <thead>
                <tr
                  style={{
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                  }}
                >
                  <th style={{ padding: "0.75rem" }}>Date</th>
                  <th style={{ padding: "0.75rem" }}>Description</th>
                  <th style={{ padding: "0.75rem" }}>Category</th>
                  <th style={{ padding: "0.75rem" }}>Amount</th>
                  <th style={{ padding: "0.75rem" }}>Reason</th>
                  <th style={{ padding: "0.75rem" }}>Score</th>
                </tr>
              </thead>

              <tbody>
                {anomalies.map((item) => (
                  <tr
                    key={item.transaction_id}
                    style={{
                      borderBottom: "1px solid #eee",
                    }}
                  >
                    <td style={{ padding: "0.75rem" }}>
                      {item.txn_date}
                    </td>

                    <td style={{ padding: "0.75rem" }}>
                      {!item.description ||
                      String(item.description).toLowerCase() === "nan"
                        ? "(no description)"
                        : item.description}
                    </td>

                    <td style={{ padding: "0.75rem" }}>
                      {item.category}
                    </td>

                    <td style={{ padding: "0.75rem" }}>
                      {formatCurrency(item.amount)}
                    </td>

                    <td style={{ padding: "0.75rem" }}>
                      {item.reason}
                    </td>

                    <td style={{ padding: "0.75rem" }}>
                      {Number(item.anomaly_score).toFixed(3)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default Anomalies;