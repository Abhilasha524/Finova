import streamlit as st

# ============================================================
# FINOVA
# ============================================================

st.set_page_config(
    page_title="Finova",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background-color: #f7f8f6;
}

/* Main content text */
.main p,
.main label,
.main span {
    color: #324635;
}

h1, h2, h3, h4, h5, h6 {
    color: #324635 !important;
}

p {
    color: #68736b;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #324635;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Finova title */
.finova-title {
    font-size: 46px;
    font-weight: 700;
    color: #324635;
    margin-bottom: 0;
}

.finova-subtitle {
    font-size: 17px;
    color: #68736b !important;
    margin-top: 0;
}

/* Feature cards */
.feature-box {
    background-color: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e1e6e1;
    min-height: 130px;
}

.feature-box h3 {
    color: #324635 !important;
}

.feature-box p {
    color: #68736b !important;
}

/* Metrics */
[data-testid="stMetricLabel"] {
    color: #68736b !important;
}

[data-testid="stMetricValue"] {
    color: #324635 !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
<div style="font-size:32px;font-weight:700;">
Finova
</div>

<div style="font-size:13px;margin-top:5px;">
A modern approach to managing your finances.
</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Transactions",
            "Anomalies",
            "Forecast",
            "Spending Persona",
            "Savings Goals",
            "Recommendations",
            "AI Chat",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("Finova")
    st.caption("Personal Finance Intelligence")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="finova-title">Finova</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="finova-subtitle">'
    "A modern approach to managing your finances."
    "</div>",
    unsafe_allow_html=True,
)

# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown("## Welcome to Finova")

    st.write(
        "Your personal finance intelligence platform. "
        "Finova transforms transaction data into meaningful "
        "insights, predictions and personalized recommendations."
    )

    st.divider()

    st.subheader("Financial Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Income", "₹0")

    with col2:
        st.metric("Total Expenses", "₹0")

    with col3:
        st.metric("Net Savings", "₹0")

    with col4:
        st.metric("Transactions", "0")

    st.divider()

    st.subheader("Finova Intelligence")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
<div class="feature-box">
<h3>ML Categorization</h3>
<p>Automatically classify transactions using machine learning.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
<div class="feature-box">
<h3>Anomaly Detection</h3>
<p>Detect unusual transactions and spending patterns.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
<div class="feature-box">
<h3>Expense Forecast</h3>
<p>Estimate future expenses using historical spending behaviour.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
<div class="feature-box">
<h3>Spending Persona</h3>
<p>Understand your financial behaviour using K-Means clustering.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
<div class="feature-box">
<h3>Smart Recommendations</h3>
<p>Get recommendations based on your actual spending behaviour.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
<div class="feature-box">
<h3>Finova AI</h3>
<p>Ask questions about your financial data and get grounded answers.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.write("")

    st.info(
        "Upload your transaction statement from the Transactions section to get started."
    )

# ============================================================
# TRANSACTIONS
# ============================================================

elif page == "Transactions":

    st.header("Transactions")

    st.write(
        "Upload your transaction statement and explore your financial activity."
    )

    uploaded_file = st.file_uploader(
        "Upload Transaction CSV",
        type=["csv"],
    )

    if uploaded_file:
        st.success(
            f"{uploaded_file.name} uploaded successfully."
        )

        st.info(
            "Finova's existing transaction processing will be connected here."
        )

# ============================================================
# ANOMALIES
# ============================================================

elif page == "Anomalies":

    st.header("Anomaly Detection")

    st.write(
        "Finova identifies unusual transactions and spending behaviour."
    )

    st.info(
        "Existing Finova anomaly detection will be connected here."
    )

# ============================================================
# FORECAST
# ============================================================

elif page == "Forecast":

    st.header("Expense Forecast")

    st.write(
        "Forecast your upcoming expenses using historical spending data."
    )

    st.info(
        "Existing Finova forecasting will be connected here."
    )

# ============================================================
# PERSONA
# ============================================================

elif page == "Spending Persona":

    st.header("Spending Persona")

    st.write(
        "Discover your spending behaviour using K-Means clustering."
    )

    st.info(
        "Existing Finova persona analysis will be connected here."
    )

# ============================================================
# GOALS
# ============================================================

elif page == "Savings Goals":

    st.header("Savings Goals")

    st.write(
        "Set financial targets and track your progress."
    )

    st.info(
        "Existing Finova goals functionality will be connected here."
    )

# ============================================================
# RECOMMENDATIONS
# ============================================================

elif page == "Recommendations":

    st.header("Personalized Recommendations")

    st.write(
        "Get recommendations based on your actual spending behaviour."
    )

    st.info(
        "Existing Finova recommendation engine will be connected here."
    )

# ============================================================
# AI CHAT
# ============================================================

elif page == "AI Chat":

    st.header("Finova AI")

    st.write(
        "Ask questions about your financial data."
    )

    question = st.text_input(
        "Ask Finova something..."
    )

    if question:
        st.info(
            "Existing Finova financial-data-grounded chatbot will be connected here."
        )