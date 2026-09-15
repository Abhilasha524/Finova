"""
Finova - Standalone Streamlit Dashboard

Connects DIRECTLY to the Finova Postgres database (read-only) - no
dependency on the FastAPI backend being online, and no dependency on the
saved .joblib model files, so this can be deployed independently on
Streamlit Community Cloud.

WHY forecasting and persona are recomputed here instead of loading the
saved backend models: the backend's forecaster is a pickled Python object
(NaiveLastValueForecaster) whose class definition lives in the backend
codebase - unpickling it here would require bundling backend source files
into this separate app, which is exactly the kind of brittle coupling a
"standalone" app should avoid. Since the winning forecasting approach is
just "next month = last known month," it's trivial and safe to recompute
directly from the data instead.
"""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Finova Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------
# DATABASE_URL comes from .streamlit/secrets.toml locally, or from the
# "Secrets" panel in Streamlit Community Cloud when deployed - never
# hardcoded, and never the same file that gets committed to git.
@st.cache_resource
def get_engine():
    return create_engine(st.secrets["DATABASE_URL"])


engine = get_engine()

MONEY_TRANSFER_CATEGORY = "Money Transfer"  # excluded from "spending" framing - see note below


@st.cache_data(ttl=300)
def load_users():
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT id, email FROM users ORDER BY email"), conn)


@st.cache_data(ttl=300)
def load_transactions(user_id: str):
    query = text("""
        SELECT t.id, t.txn_date, t.description, t.amount, t.txn_type,
               t.is_recurring, t.payment_mode, c.name AS category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = :user_id
        ORDER BY t.txn_date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"user_id": user_id})
    df["txn_date"] = pd.to_datetime(df["txn_date"])
    return df


@st.cache_data(ttl=300)
def load_anomalies(user_id: str):
    query = text("""
        SELECT t.txn_date, t.description, t.amount, c.name AS category,
               a.reason, a.anomaly_score
        FROM anomaly_flags a
        JOIN transactions t ON a.transaction_id = t.id
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = :user_id
        ORDER BY a.anomaly_score DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"user_id": user_id})
    return df


def format_inr(amount) -> str:
    return f"\u20b9{amount:,.0f}"


# ---------------------------------------------------------------------------
# Sidebar - user selection (read-only demo, no password required)
# ---------------------------------------------------------------------------
st.sidebar.title("Finova")
st.sidebar.caption("Read-only analytics view - direct database connection")

users_df = load_users()
if users_df.empty:
    st.error("No registered users found in the database.")
    st.stop()

selected_email = st.sidebar.selectbox("Viewing data for", users_df["email"])
user_id = users_df.loc[users_df["email"] == selected_email, "id"].iloc[0]

section = st.sidebar.radio(
    "Section", ["Analytics", "Anomalies", "Forecast", "Persona"]
)

df = load_transactions(user_id)

if df.empty:
    st.warning("This user has no transactions yet.")
    st.stop()

expense_df = df[df["txn_type"] == "Expense"]

# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
if section == "Analytics":
    st.title("Analytics Overview")

    total_income = df.loc[df["txn_type"] == "Income", "amount"].sum()
    total_expense = expense_df["amount"].sum()
    total_transfer_out = df.loc[df["txn_type"] == "Transfer-Out", "amount"].sum()
    net_savings = total_income - total_expense - total_transfer_out

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", format_inr(total_income))
    col2.metric("Total Expense", format_inr(total_expense))
    col3.metric("Transfer-Out", format_inr(total_transfer_out))
    col4.metric("Net Savings", format_inr(net_savings))

    st.divider()

    category_totals = (
        expense_df.groupby("category")["amount"]
        .agg(["sum", "count"])
        .reset_index()
        .sort_values("sum", ascending=False)
        .rename(columns={"sum": "Total Amount", "count": "Transactions", "category": "Category"})
    )

    # Honest framing note: Money Transfer is included in the "Expense" total
    # by the source data's own labeling, but it represents money sent to
    # another person, not discretionary spending - it's flagged here rather
    # than presented as an ordinary spending category to cut back on.
    if MONEY_TRANSFER_CATEGORY in category_totals["Category"].values:
        st.caption(
            f"Note: '{MONEY_TRANSFER_CATEGORY}' represents money sent to other people, "
            "not discretionary spending - shown for completeness, not as a category to reduce."
        )

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Category Breakdown")
        st.dataframe(category_totals, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Share by Category")
        st.bar_chart(category_totals.set_index("Category")["Total Amount"])

    st.subheader("Monthly Expense Trend")
    monthly = expense_df.copy()
    monthly["month"] = monthly["txn_date"].dt.to_period("M").astype(str)
    monthly_totals = monthly.groupby("month")["amount"].sum()
    st.line_chart(monthly_totals)

# ---------------------------------------------------------------------------
# Anomalies
# ---------------------------------------------------------------------------
elif section == "Anomalies":
    st.title("Anomaly Detection")
    st.caption("Reads previously-detected anomalies - does not recompute Isolation Forest here.")

    anomalies_df = load_anomalies(user_id)

    if anomalies_df.empty:
        st.info(
            "No anomalies found for this user yet. Anomaly detection runs from the "
            "main Finova app (POST /anomalies/detect) - this dashboard only displays "
            "results already saved to the database."
        )
    else:
        st.metric("Anomalies Detected", len(anomalies_df))
        st.dataframe(
            anomalies_df.rename(columns={
                "txn_date": "Date", "description": "Description", "amount": "Amount",
                "category": "Category", "reason": "Reason", "anomaly_score": "Score",
            }),
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------
elif section == "Forecast":
    st.title("Expense Forecast")
    st.caption(
        "Uses Naive Last Value - the approach that outperformed Holt-Winters on this "
        "dataset (see project documentation). Recomputed here directly from the data, "
        "not loaded from a saved model file, to keep this app fully standalone."
    )

    # Exclude Money Transfer from the forecasting series - same deliberate
    # scope decision made in the main backend (see forecast_data.py):
    # lumpy one-off transfers would corrupt trend estimation.
    forecast_input = expense_df[expense_df["category"] != MONEY_TRANSFER_CATEGORY].copy()
    forecast_input["month"] = forecast_input["txn_date"].dt.to_period("M").dt.to_timestamp()
    monthly_series = forecast_input.groupby("month")["amount"].sum().sort_index()

    if len(monthly_series) == 0:
        st.warning("Not enough data to forecast.")
        st.stop()

    # Drop a likely-partial trailing month (same heuristic as the backend):
    # if the most recent transaction falls well before month-end, that
    # month's data collection probably isn't complete.
    last_txn_date = forecast_input["txn_date"].max()
    if last_txn_date.day < 25 and len(monthly_series) > 1:
        monthly_series = monthly_series.iloc[:-1]
        st.caption(
            f"Excluded {last_txn_date.strftime('%Y-%m')} as a likely partial month "
            f"(last transaction on day {last_txn_date.day})."
        )

    months_ahead = st.slider("Months to forecast", 1, 12, 3)
    last_value = float(monthly_series.iloc[-1])

    future_months = pd.date_range(
        start=monthly_series.index[-1] + pd.DateOffset(months=1), periods=months_ahead, freq="MS"
    )
    forecast_df = pd.DataFrame(
        {"predicted_expense": [last_value] * months_ahead}, index=future_months
    )

    st.caption(
        "Every predicted month shows the same value by design - this is the honest "
        "output of the model that actually won on held-out evaluation, not a bug."
    )
    st.bar_chart(forecast_df["predicted_expense"])
    st.dataframe(
        forecast_df.reset_index().rename(
            columns={"index": "Month", "predicted_expense": "Predicted Expense"}
        ),
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------
elif section == "Persona":
    st.title("Spending Persona")
    st.caption(
        "K-Means applied to this user's OWN spending across different months - not "
        "across multiple users. A genuine cross-user persona would need a multi-user "
        "dataset this project doesn't have; this is a deliberate scope adaptation."
    )

    monthly_df = expense_df.copy()
    monthly_df["month"] = monthly_df["txn_date"].dt.to_period("M")

    grouped = monthly_df.groupby("month")
    features = grouped.apply(lambda g: pd.Series({
        "total_expense": g["amount"].sum(),
        "category_diversity": g["category"].nunique(),
        "weekend_ratio": g.loc[g["txn_date"].dt.weekday >= 5, "amount"].sum() / g["amount"].sum()
        if g["amount"].sum() > 0 else 0,
        "recurring_ratio": g["is_recurring"].mean(),
    })).reset_index()

    if len(features) < 3:
        st.warning("Need at least 3 months of data for meaningful clustering.")
        st.stop()

    feature_cols = ["total_expense", "category_diversity", "weekend_ratio", "recurring_ratio"]
    X = features[feature_cols].fillna(0)
    X_normalized = (X - X.mean()) / X.std().replace(0, 1)

    n_clusters = min(3, len(features))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    features["cluster"] = kmeans.fit_predict(X_normalized)

    # Label clusters by relative spending volatility - simple, explainable,
    # not a black-box label
    cluster_volatility = features.groupby("cluster")["total_expense"].std().fillna(0)
    ranked = cluster_volatility.sort_values()
    labels = {}
    label_names = ["Stable Spender", "Balanced Spender", "High-Variance Spender"]
    for i, cluster_id in enumerate(ranked.index):
        labels[cluster_id] = label_names[min(i, len(label_names) - 1)]
    features["persona"] = features["cluster"].map(labels)

    latest_month = features.iloc[-1]
    st.subheader(f"Most Recent Month: {latest_month['persona']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Expense", format_inr(latest_month["total_expense"]))
    col2.metric("Category Diversity", int(latest_month["category_diversity"]))
    col3.metric("Weekend Spending Share", f"{latest_month['weekend_ratio']*100:.1f}%")
    col4.metric("Recurring Share", f"{latest_month['recurring_ratio']*100:.1f}%")

    st.subheader("Persona History by Month")
    display_df = features[["month", "persona", "total_expense", "category_diversity"]].copy()
    display_df["month"] = display_df["month"].astype(str)
    st.dataframe(
        display_df.rename(columns={
            "month": "Month", "persona": "Persona",
            "total_expense": "Total Expense", "category_diversity": "Categories Used",
        }),
        use_container_width=True,
        hide_index=True,
    )
