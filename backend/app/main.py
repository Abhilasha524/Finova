from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import analytics, anomalies, auth, categorize, forecast, transactions, goals, persona, chat, recommendations
# Creates tables if they don't exist yet. Fine for development;
# use Alembic migrations once the schema stabilizes.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ExpenseMind AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(goals.router)
app.include_router(recommendations.router)
app.include_router(persona.router)
app.include_router(chat.router)
app.include_router(categorize.router)
app.include_router(analytics.router)
app.include_router(anomalies.router)
app.include_router(forecast.router) 
@app.get("/health")
def health_check():
    return {"status": "ok"}
