import { useEffect, useState } from "react";
import { getPersona } from "../api/persona";

function Persona() {
  const [persona, setPersona] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPersona() {
      try {
        const data = await getPersona();
        setPersona(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadPersona();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          padding: "3rem",
          fontFamily: "sans-serif",
          textAlign: "center",
        }}
      >
        <h2>Analyzing financial behaviour...</h2>
        <p>Our model is analyzing your spending patterns.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          padding: "3rem 2rem",
          fontFamily: "sans-serif",
          maxWidth: 1000,
          margin: "0 auto",
        }}
      >
        <h1>AI Financial Persona</h1>

        <p style={{ color: "#ef4444" }}>
          Error: {error}
        </p>
      </div>
    );
  }

  if (!persona) {
    return null;
  }

  const weekendRatio =
    Number(persona.weekend_spending_ratio) * 100;

  const recurringRatio =
    Number(persona.recurring_expense_ratio) * 100;

  const volatility =
    Number(persona.spending_volatility);

  return (
    <div
      style={{
        padding: "2.5rem 2rem",
        fontFamily: "sans-serif",
        maxWidth: 1100,
        margin: "0 auto",
      }}
    >
      {/* HEADER */}
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
          AI Financial Persona
        </h1>

        <p
          style={{
            margin: 0,
            opacity: 0.75,
          }}
        >
          Understand your financial behaviour through machine learning.
        </p>
      </div>

      {/* PERSONA CARD */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: "2rem",
          marginBottom: "2rem",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: "3rem",
            marginBottom: "0.5rem",
          }}
        >
          
        </div>

        <p
          style={{
            margin: 0,
            fontSize: "0.9rem",
            opacity: 0.7,
            textTransform: "uppercase",
            letterSpacing: "1px",
          }}
        >
          Your Financial Persona
        </p>

        <h2
          style={{
            margin: "0.6rem 0 1rem",
            fontSize: "1.8rem",
          }}
        >
          {persona.persona}
        </h2>

        <p
          style={{
            maxWidth: 700,
            margin: "0 auto",
            lineHeight: 1.6,
            opacity: 0.8,
          }}
        >
          {persona.description}
        </p>
      </div>

      {/* BEHAVIOUR METRICS */}
      <h2
        style={{
          marginBottom: "1rem",
        }}
      >
        Behavioural Insights
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        {/* VOLATILITY */}
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "1.5rem",
          }}
        >
          <div
            style={{
              fontSize: "1.8rem",
              marginBottom: "0.7rem",
            }}
          >
            
          </div>

          <p
            style={{
              margin: 0,
              opacity: 0.7,
            }}
          >
            Spending Volatility
          </p>

          <h3
            style={{
              margin: "0.4rem 0",
              fontSize: "1.3rem",
            }}
          >
            ₹{volatility.toLocaleString("en-IN")}
          </h3>

          <small style={{ opacity: 0.65 }}>
            Variation in monthly spending
          </small>
        </div>

        {/* CATEGORY DIVERSITY */}
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "1.5rem",
          }}
        >
          <div
            style={{
              fontSize: "1.8rem",
              marginBottom: "0.7rem",
            }}
          >
            
          </div>

          <p
            style={{
              margin: 0,
              opacity: 0.7,
            }}
          >
            Category Diversity
          </p>

          <h3
            style={{
              margin: "0.4rem 0",
              fontSize: "1.3rem",
            }}
          >
            {persona.category_diversity}
          </h3>

          <small style={{ opacity: 0.65 }}>
            Expense categories used
          </small>
        </div>

        {/* WEEKEND SPENDING */}
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "1.5rem",
          }}
        >
          <div
            style={{
              fontSize: "1.8rem",
              marginBottom: "0.7rem",
            }}
          >
            
          </div>

          <p
            style={{
              margin: 0,
              opacity: 0.7,
            }}
          >
            Weekend Spending
          </p>

          <h3
            style={{
              margin: "0.4rem 0",
              fontSize: "1.3rem",
            }}
          >
            {weekendRatio.toFixed(1)}%
          </h3>

          <small style={{ opacity: 0.65 }}>
            Share of expenses spent on weekends
          </small>
        </div>

        {/* RECURRING EXPENSE */}
        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 12,
            padding: "1.5rem",
          }}
        >
          <div
            style={{
              fontSize: "1.8rem",
              marginBottom: "0.7rem",
            }}
          >
            
          </div>

          <p
            style={{
              margin: 0,
              opacity: 0.7,
            }}
          >
            Recurring Expenses
          </p>

          <h3
            style={{
              margin: "0.4rem 0",
              fontSize: "1.3rem",
            }}
          >
            {recurringRatio.toFixed(1)}%
          </h3>

          <small style={{ opacity: 0.65 }}>
            Share of expenses that are recurring
          </small>
        </div>
      </div>

      {/* HOW IT WORKS */}
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
            marginBottom: "0.8rem",
          }}
        >
          How your persona is determined
        </h2>

        <p
          style={{
            lineHeight: 1.6,
            marginBottom: "1rem",
            opacity: 0.8,
          }}
        >
          Expense transactions are analyzed across monthly
          spending behaviour. The system uses behavioural
          features such as spending amount, category diversity,
          weekend spending and recurring expenses to identify
          patterns.
        </p>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.7rem",
          }}
        >
          <span
            style={{
              border: "1px solid #ddd",
              borderRadius: 20,
              padding: "0.5rem 0.9rem",
            }}
          >
            Monthly Spending
          </span>

          <span
            style={{
              border: "1px solid #ddd",
              borderRadius: 20,
              padding: "0.5rem 0.9rem",
            }}
          >
            Category Diversity
          </span>

          <span
            style={{
              border: "1px solid #ddd",
              borderRadius: 20,
              padding: "0.5rem 0.9rem",
            }}
          >
            Weekend Spending
          </span>

          <span
            style={{
              border: "1px solid #ddd",
              borderRadius: 20,
              padding: "0.5rem 0.9rem",
            }}
          >
            Recurring Expenses
          </span>

          <span
            style={{
              border: "1px solid #ddd",
              borderRadius: 20,
              padding: "0.5rem 0.9rem",
            }}
          >
            K-Means Clustering
          </span>
        </div>
      </div>
    </div>
  );
}

export default Persona;