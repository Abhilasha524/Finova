# ExpenseMind AI

ExpenseMind AI is a personal finance management application that combines
transaction analytics, machine learning, forecasting, anomaly detection,
financial goals, behavioural analysis, chatbot assistance, and personalized
saving recommendations.

## Current Features

### Authentication
- User registration
- Secure bcrypt password hashing
- JWT-based authentication
- Protected financial APIs

### Transaction Management
- CSV transaction upload
- Automatic transaction categorization
- Duplicate transaction detection
- Transaction history
- Support for income, expenses, and transfer-out transactions

### Analytics Dashboard
- Total income
- Total expenses
- Total transfer-out
- Net savings
- Spending by category
- Monthly spending trends

### Machine Learning
- ML-based transaction categorization
- Logistic Regression classification
- Anomaly detection
- Spending behaviour analysis using K-Means clustering
- Financial persona generation
- Expense forecasting

### Financial Planning
- Savings goals
- Goal progress tracking
- Required monthly savings calculation
- Personalized saving recommendations

### AI Chatbot
The chatbot provides grounded responses based on the user's financial
data, including:
- Income
- Expenses
- Net savings
- Transfer-out amounts
- Spending categories
- Transaction count
- Financial persona
- Savings goals

It also supports basic conversational interactions such as greetings,
thanks, and general assistance.

## Technology Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT authentication
- Passlib / bcrypt

### Machine Learning & Data Processing
- Pandas
- NumPy
- Scikit-learn
- Statsmodels
- Joblib

### Frontend
- React
- Vite
- JavaScript
- Recharts

## Project Structure

```text
expensemind_backend_phase1/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   └── main.py
│   │
│   ├── data/
│   ├── requirements.txt
│   ├── .env
│   └── .gitignore
│
└── frontend/
    ├── src/
    │   ├── api/
    │   ├── components/
    │   ├── context/
    │   ├── pages/
    │   └── utils/
    └── ...