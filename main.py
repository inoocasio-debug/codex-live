from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random

app = FastAPI(title="Code X Live")

# --------------------------
# Monta la carpeta raíz para servir archivos web
# --------------------------
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# --------------------------
# Health check
# --------------------------
@app.get("/health")
def root():
    return {"status": "ok"}

# --------------------------
# Modelo de señal
# --------------------------
class Signal(BaseModel):
    market: str
    momentum: int = None
    size: float = 1.0

# --------------------------
# Variables globales para simular presión del mercado
# --------------------------
MARKET_PRESSURE = {}

# --------------------------
# Función simulada de Order Book dinámico
# --------------------------
def get_dynamic_orderbook(market_id: str):
    global MARKET_PRESSURE
    if market_id not in MARKET_PRESSURE:
        MARKET_PRESSURE[market_id] = random.uniform(0.4, 0.6)
    delta = random.uniform(-0.05, 0.05)
    MARKET_PRESSURE[market_id] = min(max(MARKET_PRESSURE[market_id] + delta, 0.0), 1.0)
    base_price = 50
    bids = [{"price": round(base_price - random.uniform(0, 5), 2), "size": random.randint(1, 5)} for _ in range(5)]
    asks = [{"price": round(base_price + random.uniform(0, 5), 2), "size": random.randint(1, 5)} for _ in range(5)]
    return {"bids": bids, "asks": asks, "pressure": MARKET_PRESSURE[market_id]}

# --------------------------
# Calcula momentum dinámico
# --------------------------
def calculate_momentum(orderbook):
    bid_total = sum([b['price']*b['size'] for b in orderbook['bids']])
    ask_total = sum([a['price']*a['size'] for a in orderbook['asks']])
    if bid_total + ask_total == 0:
        return 50
    momentum = int((bid_total / (bid_total + ask_total)) * 100)
    momentum = int(momentum * (1 + (orderbook['pressure'] - 0.5)))
    return max(0, min(momentum, 100))

# --------------------------
# Endpoint de Orderbook dinámico
# --------------------------
@app.get("/orderbook/{market_id}")
def orderbook_endpoint(market_id: str):
    ob = get_dynamic_orderbook(market_id)
    momentum = calculate_momentum(ob)
    return {"market_id": market_id, "orderbook": ob, "momentum": momentum}

# --------------------------
# Endpoint de señal agresiva
# --------------------------
@app.post("/signal")
def generate_signal(signal: Signal):
    ob = get_dynamic_orderbook(signal.market)
    momentum = calculate_momentum(ob)
    if momentum > 65:
        action = "BUY"
        size = round(signal.size * (momentum / 100), 2)
    elif momentum < 35:
        action = "SELL"
        size = round(signal.size * ((100 - momentum) / 100), 2)
    else:
        action = "HOLD"
        size = signal.size
    return {
        "market": signal.market,
        "momentum": momentum,
        "recommended_action": action,
        "size": size,
        "orderbook": ob
    }
