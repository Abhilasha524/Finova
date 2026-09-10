import { useEffect, useState } from "react";
import { createGoal, deleteGoal, getGoals } from "../api/goals";
import { formatCurrency } from "../utils/format";

function Goals() {
  const [goals, setGoals] = useState([]);
  const [title, setTitle] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadGoals() {
    try {
      setError(null);
      const data = await getGoals();
      setGoals(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadGoals();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!title || !targetAmount || !targetDate) {
      return;
    }

    try {
      await createGoal({
        title,
        target_amount: Number(targetAmount),
        target_date: targetDate,
      });

      setTitle("");
      setTargetAmount("");
      setTargetDate("");

      await loadGoals();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(goalId) {
    try {
      await deleteGoal(goalId);
      await loadGoals();
    } catch (err) {
      setError(err.message);
    }
  }

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
      <div style={{ marginBottom: "2rem" }}>
        <h1
          style={{
            margin: 0,
            marginBottom: "0.5rem",
            fontSize: "2.2rem",
            lineHeight: 1.2,
          }}
        >
          Financial Goals
        </h1>

        <p
          style={{
            margin: 0,
            opacity: 0.75,
          }}
        >
          Set savings goals and track your progress over time.
        </p>
      </div>

      {/* CREATE GOAL */}
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
          Create a New Goal
        </h2>

        <p
          style={{
            marginTop: 0,
            marginBottom: "1.5rem",
            opacity: 0.7,
          }}
        >
          Define a target amount and deadline for your financial goal.
        </p>

        <form
          onSubmit={handleSubmit}
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem",
            alignItems: "end",
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
              Goal Title
            </label>

            <input
              type="text"
              placeholder="e.g. Emergency Fund"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "0.7rem",
                borderRadius: 8,
                border: "1px solid #bbb",
              }}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                marginBottom: "0.4rem",
                fontWeight: "600",
              }}
            >
              Target Amount
            </label>

            <input
              type="number"
              placeholder="₹ 10,000"
              value={targetAmount}
              onChange={(e) => setTargetAmount(e.target.value)}
              min="1"
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "0.7rem",
                borderRadius: 8,
                border: "1px solid #bbb",
              }}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                marginBottom: "0.4rem",
                fontWeight: "600",
              }}
            >
              Target Date
            </label>

            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "0.7rem",
                borderRadius: 8,
                border: "1px solid #bbb",
              }}
            />
          </div>

          <button
            type="submit"
            style={{
              padding: "0.7rem 1.2rem",
              borderRadius: 8,
              border: "none",
              cursor: "pointer",
              fontWeight: "600",
              backgroundColor: "#4f46e5",
              color: "white",
            }}
          >
            Add Goal
          </button>
        </form>
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
          <h3 style={{ marginBottom: "0.5rem" }}>
            Loading financial goals...
          </h3>

          <p style={{ margin: 0, opacity: 0.7 }}>
            Please wait while your goals are loaded.
          </p>
        </div>
      )}

      {/* EMPTY STATE */}
      {!loading && !error && goals.length === 0 && (
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
            🎯
          </div>

          <h2 style={{ marginBottom: "0.75rem" }}>
            No financial goals yet
          </h2>

          <p
            style={{
              maxWidth: 550,
              margin: "0 auto",
              lineHeight: 1.6,
              opacity: 0.75,
            }}
          >
            Create your first savings goal above to start tracking how
            close you are to achieving it.
          </p>
        </div>
      )}

      {/* GOALS */}
      {!loading && goals.length > 0 && (
        <>
          <div
            style={{
              marginBottom: "1rem",
            }}
          >
            <h2 style={{ margin: 0 }}>
              Your Goals
            </h2>

            <p
              style={{
                marginTop: "0.4rem",
                opacity: 0.7,
              }}
            >
              {goals.length}{" "}
              {goals.length === 1 ? "goal" : "goals"} currently being tracked.
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "1.5rem",
            }}
          >
            {goals.map((goal) => {
              const progress = Math.min(
                100,
                Math.max(0, Number(goal.progress_percent))
              );

              return (
                <div
                  key={goal.id}
                  style={{
                    border: "1px solid #ddd",
                    borderRadius: 12,
                    padding: "1.5rem",
                    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.06)",
                  }}
                >
                  {/* GOAL TITLE */}
                  <h2
                    style={{
                      marginTop: 0,
                      marginBottom: "1.2rem",
                    }}
                  >
                    {goal.title}
                  </h2>

                  {/* TARGET INFORMATION */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "1rem",
                      marginBottom: "1.5rem",
                    }}
                  >
                    <div>
                      <small style={{ opacity: 0.7 }}>
                        Target Amount
                      </small>

                      <div
                        style={{
                          fontSize: "1.2rem",
                          fontWeight: "600",
                          marginTop: "0.2rem",
                        }}
                      >
                        {formatCurrency(goal.target_amount)}
                      </div>
                    </div>

                    <div>
                      <small style={{ opacity: 0.7 }}>
                        Target Date
                      </small>

                      <div
                        style={{
                          fontSize: "1.05rem",
                          fontWeight: "600",
                          marginTop: "0.2rem",
                        }}
                      >
                        {goal.target_date}
                      </div>
                    </div>
                  </div>

                  {/* PROGRESS */}
                  <div style={{ marginBottom: "1.5rem" }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginBottom: "0.5rem",
                      }}
                    >
                      <strong>Progress</strong>

                      <strong>
                        {progress.toFixed(1)}%
                      </strong>
                    </div>

                    <div
                      style={{
                        width: "100%",
                        height: 12,
                        backgroundColor: "#e5e7eb",
                        borderRadius: 999,
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${progress}%`,
                          height: "100%",
                          backgroundColor: "#4f46e5",
                          borderRadius: 999,
                          transition: "width 0.3s ease",
                        }}
                      />
                    </div>
                  </div>

                  {/* GOAL STATISTICS */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "0.8rem",
                      marginBottom: "1.5rem",
                    }}
                  >
                    <div
                      style={{
                        padding: "0.9rem",
                        borderRadius: 8,
                        border: "1px solid #ddd",
                      }}
                    >
                      <small style={{ opacity: 0.7 }}>
                        Current Savings
                      </small>

                      <div
                        style={{
                          fontWeight: "600",
                          marginTop: "0.25rem",
                        }}
                      >
                        {formatCurrency(goal.current_savings)}
                      </div>
                    </div>

                    <div
                      style={{
                        padding: "0.9rem",
                        borderRadius: 8,
                        border: "1px solid #ddd",
                      }}
                    >
                      <small style={{ opacity: 0.7 }}>
                        Remaining
                      </small>

                      <div
                        style={{
                          fontWeight: "600",
                          marginTop: "0.25rem",
                        }}
                      >
                        {formatCurrency(goal.remaining_amount)}
                      </div>
                    </div>

                    <div
                      style={{
                        padding: "0.9rem",
                        borderRadius: 8,
                        border: "1px solid #ddd",
                        gridColumn: "1 / -1",
                      }}
                    >
                      <small style={{ opacity: 0.7 }}>
                        Required Monthly Saving
                      </small>

                      <div
                        style={{
                          fontSize: "1.1rem",
                          fontWeight: "600",
                          marginTop: "0.25rem",
                        }}
                      >
                        {formatCurrency(goal.required_monthly_saving)}
                      </div>
                    </div>
                  </div>

                  {/* DELETE */}
                  <button
                    onClick={() => handleDelete(goal.id)}
                    style={{
                      width: "100%",
                      padding: "0.7rem",
                      borderRadius: 8,
                      border: "1px solid #ef4444",
                      backgroundColor: "transparent",
                      color: "#ef4444",
                      cursor: "pointer",
                      fontWeight: "600",
                    }}
                  >
                    Delete Goal
                  </button>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export default Goals;