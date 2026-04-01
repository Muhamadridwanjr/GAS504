from pydantic import BaseModel
from typing import Optional, List, Any

class AgentPrediction(BaseModel):
    model: str
    yes: float
    no: float
    confidence: float
    reasoning: str

class ConsensusPrediction(BaseModel):
    yes: float
    no: float
    action: str  # BUY YES / BUY NO / NO TRADE
    confidence: float
    agents: List[AgentPrediction]
    majority_yes: int
    majority_no: int

class MarketCard(BaseModel):
    event_id: str
    question: str
    category: str
    yes_price: float  # from CLOB 0-1
    no_price: float
    volume: float
    end_date: Optional[str]
    active: bool
    prediction: Optional[ConsensusPrediction] = None

class PredictRequest(BaseModel):
    event_id: str
    question: str
    category: str
    yes_price: float
    no_price: float
    pair: Optional[str] = None  # mapped forex/crypto pair
    timeframe: Optional[str] = "H4"
    models: Optional[List[str]] = ["claude", "gpt", "gemini", "grok"]

class AnalyticsEntry(BaseModel):
    event_id: str
    question: str
    category: str
    predicted_action: str
    actual_outcome: Optional[str]
    correct: Optional[bool]
    confidence: float
    timestamp: str
