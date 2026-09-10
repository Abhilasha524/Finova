# Finova

A personal finance application that goes past basic expense tracking:
transaction analytics, ML-based categorization, anomaly detection, expense
forecasting, behavioural clustering, a grounded chatbot, and savings goal
tracking — built as an MCA (AI & Data Science) project, with an emphasis on
honest evaluation over inflated claims.

Every model in this project was chosen after comparing at least one
alternative and evaluating both on held-out data. Where a model performs
poorly on part of the data, that's documented below rather than hidden.

## Features

**Authentication** — registration, bcrypt password hashing, JWT-based auth,
and protected financial APIs.

**Transactions** — CSV upload with date-format normalization, duplicate
detection based on transaction content, income/expense/transfer-out
classification, and transaction history.

**Analytics Dashboard** — income, expense, transfer-out, and net savings
totals; category breakdown; and monthly spending trends.

**Categorization** — TF-IDF + Logistic Regression, compared against Naive
Bayes on the same held-out data. Logistic Regression won with approximately
77% accuracy and 79% weighted F1. Rare categories with too few examples to
learn reliably were excluded rather than reported with misleading metrics —
documented as a real limitation rather than glossed over.

**Anomaly Detection** — Isolation Forest, scoped per user and per category,
with a human-readable reason attached to every flagged transaction rather
than only a black-box anomaly score. No ground-truth labels exist for real
anomalies in this dataset, so there is no accuracy number here by design —
reporting one would be misleading.

**Forecasting** — Holt-Winters was evaluated against a simple Naive Last
Value baseline. After evaluating the available historical data, the Naive
Last Value approach performed better and was selected. The resulting
forecast is intentionally flat month-to-month — a correct reflection of
what the available data supports rather than a fabricated trend.

**Behavioural Clustering** — K-Means applied to spending patterns over time,
using features such as spending volatility, category diversity, weekend
spending ratio, and recurring-expense ratio. Because the available dataset
represents a single household, clustering is performed across time periods
rather than across multiple users. This is a deliberate scope adaptation;
genuine cross-user persona clustering would require a multi-user dataset.

**Savings Goals** — target amount and date, live progress tracking, remaining
amount calculation, and required monthly saving rate calculated from real
transaction history.

**Chatbot** — answers questions about the user's own financial data,
including income, expenses, net savings, transfer-out amounts, spending
categories, transaction count, financial persona, and savings goals. The
chatbot queries stored financial data directly rather than generating
financial figures from a language model, keeping responses grounded in the
actual database.

**Personalized Recommendations** — generated from actual spending patterns,
including high-spending categories, weekend spending behaviour, recurring
expenses, and a suggested savings target.

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, Pydantic, JWT
authentication, Passlib/bcrypt

**ML/Data:** Pandas, NumPy, scikit-learn, statsmodels, joblib

**Frontend:** React, Vite, JavaScript, Recharts

## Project Structure

```text
Finova/
│
├── backend/
│   ├── app/
│   │   ├── routers/            # API endpoints
│   │   │                       # auth, transactions, analytics,
│   │   │                       # anomalies, forecast, goals,
│   │   │                       # persona, chat, recommendations
│   │   ├── services/           # CSV ingestion and analytics
│   │   ├── ml/                 # ML training and model artifacts
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   └── main.py
│   │
│   ├── data/
│   ├── requirements.txt
│   ├── .env                    # local configuration; not committed
│   └── .gitignore
│
└── frontend/
    └── src/
        ├── api/                # backend API integration
        ├── components/         # reusable UI components
        ├── context/            # authentication state
        ├── pages/              # application pages
        └── utils/              # utility functions
