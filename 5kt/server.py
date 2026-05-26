from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import httpx
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIXED_RATES: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "RUB": 90.50,
    "GBP": 0.79,
    "JPY": 150.25,
    "CNY": 7.24,
}

SUPPORTED_CURRENCIES = list(FIXED_RATES.keys())

async def get_live_rates() -> Dict[str, float]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://open.er-api.com/v6/latest/USD",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                return {curr: rates.get(curr) for curr in SUPPORTED_CURRENCIES if curr in rates}
    except Exception:
        pass
    return FIXED_RATES

@app.get("/currencies")
async def get_supported_currencies():
    return {"currencies": SUPPORTED_CURRENCIES}

@app.get("/rates")
async def get_rates():
    rates = await get_live_rates()
    return {"base": "USD", "rates": rates}

@app.get("/convert")
async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float
):
    if from_currency.upper() not in SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемая валюта: {from_currency}. Доступные валюты: {', '.join(SUPPORTED_CURRENCIES)}"
        )
    
    if to_currency.upper() not in SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемая валюта: {to_currency}. Доступные валюты: {', '.join(SUPPORTED_CURRENCIES)}"
        )
    
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Сумма должна быть положительным числом больше нуля"
        )
    
    rates = await get_live_rates()
    
    from_rate = rates.get(from_currency.upper())
    to_rate = rates.get(to_currency.upper())
    
    if from_rate is None or to_rate is None:
        raise HTTPException(
            status_code=500,
            detail="Ошибка получения курсов валют"
        )
    
    converted_amount = amount * (to_rate / from_rate)
    
    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount,
        "converted_amount": round(converted_amount, 2),
        "rate": round(to_rate / from_rate, 4),
        "timestamp": "Актуальный курс" if rates != FIXED_RATES else "Фиксированный курс"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)