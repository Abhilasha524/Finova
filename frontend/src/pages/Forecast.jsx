import { useEffect, useState } from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

import { getForecast } from "../api/forecast";
import { formatCurrency } from "../utils/format";

function Forecast() {
  const [months, setMonths] = useState(3);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadForecast(selectedMonths = months) {
    try {
      setLoading(true);
      setError("");

      const data = await getForecast(selectedMonths);
      setForecast(data.forecast || []);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to load forecast.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadForecast(3);
  }, []);

  function handleLoadForecast() {
    loadForecast(months);
  }

  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1200,
        margin: "0 auto",
      }}
    >
      {/* HEADER */}
      <div style={{ marginBottom: "2rem" }}>
        <h1
          style={{
            margin: 0,
            marginBottom: "0.5rem",
            fontSize: "2.2rem",
            lineHeight: 1.2,
          }}
        >
          Expense Forecast
        </h1>

        <p
          style={{
            margin: 0,
            opacity: 0.75,
          }}
        >
          Predict your future expenses using your historical transaction
          patterns.
        </p>
      </div>

      {/* FORECAST CONTROLS */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
          marginBottom: "2rem",
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: "0.5rem",
          }}
        >
          Forecast Settings
        </h2>

        <p
          style={{
            marginTop: 0,
            marginBottom: "1.25rem",
            opacity: 0.7,
          }}
        >
          Select how many future months you want to predict.
        </p>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            flexWrap: "wrap",
          }}
        >
          <div>
            <label
              style={{
                display: "block",
                marginBottom: "0.4rem",
                fontWeight: "600",
              }}
            >
              Forecast Months
            </label>

            <select
              value={months}
              onChange={(e) => setMonths(Number(e.target.value))}
              style={{
                padding: "0.7rem 1rem",
                borderRadius: 8,
                border: "1px solid #bbb",
                minWidth: 150,
                backgroundColor: "white",
                color: "#111827",
                fontWeight: "500",
              }}
            >
              {Array.from(
                { length: 12 },
                (_, index) => index + 1
              ).map((month) => (
                <option
                  key={month}
                  value={month}
                  style={{
                    color: "#111827",
                    backgroundColor: "white",
                  }}
                >
                  {month} {month === 1 ? "Month" : "Months"}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleLoadForecast}
            disabled={loading}
            style={{
              padding: "0.7rem 1.2rem",
              borderRadius: 8,
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "600",
              backgroundColor: "#324635",
              color: "white",
              marginTop: "1.45rem",
            }}
          >
            {loading ? "Loading..." : "Load Forecast"}
          </button>
        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div
          style={{
            border: "1px solid #ef4444",
            borderRadius: 10,
            padding: "1rem",
            marginBottom: "1.5rem",
            color: "#ef4444",
          }}
        >
          Error: {error}
        </div>
      )}

      {/* LOADING */}
      {loading && (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "3rem 2rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "2.5rem",
              marginBottom: "1rem",
            }}
          >
            📈
          </div>

          <h2 style={{ marginBottom: "0.5rem" }}>
            Generating Forecast
          </h2>

          <p
            style={{
              margin: 0,
              opacity: 0.7,
            }}
          >
            Analyzing your historical expense data...
          </p>
        </div>
      )}

      {/* FORECAST RESULTS */}
      {!loading && !error && forecast.length > 0 && (
        <>
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: "1.5rem",
              marginBottom: "1.5rem",
            }}
          >
            <div style={{ marginBottom: "1.5rem" }}>
              <h2
                style={{
                  margin: 0,
                  marginBottom: "0.4rem",
                }}
              >
                Predicted Expenses
              </h2>

              <p
                style={{
                  margin: 0,
                  opacity: 0.7,
                }}
              >
                Estimated expenses for the next {months}{" "}
                {months === 1 ? "month" : "months"}.
              </p>
            </div>

            <div
              style={{
                width: "100%",
                height: 430,
              }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={forecast}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 20,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#d1d5db"
                  />

                  <XAxis
                    dataKey="month"
                    tick={{
                      fill: "#374151",
                      fontSize: 12,
                    }}
                    axisLine={{
                      stroke: "#9ca3af",
                    }}
                    tickLine={{
                      stroke: "#9ca3af",
                    }}
                  />

                  <YAxis
                    tick={{
                      fill: "#374151",
                      fontSize: 12,
                    }}
                    axisLine={{
                      stroke: "#9ca3af",
                    }}
                    tickLine={{
                      stroke: "#9ca3af",
                    }}
                  />

                  <Tooltip
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{
                      backgroundColor: "#ffffff",
                      border: "1px solid #d1d5db",
                      borderRadius: "8px",
                      color: "#111827",
                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08)",
                    }}
                    labelStyle={{
                      color: "#374151",
                      fontWeight: "600",
                    }}
                  />

                  <Bar
                    dataKey="predicted_expense"
                    name="Predicted Expense"
                    fill="#5f7664"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* MODEL NOTE */}
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: "1.25rem 1.5rem",
            }}
          >
            <h3
              style={{
                marginTop: 0,
                marginBottom: "0.5rem",
              }}
            >
              ℹ️ About this forecast
            </h3>

            <p
              style={{
                margin: 0,
                lineHeight: 1.6,
                opacity: 0.75,
              }}
            >
              The current forecast uses the Naive Last Value method.
              This method uses the most recent expense value as the
              prediction for future months, so the forecast may appear
              relatively flat.
            </p>
          </div>
        </>
      )}

      {/* EMPTY STATE */}
      {!loading && !error && forecast.length === 0 && (
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "3rem 2rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "3rem",
              marginBottom: "1rem",
            }}
          >
            📊
          </div>

          <h2 style={{ marginBottom: "0.75rem" }}>
            No Forecast Data Available
          </h2>

          <p
            style={{
              maxWidth: 550,
              margin: "0 auto",
              lineHeight: 1.6,
              opacity: 0.7,
            }}
          >
            We couldn't generate a forecast from your current
            transaction data. Try uploading more historical
            transactions and run the forecast again.
          </p>
        </div>
      )}
    </div>
  );
}

export default Forecast;