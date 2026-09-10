import { useEffect, useState } from "react";

import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { getAnalyticsSummary } from "../api/analytics";
import { formatCurrency } from "../utils/format";
import StatCard from "../components/StatCard";

const PIE_COLORS = [
  "#4f46e5",
  "#0ea5e9",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
  "#14b8a6",
  "#6366f1",
  "#06b6d4",
  "#22c55e",
  "#eab308",
  "#f43f5e",
  "#a855f7",
  "#d946ef",
  "#14b8a6",
];

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadSummary() {
      try {
        const data = await getAnalyticsSummary();
        setSummary(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }

    loadSummary();
  }, []);

  if (isLoading) {
  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1250,
        margin: "0 auto",
      }}
    >
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
          📊
        </div>

        <h2 style={{ marginBottom: "0.5rem" }}>
          Loading Dashboard
        </h2>

        <p
          style={{
            margin: 0,
            opacity: 0.7,
          }}
        >
          Loading your financial summary and spending insights...
        </p>
      </div>
    </div>
  );
}

  if (error) {
    return (
      <div
        style={{
          padding: "3rem",
          fontFamily: "sans-serif",
          maxWidth: 1200,
          margin: "0 auto",
        }}
      >
        <h1>Financial Dashboard</h1>
        <p style={{ color: "#ef4444" }}>Error: {error}</p>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  if (
    summary.total_income === 0 &&
    summary.total_expense === 0 &&
    summary.total_transfer_out === 0
  ) {
    return (
      <div
        style={{
          padding: "3rem 2rem",
          fontFamily: "sans-serif",
          maxWidth: 1200,
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <h1 style={{ marginBottom: "1rem" }}>
          Financial Dashboard
        </h1>

        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "2rem",
          }}
        >
          <h3>No transaction data available.</h3>
          <p>
            Upload a transactions CSV to see your financial dashboard.
          </p>
        </div>
      </div>
    );
  }

  const flowData = [
    {
      name: "Income",
      amount: summary.total_income,
    },
    {
      name: "Expense",
      amount: summary.total_expense,
    },
    {
      name: "Transfer-Out",
      amount: summary.total_transfer_out,
    },
  ];

  const totalCategoryExpense = summary.category_breakdown.reduce(
    (total, row) => total + Number(row.total_amount),
    0
  );

  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1250,
        margin: "0 auto",
      }}
    >
      {/* PAGE HEADER */}
      <div
        style={{
          marginBottom: "2rem",
        }}
      >
        <h1
          style={{
            margin: 0,
            marginBottom: "0.5rem",
            fontSize: "2.2rem",
            lineHeight: 1.2,
          }}
        >
          Financial Dashboard
        </h1>

        <p
          style={{
            margin: 0,
            opacity: 0.75,
          }}
        >
          Overview of your income, expenses, savings and spending behaviour.
        </p>
      </div>

      {/* STAT CARDS */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1rem",
          marginBottom: "2.5rem",
        }}
      >
        <StatCard
          label="Total Income"
          value={formatCurrency(summary.total_income)}
          color="#10b981"
        />

        <StatCard
          label="Total Expense"
          value={formatCurrency(summary.total_expense)}
          color="#ef4444"
        />

        <StatCard
          label="Transfer-Out"
          value={formatCurrency(summary.total_transfer_out)}
          color="#f59e0b"
        />

        <StatCard
          label="Net Savings"
          value={formatCurrency(summary.net_savings)}
          color={
            summary.net_savings >= 0
              ? "#10b981"
              : "#ef4444"
          }
        />
      </div>

      {/* INCOME / EXPENSE / TRANSFER CHART */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: "1.5rem",
          }}
        >
          Income vs Expense vs Transfer-Out
        </h2>

        <div
          style={{
            width: "100%",
            height: 350,
          }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={flowData}
              margin={{
                top: 10,
                right: 20,
                left: 10,
                bottom: 10,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="name" />

              <YAxis />

              <Tooltip
                formatter={(value) =>
                  formatCurrency(value)
                }
              />

              <Bar
                dataKey="amount"
                fill="#4f46e5"
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* SPENDING BY CATEGORY */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
          marginBottom: "2.5rem",
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: "0.4rem",
          }}
        >
          Spending by Category
        </h2>

        <p
          style={{
            marginTop: 0,
            marginBottom: "1.5rem",
            opacity: 0.75,
          }}
        >
          Breakdown of your expenses across different categories.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(350px, 1.1fr) minmax(350px, 1fr)",
            gap: "2rem",
            alignItems: "center",
          }}
        >
          {/* PIE CHART */}
          <div
            style={{
              width: "100%",
              height: 430,
            }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={summary.category_breakdown}
                  dataKey="total_amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={160}
                  innerRadius={0}
                  paddingAngle={1}
                  label={false}
                  labelLine={false}
                >
                  {summary.category_breakdown.map(
                    (_, index) => (
                      <Cell
                        key={index}
                        fill={
                          PIE_COLORS[
                            index % PIE_COLORS.length
                          ]
                        }
                      />
                    )
                  )}
                </Pie>

                <Tooltip
                  formatter={(value, name) => [
                    formatCurrency(value),
                    name,
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* CATEGORY LEGEND / DETAILS */}
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: 10,
              overflow: "hidden",
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 110px 80px",
                gap: "0.5rem",
                padding: "0.8rem 1rem",
                borderBottom: "1px solid #ddd",
                fontWeight: "bold",
              }}
            >
              <span>Category</span>
              <span>Amount</span>
              <span>Share</span>
            </div>

            {/* Scrollable categories */}
            <div
              style={{
                maxHeight: 360,
                overflowY: "auto",
              }}
            >
              {summary.category_breakdown.map(
                (row, index) => {
                  const percentage =
                    totalCategoryExpense > 0
                      ? (Number(row.total_amount) /
                          totalCategoryExpense) *
                        100
                      : 0;

                  return (
                    <div
                      key={row.category}
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "1fr 110px 80px",
                        gap: "0.5rem",
                        padding: "0.7rem 1rem",
                        borderBottom:
                          "1px solid #eee",
                        alignItems: "center",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.6rem",
                          minWidth: 0,
                        }}
                      >
                        <span
                          style={{
                            width: 12,
                            height: 12,
                            borderRadius: "50%",
                            backgroundColor:
                              PIE_COLORS[
                                index %
                                  PIE_COLORS.length
                              ],
                            flexShrink: 0,
                          }}
                        />

                        <span
                          style={{
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                          title={row.category}
                        >
                          {row.category}
                        </span>
                      </div>

                      <span>
                        {formatCurrency(
                          row.total_amount
                        )}
                      </span>

                      <span>
                        {percentage.toFixed(1)}%
                      </span>
                    </div>
                  );
                }
              )}
            </div>

            {/* Total */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 110px 80px",
                gap: "0.5rem",
                padding: "0.9rem 1rem",
                fontWeight: "bold",
                borderTop: "1px solid #ddd",
              }}
            >
              <span>Total</span>

              <span>
                {formatCurrency(totalCategoryExpense)}
              </span>

              <span>100%</span>
            </div>
          </div>
        </div>
      </div>

      {/* CATEGORY BREAKDOWN TABLE */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
          marginBottom: "2.5rem",
          overflowX: "auto",
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: "1rem",
          }}
        >
          Category Breakdown
        </h2>

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
                borderBottom: "2px solid #ddd",
              }}
            >
              <th style={{ padding: "0.75rem" }}>
                Category
              </th>

              <th style={{ padding: "0.75rem" }}>
                Total Amount
              </th>

              <th style={{ padding: "0.75rem" }}>
                Transactions
              </th>
            </tr>
          </thead>

          <tbody>
            {summary.category_breakdown.map((row) => (
              <tr
                key={row.category}
                style={{
                  borderBottom: "1px solid #eee",
                }}
              >
                <td style={{ padding: "0.75rem" }}>
                  {row.category}
                </td>

                <td style={{ padding: "0.75rem" }}>
                  {formatCurrency(row.total_amount)}
                </td>

                <td style={{ padding: "0.75rem" }}>
                  {row.transaction_count}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MONTHLY EXPENSE TREND */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "1.5rem",
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: "1rem",
          }}
        >
          Monthly Expense Trend
        </h2>

        <div
          style={{
            width: "100%",
            height: 350,
          }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={summary.monthly_trend}
              margin={{
                top: 10,
                right: 20,
                left: 10,
                bottom: 10,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="month" />

              <YAxis />

              <Tooltip
                formatter={(value) =>
                  formatCurrency(value)
                }
              />

              <Legend />

              <Line
                type="monotone"
                dataKey="total_expense"
                stroke="#4f46e5"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;